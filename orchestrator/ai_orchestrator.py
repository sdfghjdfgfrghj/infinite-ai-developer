#!/usr/bin/env python3
"""
🤖 AI-Powered Orchestrator - Phase B
Integrates your 30B model with the autonomous development system

This is where the magic happens - real AI actors working together!
"""

import asyncio
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import logging

# Import our Phase A foundation
from .main import AutonomousOrchestrator, ProjectState, Phase
from .direct_file_writer import DirectFileWriter
from models.client import ModelClient, ModelConfig
from models.schemas import SchemaValidator, ResponseTemplates
from tools.repo_api import RepoService
from tools.sandbox import Sandbox

logger = logging.getLogger(__name__)

class AIOrchestrator(AutonomousOrchestrator):
    """
    Enhanced orchestrator with real AI integration.
    
    This extends the Phase A orchestrator with actual AI actors using your 30B model.
    """
    
    def __init__(self, config_path: str = "orchestrator/policies.yaml"):
        super().__init__(config_path)
        
        # Load configuration
        self.policies = self._load_policies()
        
        # Initialize AI components
        model_config = ModelConfig(
            host=self.policies.get("model", {}).get("host", "http://localhost:11434"),
            model_name=self.policies.get("model", {}).get("name", "qwen3-coder:30b-a3b-q4_K_M"),
            timeout=self.policies.get("model", {}).get("timeout", 300)
        )
        
        self.model_client = ModelClient(model_config)
        self.schema_validator = SchemaValidator()
        
        # Initialize direct file writer (replaces broken tool bus)
        self.file_writer = None  # Will be initialized when project starts
        
        logger.info("🤖 AI Orchestrator initialized with 30B model integration")
    
    def _load_policies(self) -> Dict[str, Any]:
        """Load policies from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"🤖 Could not load policies: {e}, using defaults")
            return {}
    
    # Enhanced phase implementations with real AI
    
    async def _phase_plan(self):
        """Project Manager creates plan using AI"""
        logger.info("📋 AI Project Manager analyzing requirements...")
        
        # Prepare context for PM
        context = {
            "requirements": self.state.requirements,
            "project_path": self.state.project_path,
            "complexity": self._assess_complexity()
        }
        
        # No tools needed for PM - just planning
        tools = None
        
        # Call PM AI actor
        pm_prompt = f"""
Analyze these requirements and create a comprehensive project plan:

REQUIREMENTS: {self.state.requirements}

{ResponseTemplates.pm_response_template()}

Focus on:
1. Breaking down requirements into clear milestones
2. Defining specific acceptance tests
3. Creating logical file structure
4. Identifying potential risks
5. Setting realistic scope

Create the initial project structure using repo_write tool calls.
"""
        
        response = await self.model_client.call_ai_actor(
            role="pm",
            user_message=pm_prompt,
            context=context,
            tools=tools
        )
        
        if response.success:
            # Parse and validate response
            parsed = self.schema_validator.validate_ai_response(response.content, "plan")
            
            if parsed["success"]:
                # Store plan results
                self.state.acceptance_tests = parsed.get("acceptance_tests", [])
                
                # Execute any tool calls
                if "tool_calls" in parsed:
                    await self._execute_tool_calls(parsed["tool_calls"])
                
                logger.info(f"📋 PM created plan with {len(self.state.acceptance_tests)} acceptance tests")
                self.state.phase = Phase.ARCHITECT
            else:
                logger.error(f"📋 PM response validation failed: {parsed.get('error')}")
                # Fallback to simple plan
                self.state.acceptance_tests = ["Application runs without errors"]
                self.state.phase = Phase.ARCHITECT
        else:
            logger.error(f"📋 PM AI call failed: {response.error}")
            # Fallback
            self.state.acceptance_tests = ["Application runs without errors"]
            self.state.phase = Phase.ARCHITECT
    
    async def _phase_architect(self):
        """Architect designs system using AI"""
        logger.info("🏗️ AI Architect designing system architecture...")
        
        context = {
            "requirements": self.state.requirements,
            "acceptance_tests": self.state.acceptance_tests,
            "project_path": self.state.project_path
        }
        
        # No tools needed for Architect - just design
        tools = None
        
        architect_prompt = f"""
