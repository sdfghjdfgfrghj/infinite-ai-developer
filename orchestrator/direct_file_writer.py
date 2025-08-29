#!/usr/bin/env python3
"""
🔧 Direct File Writer - Simple, reliable file creation
Replaces the complex tool bus with direct file operations
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any
import git

logger = logging.getLogger(__name__)

class DirectFileWriter:
    """
    Simple, direct file writer that actually works.
    No complex tool bus - just write files where they should go.
    """
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.project_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize git repo if needed
        self._init_git()
        
        logger.info(f"📁 Direct file writer initialized: {self.project_path}")
    
    def _init_git(self):
        """Initialize git repository"""
        try:
            self.repo = git.Repo(self.project_path)
            logger.info("📁 Using existing git repo")
        except git.exc.InvalidGitRepositoryError:
            self.repo = git.Repo.init(self.project_path)
            
            # Create .gitignore
            gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
.coverage
.pytest_cache/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"""
            gitignore_path = self.project_path / ".gitignore"
            gitignore_path.write_text(gitignore_content.strip())
            
            self.repo.index.add([".gitignore"])
            self.repo.index.commit("Initial commit - Autonomous AI Developer")
            
            logger.info("📁 Initialized new git repo")
    
    def write_file(self, file_path: str, content: str, commit_message: str = None):
        """
        Write a single file - simple and direct
        
        Args:
            file_path: Relative path within project
            content: File content
            commit_message: Optional commit message
        """
        try:
            # Ensure relative path
            if file_path.startswith('/'):
                file_path = file_path[1:]
            
            full_path = self.project_path / file_path
            
            # Create parent directories
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            full_path.write_text(content, encoding='utf-8')
            
            logger.info(f"📄 Created file: {full_path}")
            
            # Git add and commit
            if commit_message:
                try:
                    self.repo.index.add([file_path])
                    self.repo.index.commit(commit_message)
                    logger.info(f"📝 Committed: {commit_message}")
                except Exception as e:
                    logger.warning(f"📝 Git commit failed: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to write {file_path}: {e}")
            return False
    
    def write_multiple_files(self, files: List[Dict[str, str]], commit_message: str):
        """
        Write multiple files at once and handle dependencies
        
        Args:
            files: List of {"path": "file.py", "content": "code..."}
            commit_message: Commit message for all files
        """
        created_files = []
        
        try:
            for file_info in files:
                file_path = file_info["path"]
                content = file_info["content"]
                
                # Ensure relative path
                if file_path.startswith('/'):
                    file_path = file_path[1:]
                
                full_path = self.project_path / file_path
                
                # Create parent directories
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Write file
                full_path.write_text(content, encoding='utf-8')
                created_files.append(file_path)
                
                logger.info(f"📄 Created file: {full_path}")
            
            # Auto-detect and install dependencies
            self._auto_install_dependencies(created_files)
            
            # Git add and commit all files
            if created_files:
                try:
                    self.repo.index.add(created_files)
                    self.repo.index.commit(commit_message)
                    logger.info(f"📝 Committed {len(created_files)} files: {commit_message}")
                except Exception as e:
                    logger.warning(f"📝 Git commit failed: {e}")
            
            return {"success": True, "files_created": created_files}
            
        except Exception as e:
            logger.error(f"❌ Failed to write files: {e}")
            return {"success": False, "error": str(e), "files_created": created_files}
    
    def parse_ai_response_and_write(self, ai_response: str, commit_message: str):
        """
        Parse AI response for file creation and write them directly
        
        Looks for patterns like:
        - "path": "filename.py"
        - ```python ... ``` code blocks
        - JSON tool calls
        """
        try:
            # Try to parse as JSON first (tool calls)
            if "tool_calls" in ai_response or '"path"' in ai_response:
                return self._parse_json_and_write(ai_response, commit_message)
            
            # Try to parse code blocks
            return self._parse_code_blocks_and_write(ai_response, commit_message)
            
        except Exception as e:
            logger.error(f"❌ Failed to parse AI response: {e}")
            return {"success": False, "error": str(e)}
    
    def _parse_json_and_write(self, response: str, commit_message: str):
        """Parse JSON tool calls and write files"""
        try:
            # Look for JSON in the response
            import re
            json_matches = re.findall(r'\{[^{}]*"tool_calls"[^{}]*\}', response, re.DOTALL)
            
            if not json_matches:
                # Look for direct file specifications
                path_matches = re.findall(r'"path":\s*"([^"]+)"', response)
                content_matches = re.findall(r'"content":\s*"([^"]+)"', response, re.DOTALL)
                
                if path_matches and content_matches:
                    files = [{"path": path, "content": content} 
                            for path, content in zip(path_matches, content_matches)]
                    return self.write_multiple_files(files, commit_message)
            
            for json_str in json_matches:
                try:
                    data = json.loads(json_str)
                    if "tool_calls" in data:
                        for call in data["tool_calls"]:
                            if call.get("name") == "repo_write":
                                params = call.get("parameters", {})
                                if "edits" in params:
                                    files = []
                                    for edit in params["edits"]:
                                        if edit.get("mode") in ["create", "replace"]:
                                            files.append({
                                                "path": edit["path"],
                                                "content": edit["content"]
                                            })
                                    if files:
                                        return self.write_multiple_files(files, commit_message)
                except json.JSONDecodeError:
                    continue
            
            return {"success": False, "error": "No valid file specifications found"}
            
        except Exception as e:
            logger.error(f"❌ JSON parsing failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _parse_code_blocks_and_write(self, response: str, commit_message: str):
        """Parse code blocks and write files with intelligent naming"""
        try:
            import re
            
            # Look for explicit file specifications first
            file_patterns = [
                r'(?:File|Filename|Path):\s*([a-zA-Z_][a-zA-Z0-9_/]*\.py)',
                r'```python\s*#\s*([a-zA-Z_][a-zA-Z0-9_/]*\.py)',
                r'```py\s*#\s*([a-zA-Z_][a-zA-Z0-9_/]*\.py)',
                r'Create\s+file\s+([a-zA-Z_][a-zA-Z0-9_/]*\.py)',
                r'Save\s+as\s+([a-zA-Z_][a-zA-Z0-9_/]*\.py)'
            ]
            
            # Look for code blocks with file names
            pattern = r'```(?:python|py)?\s*(?:#\s*(.+\.py))?\s*\n(.*?)\n```'
            matches = re.findall(pattern, response, re.DOTALL)
            
            files = []
            for i, (filename, content) in enumerate(matches):
                if not filename:
                    # Try to extract filename from nearby text
                    filename = self._intelligent_filename_from_content(content, i)
                
                files.append({"path": filename, "content": content.strip()})
            
            # If no code blocks found, try to extract from response text
            if not files:
                files = self._extract_files_from_text(response)
            
            if files:
                return self.write_multiple_files(files, commit_message)
            
            return {"success": False, "error": "No code blocks found"}
            
        except Exception as e:
            logger.error(f"❌ Code block parsing failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _intelligent_filename_from_content(self, content: str, index: int) -> str:
        """Generate intelligent filename with proper directory structure"""
        content_lower = content.lower()
        
        # Check for main application patterns
        if 'if __name__ == "__main__"' in content and ('main()' in content or 'app()' in content):
            return "main.py"
        
        # Check for specific patterns with proper directory structure
        if 'class.*user' in content_lower or 'def.*user' in content_lower:
            if 'api' in content_lower or 'endpoint' in content_lower:
                return "api/users.py"
            else:
                return "services/user_service.py"
        elif 'class.*auth' in content_lower or 'def.*auth' in content_lower or 'login' in content_lower:
            if 'api' in content_lower or 'endpoint' in content_lower:
                return "api/auth.py"
            else:
                return "auth/authentication.py"
        elif 'database' in content_lower or 'db' in content_lower or 'sqlite' in content_lower:
            if 'model' in content_lower:
                return "database/models.py"
            else:
                return "database/connection.py"
        elif 'api' in content_lower or 'endpoint' in content_lower or 'route' in content_lower:
            return "api/routes.py"
        elif 'test' in content_lower or 'assert' in content_lower:
            return f"tests/test_{index + 1}.py"
        elif 'config' in content_lower or 'settings' in content_lower:
            return "config/settings.py"
        elif 'model' in content_lower and 'class' in content_lower:
            return "models/data_models.py"
        elif 'util' in content_lower or 'helper' in content_lower:
            return "utils/helpers.py"
        elif 'password' in content_lower:
            return "tools/password_generator.py"
        elif 'game' in content_lower or 'guess' in content_lower:
            return "game.py"
        elif 'calculator' in content_lower or 'add' in content_lower:
            return "calculator.py"
        elif 'scraper' in content_lower or 'scrape' in content_lower:
            return "scrapers/web_scraper.py"
        elif 'frontend' in content_lower or 'html' in content_lower or 'css' in content_lower:
            return "frontend/app.py"
        elif 'static' in content_lower:
            return "static/main.js"
        elif 'template' in content_lower:
            return "templates/index.html"
        else:
            return f"modules/module_{index + 1}.py"
    
    def _extract_files_from_text(self, response: str) -> list:
        """Extract file information from response text when no code blocks found"""
        # This is a fallback for when the AI doesn't use code blocks
        # Look for Python code patterns in the text
        import re
        
        # Simple heuristic: if response contains Python keywords, treat as single file
        python_keywords = ['def ', 'class ', 'import ', 'from ', 'if __name__']
        if any(keyword in response for keyword in python_keywords):
            filename = self._intelligent_filename_from_content(response, 0)
            return [{"path": filename, "content": response.strip()}]
        
        return []
    
    def _auto_install_dependencies(self, created_files: List[str]):
        """
        Auto-detect and install Python dependencies from created files
        """
        try:
            dependencies = set()
            
            # Scan all Python files for imports
            for file_path in created_files:
                if file_path.endswith('.py'):
                    full_path = self.project_path / file_path
                    try:
                        content = full_path.read_text(encoding='utf-8')
                        deps = self._extract_dependencies(content)
                        dependencies.update(deps)
                    except Exception as e:
                        logger.warning(f"📦 Could not scan {file_path} for dependencies: {e}")
            
            if dependencies:
                logger.info(f"📦 Detected dependencies: {list(dependencies)}")
                
                # Create requirements.txt
                requirements_path = self.project_path / "requirements.txt"
                requirements_content = "\n".join(sorted(dependencies)) + "\n"
                requirements_path.write_text(requirements_content)
                logger.info(f"📦 Created requirements.txt with {len(dependencies)} dependencies")
                
                # Try to install dependencies
                self._install_dependencies(dependencies)
            
        except Exception as e:
            logger.warning(f"📦 Dependency auto-detection failed: {e}")
    
    def _extract_dependencies(self, code_content: str) -> set:
        """Extract Python package dependencies from code"""
        import re
        
        dependencies = set()
        
        # Common import patterns
        import_patterns = [
            r'^import\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'^from\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+import',
        ]
        
        # Known standard library modules (don't need installation)
        stdlib_modules = {
            'os', 'sys', 're', 'json', 'urllib', 'pathlib', 'logging', 'datetime',
            'collections', 'itertools', 'functools', 'typing', 'argparse', 'subprocess',
            'threading', 'multiprocessing', 'asyncio', 'time', 'random', 'math',
            'string', 'io', 'tempfile', 'shutil', 'glob', 'csv', 'xml', 'html',
            'http', 'email', 'base64', 'hashlib', 'hmac', 'secrets', 'uuid'
        }
        
        # Package name mappings (import name -> pip package name)
        package_mappings = {
            'cv2': 'opencv-python',
            'PIL': 'Pillow',
            'sklearn': 'scikit-learn',
            'yaml': 'PyYAML',
            'bs4': 'beautifulsoup4',
            'requests_oauthlib': 'requests-oauthlib',
            'jwt': 'PyJWT',
            'dotenv': 'python-dotenv',
            'psycopg2': 'psycopg2-binary',
            'MySQLdb': 'mysqlclient',
            'discord': 'discord.py',
            'telebot': 'pyTelegramBotAPI',
            'yt_dlp': 'yt-dlp',
        }
        
        lines = code_content.split('\n')
        for line in lines:
            line = line.strip()
            for pattern in import_patterns:
                match = re.match(pattern, line)
                if match:
                    module_name = match.group(1)
                    
                    # Skip standard library modules
                    if module_name in stdlib_modules:
                        continue
                    
                    # Use mapping if available, otherwise use module name
                    package_name = package_mappings.get(module_name, module_name)
                    dependencies.add(package_name)
        
        return dependencies
    
    def _install_dependencies(self, dependencies: set):
        """Install Python packages using pip"""
        import subprocess
        
        for package in dependencies:
            try:
                logger.info(f"📦 Installing {package}...")
                result = subprocess.run([
                    'python3', '-m', 'pip', 'install', '--user', package
                ], capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    logger.info(f"✅ Successfully installed {package}")
                else:
                    logger.warning(f"❌ Failed to install {package}: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                logger.warning(f"⏰ Installation of {package} timed out")
            except Exception as e:
                logger.warning(f"❌ Error installing {package}: {e}")

# Test the direct file writer
def test_direct_writer():
    """Test the direct file writer"""
    import tempfile
    import shutil
    
    # Create temp directory
    temp_dir = tempfile.mkdtemp()
    
    try:
        writer = DirectFileWriter(temp_dir)
        
        # Test single file
        result = writer.write_file("test.py", "print('Hello, World!')", "Add test file")
        print(f"Single file test: {result}")
        
        # Test multiple files
        files = [
            {"path": "main.py", "content": "def main():\n    print('Main function')"},
            {"path": "utils/helper.py", "content": "def helper():\n    return 'Helper function'"}
        ]
        result = writer.write_multiple_files(files, "Add main files")
        print(f"Multiple files test: {result}")
        
        # List created files
        created_files = list(Path(temp_dir).rglob("*.py"))
        print(f"Created files: {[str(f.relative_to(temp_dir)) for f in created_files]}")
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)
    
    print("✅ Direct file writer test completed!")

if __name__ == "__main__":
    test_direct_writer()