#!/usr/bin/env python3
"""
🐳 Sandbox - Secure Test Execution Environment
Phase A: Docker-based isolated testing

Provides secure, isolated environments for running tests and code analysis.
"""

import docker
import subprocess
import tempfile
import json
import time
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class SandboxResult:
    """Result from sandbox execution"""
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    execution_time: float
    timeout: bool = False
    error: Optional[str] = None

@dataclass
class SandboxConfig:
    """Sandbox configuration"""
    image: str = "python:3.11-slim"
    timeout: int = 600
    memory_limit: str = "2g"
    cpu_limit: str = "2"
    network: str = "none"
    working_dir: str = "/workspace"

class Sandbox:
    """
    Secure sandbox for running tests and code analysis.
    
    Uses Docker containers with security restrictions to safely execute
    generated code and tests.
    """
    
    def __init__(self):
        self.docker_client = None
        self.docker_available = self._check_docker()
        
        # Predefined sandbox images
        self.images = {
            "python": "python:3.11-slim",
            "node": "node:18-slim",
            "ubuntu": "ubuntu:22.04"
        }
        
        logger.info(f"🐳 Sandbox initialized (Docker available: {self.docker_available})")
    
    def _check_docker(self) -> bool:
        """Check if Docker is available"""
        try:
            self.docker_client = docker.from_env()
            self.docker_client.ping()
            return True
        except Exception as e:
            logger.warning(f"🐳 Docker not available: {e}")
            return False
    
    async def run_command(
        self,
        command: str,
        project_path: str,
        config: SandboxConfig = None,
        env: Dict[str, str] = None
    ) -> SandboxResult:
        """
        Run a command in a secure sandbox
        
        Args:
            command: Command to execute
            project_path: Path to project directory to mount
            config: Sandbox configuration
            env: Environment variables
            
        Returns:
            SandboxResult with execution details
        """
        if config is None:
            config = SandboxConfig()
        
        if env is None:
            env = {}
        
        start_time = time.time()
        
        if self.docker_available:
            return await self._run_docker(command, project_path, config, env, start_time)
        else:
            return await self._run_local(command, project_path, config, env, start_time)
    
    async def _run_docker(
        self,
        command: str,
        project_path: str,
        config: SandboxConfig,
        env: Dict[str, str],
        start_time: float
    ) -> SandboxResult:
        """Run command in Docker container"""
        try:
            # Ensure project path exists
            project_path = Path(project_path).resolve()
            if not project_path.exists():
                return SandboxResult(
                    success=False,
                    exit_code=-1,
                    stdout="",
                    stderr="",
                    execution_time=0,
                    error=f"Project path does not exist: {project_path}"
                )
            
            # Prepare volumes
            volumes = {
                str(project_path): {
                    'bind': config.working_dir,
                    'mode': 'rw'
                }
            }
            
            # Prepare environment
            container_env = {
                'PYTHONPATH': config.working_dir,
                'HOME': '/tmp',
                **env
            }
            
            logger.info(f"🐳 Running in Docker: {command}")
            
            # Run container
            container = self.docker_client.containers.run(
                image=config.image,
                command=f"bash -c '{command}'",
                volumes=volumes,
                working_dir=config.working_dir,
                environment=container_env,
                network_mode=config.network,
                mem_limit=config.memory_limit,
                cpu_count=int(config.cpu_limit),
                detach=True,
                remove=True,
                user="1000:1000",  # Non-root user
                cap_drop=["ALL"],   # Drop all capabilities
                security_opt=["no-new-privileges:true"]
            )
            
            # Wait for completion with timeout
            try:
                exit_code = container.wait(timeout=config.timeout)['StatusCode']
                logs = container.logs(stdout=True, stderr=True).decode('utf-8', errors='ignore')
                
                # Split stdout and stderr (simplified)
                stdout = logs
                stderr = ""
                
                execution_time = time.time() - start_time
                
                return SandboxResult(
                    success=exit_code == 0,
                    exit_code=exit_code,
                    stdout=stdout,
                    stderr=stderr,
                    execution_time=execution_time
                )
                
            except docker.errors.APIError as e:
                if "timeout" in str(e).lower():
                    container.kill()
                    return SandboxResult(
                        success=False,
                        exit_code=-1,
                        stdout="",
                        stderr="Command timed out",
                        execution_time=time.time() - start_time,
                        timeout=True
                    )
                else:
                    raise
            
        except Exception as e:
            logger.error(f"🐳 Docker execution error: {e}")
            return SandboxResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr="",
                execution_time=time.time() - start_time,
                error=str(e)
            )
    
    async def _run_local(
        self,
        command: str,
        project_path: str,
        config: SandboxConfig,
        env: Dict[str, str],
        start_time: float
    ) -> SandboxResult:
        """Run command locally (fallback when Docker unavailable)"""
        logger.warning("🐳 Running locally (Docker unavailable) - SECURITY RISK!")
        
        try:
            # Prepare environment
            local_env = os.environ.copy()
            local_env.update(env)
            local_env['PYTHONPATH'] = project_path
            
            # Run command with timeout
            process = subprocess.Popen(
                command,
                shell=True,
                cwd=project_path,
                env=local_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            try:
                stdout, stderr = process.communicate(timeout=config.timeout)
                exit_code = process.returncode
                
                execution_time = time.time() - start_time
                
                return SandboxResult(
                    success=exit_code == 0,
                    exit_code=exit_code,
                    stdout=stdout,
                    stderr=stderr,
                    execution_time=execution_time
                )
                
            except subprocess.TimeoutExpired:
                process.kill()
                return SandboxResult(
                    success=False,
                    exit_code=-1,
                    stdout="",
                    stderr="Command timed out",
                    execution_time=time.time() - start_time,
                    timeout=True
                )
            
        except Exception as e:
            logger.error(f"🐳 Local execution error: {e}")
            return SandboxResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr="",
                execution_time=time.time() - start_time,
                error=str(e)
            )
    
    async def run_tests(self, project_path: str, test_command: str = None) -> SandboxResult:
        """Run tests in the project"""
        if test_command is None:
            # Auto-detect test command
            project_path_obj = Path(project_path)
            
            if (project_path_obj / "pytest.ini").exists() or (project_path_obj / "pyproject.toml").exists():
                test_command = "python -m pytest -v"
            elif (project_path_obj / "package.json").exists():
                test_command = "npm test"
            else:
                test_command = "python -m pytest -v"  # Default
        
        config = SandboxConfig(
            image=self.images["python"],
            timeout=300  # 5 minutes for tests
        )
        
        return await self.run_command(test_command, project_path, config)
    
    async def run_static_analysis(self, project_path: str, targets: List[str]) -> Dict[str, SandboxResult]:
        """Run static analysis tools"""
        results = {}
        
        # Python static analysis
        if any(target.endswith('.py') for target in targets):
            # MyPy type checking
            mypy_result = await self.run_command(
                f"python -m mypy {' '.join(targets)}",
                project_path,
                SandboxConfig(image=self.images["python"])
            )
            results["mypy"] = mypy_result
            
            # Ruff linting
            ruff_result = await self.run_command(
                f"python -m ruff check {' '.join(targets)}",
                project_path,
                SandboxConfig(image=self.images["python"])
            )
            results["ruff"] = ruff_result
            
            # Bandit security analysis
            bandit_result = await self.run_command(
                f"python -m bandit -r {' '.join(targets)}",
                project_path,
                SandboxConfig(image=self.images["python"])
            )
            results["bandit"] = bandit_result
        
        # JavaScript/TypeScript static analysis
        js_files = [t for t in targets if t.endswith(('.js', '.ts'))]
        if js_files:
            # ESLint
            eslint_result = await self.run_command(
                f"npx eslint {' '.join(js_files)}",
                project_path,
                SandboxConfig(image=self.images["node"])
            )
            results["eslint"] = eslint_result
            
            # TypeScript compiler
            if any(f.endswith('.ts') for f in js_files):
                tsc_result = await self.run_command(
                    "npx tsc --noEmit",
                    project_path,
                    SandboxConfig(image=self.images["node"])
                )
                results["typescript"] = tsc_result
        
        return results
    
    async def install_dependencies(self, project_path: str) -> SandboxResult:
        """Install project dependencies"""
        project_path_obj = Path(project_path)
        
        # Python project
        if (project_path_obj / "requirements.txt").exists():
            return await self.run_command(
                "pip install -r requirements.txt",
                project_path,
                SandboxConfig(image=self.images["python"], timeout=300)
            )
        elif (project_path_obj / "pyproject.toml").exists():
            return await self.run_command(
                "pip install -e .",
                project_path,
                SandboxConfig(image=self.images["python"], timeout=300)
            )
        
        # Node.js project
        elif (project_path_obj / "package.json").exists():
            return await self.run_command(
                "npm install",
                project_path,
                SandboxConfig(image=self.images["node"], timeout=300)
            )
        
        else:
            return SandboxResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr="No dependency file found",
                execution_time=0,
                error="No requirements.txt, pyproject.toml, or package.json found"
            )
    
    def prepare_sandbox_image(self, image_name: str, dockerfile_content: str = None):
        """Prepare a custom sandbox image"""
        if not self.docker_available:
            logger.warning("🐳 Cannot prepare image - Docker unavailable")
            return False
        
        try:
            if dockerfile_content:
                # Build custom image
                with tempfile.TemporaryDirectory() as temp_dir:
                    dockerfile_path = Path(temp_dir) / "Dockerfile"
                    dockerfile_path.write_text(dockerfile_content)
                    
                    self.docker_client.images.build(
                        path=temp_dir,
                        tag=image_name,
                        rm=True
                    )
            else:
                # Pull existing image
                self.docker_client.images.pull(image_name)
            
            logger.info(f"🐳 Prepared sandbox image: {image_name}")
            return True
            
        except Exception as e:
            logger.error(f"🐳 Error preparing image {image_name}: {e}")
            return False

# Test the sandbox
async def test_sandbox():
    """Test the sandbox functionality"""
    print("🧪 Testing Sandbox...")
    
    sandbox = Sandbox()
    
    # Create test project
    test_dir = Path("test_sandbox_project")
    test_dir.mkdir(exist_ok=True)
    
    # Create test file
    test_file = test_dir / "test.py"
    test_file.write_text("""
def add(a, b):
    return a + b

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0

if __name__ == "__main__":
    test_add()
    print("All tests passed!")
""")
    
    # Test running Python code
    result = await sandbox.run_command("python test.py", str(test_dir))
    print(f"✅ Python execution: success={result.success}, exit_code={result.exit_code}")
    print(f"   Output: {result.stdout.strip()}")
    
    # Test running tests
    test_result = await sandbox.run_tests(str(test_dir), "python test.py")
    print(f"✅ Test execution: success={test_result.success}")
    
    # Cleanup
    import shutil
    shutil.rmtree(test_dir)
    
    print("🧪 Sandbox test completed!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_sandbox())