Design the software architecture for this project:

REQUIREMENTS: {self.state.requirements}
ACCEPTANCE TESTS: {self.state.acceptance_tests}

{ResponseTemplates.architect_response_template()}

Consider:
1. Appropriate architectural patterns
2. Module boundaries and interfaces
3. Technology stack selection
4. Scalability and maintainability
5. Testing strategy

Create scaffolding files using repo_write tool calls.
"""
        
        response = await self.model_client.call_ai_actor(
            role="architect",
            user_message=architect_prompt,
            context=context,
            tools=tools
        )
        
        if response.success:
            parsed = self.schema_validator.validate_ai_response(response.content, "architecture")
            
            if parsed["success"]:
                # Store architecture decisions
                self.state.build_cmd = "python -m pytest"
                self.state.test_cmd = "python -m pytest tests/ -v"
                
                # Execute tool calls
                if "tool_calls" in parsed:
                    await self._execute_tool_calls(parsed["tool_calls"])
                
                logger.info(f"🏗️ Architect designed {parsed.get('pattern', 'unknown')} architecture")
                self.state.phase = Phase.CODE_WRITE  # Write code first, then tests!
            else:
                logger.error(f"🏗️ Architect response validation failed")
                self.state.phase = Phase.TEST_WRITE
        else:
            logger.error(f"🏗️ Architect AI call failed: {response.error}")
            self.state.phase = Phase.CODE_WRITE
    
    async def _phase_code_write(self):
        """Coder writes the actual implementation using AI"""
        logger.info("💻 AI Coder writing implementation...")
        
        # Read current project files
        repo = RepoService(self.state.project_path)
        files = repo.read_files(["**/*.py", "**/*.js", "**/*.ts"])
        
        context = {
            "requirements": self.state.requirements,
            "acceptance_tests": self.state.acceptance_tests,
            "existing_files": files.get("files", {})
        }
        
        # No tools needed - we'll parse response directly
        tools = None
        
        code_prompt = f"""
Write the complete implementation for this project:

REQUIREMENTS: {self.state.requirements}
ACCEPTANCE TESTS: {self.state.acceptance_tests}

EXISTING FILES:
{self._format_files_for_prompt(files.get("files", {}))}

CRITICAL: Create RUNNABLE applications, not just function definitions!

Requirements for ALL code:
1. Include a main() function that demonstrates the functionality
2. Add if __name__ == "__main__": main() at the end
3. Create interactive CLI interfaces where appropriate
4. Make the program actually DO something when run
5. Include example usage and clear output
6. Add ROBUST error handling and user feedback
7. Create complete, working applications that users can run immediately

CRITICAL ERROR HANDLING REQUIREMENTS:
- Validate ALL user inputs with try/catch blocks
- Handle invalid inputs gracefully (don't crash!)
- Provide helpful error messages and retry options
- Use input validation loops that keep asking until valid input
- Handle edge cases like empty input, wrong types, out of range values
- Never let the program crash from user input errors
- Always provide fallback defaults or retry mechanisms

Example structure:
```python
def main_functionality():
    # Core logic here
    pass

def main():
    print("Welcome to [App Name]!")
    # Interactive interface or demo
    # Show the functionality working
    print("Example usage:")
    # Demonstrate with real examples
    
if __name__ == "__main__":
    main()
```

Use repo_write to create/update implementation files. Write production-ready, EXECUTABLE code.

CRITICAL FILE NAMING AND STRUCTURE REQUIREMENTS:
- Use meaningful, descriptive file names (NOT generic names like "generated_code_1.py")
- Create proper directory structures for complex projects
- Use this format: "File: path/filename.py" or "# path/filename.py" before code blocks
- IMPORTANT: When creating files in subfolders, ensure imports work correctly:
  * Use relative imports: from .database.models import User
  * Or absolute imports: from api.auth import authenticate
  * Create __init__.py files in directories to make them Python packages
  * In main.py, use: from api.auth import login, from database.models import User
- Examples:
  * main.py (entry point)
  * api/auth.py (authentication API)
  * api/users.py (user management API)
  * database/models.py (data models)
  * database/connection.py (database setup)
  * services/user_service.py (business logic)
  * utils/helpers.py (utility functions)
  * config/settings.py (configuration)
  * tests/test_auth.py (authentication tests)
  * frontend/app.py (frontend application)
  * static/style.css (CSS files)
  * templates/index.html (HTML templates)
"""
        
        response = await self.model_client.call_ai_actor(
            role="coder",
            user_message=code_prompt,
            context=context,
            tools=tools
        )
        
        if response.success:
            # Initialize file writer if not done yet
            if not self.file_writer:
                self.file_writer = DirectFileWriter(self.state.project_path)
            
            # SKIP BROKEN SCHEMA VALIDATOR - Use direct parsing always
            logger.info("💻 Using direct response parsing (schema validator bypassed)")
            
            # Always use direct parsing since schema validator is broken
            result = self.file_writer.parse_ai_response_and_write(
                response.content, 
                "AI Coder implementation"
            )
            if result["success"]:
                logger.info(f"💻 Coder created {len(result.get('files_created', []))} files")
            else:
                # Try old method as backup
                parsed = self.schema_validator.validate_ai_response(response.content)
                if parsed["success"] and "tool_calls" in parsed:
                    await self._execute_tool_calls(parsed["tool_calls"])
                logger.info("💻 Using direct response parsing for file creation")
                logger.info(f"🔍 DEBUG: AI Response preview: {response.content[:200]}...")
                logger.info(f"🔍 DEBUG: Response contains 'class': {'class' in response.content}")
                logger.info(f"🔍 DEBUG: Response contains 'def': {'def' in response.content}")
                logger.info(f"🔍 DEBUG: Response contains code blocks: {'```' in response.content}")
                
                result = self.file_writer.parse_ai_response_and_write(
                    response.content, 
                    "AI Coder implementation"
                )
                if result["success"]:
                    logger.info(f"💻 Coder created {len(result.get('files_created', []))} files")
                else:
                    logger.warning(f"💻 Direct parsing failed: {result.get('error')}")
                    logger.warning(f"🔍 DEBUG: Full AI response: {response.content}")
            
        self.state.phase = Phase.TEST_WRITE
    
    async def _phase_test_write(self):
        """Test Engineer writes tests using AI"""
        logger.info("🧪 AI Test Engineer writing comprehensive tests...")
        
        # Read current project files
        repo = RepoService(self.state.project_path)
        files = repo.read_files(["**/*.py", "**/*.js", "**/*.ts"])
        
        context = {
            "requirements": self.state.requirements,
            "acceptance_tests": self.state.acceptance_tests,
            "existing_files": files.get("files", {})
        }
        
        # No tools needed - we'll parse response directly  
        tools = None
        
        test_prompt = f"""
Write comprehensive tests for this project:

REQUIREMENTS: {self.state.requirements}
ACCEPTANCE TESTS: {self.state.acceptance_tests}

EXISTING FILES:
{self._format_files_for_prompt(files.get("files", {}))}

Create:
1. Unit tests for all functions/classes
2. Integration tests for component interactions  
3. Acceptance tests based on requirements
4. Property-based tests for edge cases

Use repo_write to create test files. Follow testing best practices.
"""
        
        response = await self.model_client.call_ai_actor(
            role="test_engineer",
            user_message=test_prompt,
            context=context,
            tools=tools
        )
        
        if response.success:
            parsed = self.schema_validator.validate_ai_response(response.content)
            
            if parsed["success"] and "tool_calls" in parsed:
                await self._execute_tool_calls(parsed["tool_calls"])
                logger.info("🧪 Test Engineer created comprehensive test suite")
            
        self.state.phase = Phase.BUILD_RUN
    
    async def _phase_build_run(self):
        """Run tests and static analysis using sandbox"""
        logger.info("🚀 Running tests and static analysis...")
        
        # Initialize sandbox and repo
        sandbox = Sandbox()
        
        # Install dependencies first
        install_result = await sandbox.install_dependencies(self.state.project_path)
        if not install_result.success:
            logger.warning(f"🚀 Dependency installation failed: {install_result.stderr}")
        
        # Run tests
        test_result = await sandbox.run_tests(self.state.project_path, self.state.test_cmd)
        
        # Run static analysis
        analysis_results = await sandbox.run_static_analysis(
            self.state.project_path, 
            ["**/*.py"]
        )
        
        # Check results
        tests_passed = test_result.success
        analysis_clean = all(result.success for result in analysis_results.values())
        
        if tests_passed and analysis_clean:
            logger.info("🚀 All tests passed and analysis clean!")
            self.state.phase = Phase.VERIFY
        else:
            # Store failure logs for debugging
            self.state.last_logs = self._format_failure_logs(test_result, analysis_results)
            logger.warning("🚀 Tests failed or analysis issues found")
            self.state.phase = Phase.DIAGNOSE
    
    async def _phase_diagnose(self):
        """Debugger analyzes failures using AI"""
        logger.info("🔍 AI Debugger analyzing failures...")
        
        # Get current diff
        repo = RepoService(self.state.project_path)
        current_diff = repo.get_diff()
        
        context = {
            "failure_logs": self.state.last_logs,
            "current_diff": current_diff,
            "requirements": self.state.requirements
        }
        
        tools = [self.tool_bus.tools["repo_write"]]
        
        debug_prompt = f"""
Analyze these test failures and propose fixes:

FAILURE LOGS:
{self.state.last_logs}

CURRENT CODE DIFF:
{current_diff}

REQUIREMENTS: {self.state.requirements}

Identify:
1. Root cause of failures
2. Minimal fix needed
3. Regression tests to add

Use repo_write to apply fixes. Keep changes minimal and focused.
"""
        
        response = await self.model_client.call_ai_actor(
            role="debugger",
            user_message=debug_prompt,
            context=context,
            tools=tools
        )
        
        if response.success:
            parsed = self.schema_validator.validate_ai_response(response.content)
            
            if parsed["success"] and "tool_calls" in parsed:
                await self._execute_tool_calls(parsed["tool_calls"])
                logger.info("🔍 Debugger applied fixes")
            
        self.state.phase = Phase.REPAIR
    
    async def _phase_repair(self):
        """Test fixes and continue or loop back"""
        logger.info("🔧 Testing repairs...")
        
        sandbox = Sandbox()
        test_result = await sandbox.run_tests(self.state.project_path, self.state.test_cmd)
        
        if test_result.success:
            logger.info("🔧 Repairs successful!")
            self.state.phase = Phase.VERIFY
        else:
            logger.warning("🔧 Repairs didn't fix all issues")
            self.state.last_logs = test_result.stderr
            self.state.phase = Phase.DIAGNOSE
    
    async def _phase_verify(self):
        """Verifier checks completion using AI"""
        logger.info("✅ AI Verifier checking completion...")
        
        # Get final project state
        repo = RepoService(self.state.project_path)
        files = repo.read_files(["**/*"])
        
        sandbox = Sandbox()
        final_test_result = await sandbox.run_tests(self.state.project_path)
        
        context = {
            "requirements": self.state.requirements,
            "acceptance_tests": self.state.acceptance_tests,
            "final_test_result": final_test_result.stdout,
            "project_files": len(files.get("files", {}))
        }
        
        verify_prompt = f"""
Verify if this project is complete and meets all requirements:

REQUIREMENTS: {self.state.requirements}
ACCEPTANCE TESTS: {self.state.acceptance_tests}

FINAL TEST RESULTS:
{final_test_result.stdout}

PROJECT STATUS:
- Files created: {len(files.get("files", {}))}
- Tests passing: {final_test_result.success}

Decide: Is the project complete and working? If not, what needs to be done?

Respond with JSON:
{{
  "complete": true/false,
  "reasoning": "Your assessment",
  "next_steps": ["step1", "step2"] // if not complete
}}
"""
        
        response = await self.model_client.call_ai_actor(
            role="verifier",
            user_message=verify_prompt,
            context=context
        )
        
        if response.success:
            # Try to parse decision
            try:
                import json
                decision = json.loads(response.content)
                if decision.get("complete", False):
                    logger.info("✅ Verifier approved completion!")
                    self.state.phase = Phase.DONE
                else:
                    logger.info("✅ Verifier requests more work")
                    self.state.phase = Phase.TEST_WRITE  # Continue iteration
            except:
                # Fallback decision
                if final_test_result.success:
                    self.state.phase = Phase.DONE
                else:
                    self.state.phase = Phase.DIAGNOSE
        else:
            # Fallback decision
            if final_test_result.success:
                self.state.phase = Phase.DONE
            else:
                self.state.phase = Phase.DIAGNOSE
    
    # Helper methods
    
    async def _execute_tool_calls(self, tool_calls: list):
        """Execute tool calls using direct file writer"""
        # Initialize file writer if not done yet
        if not self.file_writer:
            self.file_writer = DirectFileWriter(self.state.project_path)
        
        logger.info(f"🔍 DEBUG: Executing {len(tool_calls)} tool calls")
        logger.info(f"🔍 DEBUG: Tool calls: {tool_calls}")
        
        for call_data in tool_calls:
            if call_data["name"] == "repo_write":
                # Handle file writing directly
                params = call_data.get("parameters", {})
                edits = params.get("edits", [])
                message = params.get("message", "AI generated code")
                
                files = []
                for edit in edits:
                    if edit.get("mode") in ["create", "replace"] and "content" in edit:
                        files.append({
                            "path": edit["path"],
                            "content": edit["content"]
                        })
                
                if files:
                    result = self.file_writer.write_multiple_files(files, message)
                    if result["success"]:
                        logger.info(f"🔧 Created {len(result['files_created'])} files: {result['files_created']}")
                    else:
                        logger.error(f"🔧 File creation failed: {result.get('error')}")
                else:
                    logger.warning(f"🔧 No valid files to create in tool call")
            else:
                logger.info(f"🔧 Skipping non-file tool call: {call_data['name']}")
    
    def _assess_complexity(self) -> str:
        """Assess project complexity from requirements"""
        req_lower = self.state.requirements.lower()
        
        if any(word in req_lower for word in ["microservice", "distributed", "enterprise", "scalable"]):
            return "complex"
        elif any(word in req_lower for word in ["api", "database", "authentication", "real-time"]):
            return "moderate"
        else:
            return "simple"
    
    def _format_files_for_prompt(self, files: Dict[str, Any]) -> str:
        """Format files for AI prompt"""
        formatted = []
        for path, file_data in files.items():
            if isinstance(file_data, dict) and "content" in file_data:
                content = file_data["content"][:500]  # Truncate for prompt
                formatted.append(f"=== {path} ===\n{content}\n")
        return "\n".join(formatted)
    
    def _format_failure_logs(self, test_result, analysis_results) -> str:
        """Format failure logs for debugging"""
        logs = []
        
        if not test_result.success:
            logs.append(f"TEST FAILURES:\n{test_result.stderr}")
        
        for tool, result in analysis_results.items():
            if not result.success:
                logs.append(f"{tool.upper()} ISSUES:\n{result.stderr}")
        
        return "\n\n".join(logs)

# Test the AI orchestrator
async def test_ai_orchestrator():
    """Test the AI orchestrator"""
    print("🧪 Testing AI Orchestrator...")
    
    orchestrator = AIOrchestrator()
    
    # Test a simple project
    await orchestrator.run_autonomous_development(
        requirements="Create a simple Python calculator that can add, subtract, multiply and divide two numbers",
        project_name="test_calculator"
    )
    
    print("🧪 AI Orchestrator test completed!")

if __name__ == "__main__":
    asyncio.run(test_ai_orchestrator())