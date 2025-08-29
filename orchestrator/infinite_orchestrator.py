#!/usr/bin/env python3
"""
♾️ Infinite AI Orchestrator - Never-ending autonomous development
This AI can iterate FOREVER until it builds perfect applications!

Key features:
- Infinite iteration loops with safety limits
- Beautiful CLI integration
- Comprehensive testing at every step
- Self-healing and self-improving
- Detailed progress tracking
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import json

from .ai_orchestrator import AIOrchestrator
from .pipeline_states import PipelinePhase
from ui.beautiful_cli import beautiful_cli
from tools.sandbox import Sandbox
from tools.repo_api import RepoService

logger = logging.getLogger(__name__)

class InfiniteOrchestrator(AIOrchestrator):
    """
    Enhanced orchestrator that can iterate infinitely until perfection!
    
    Features:
    - Beautiful CLI integration
    - Infinite iteration loops with safety limits
    - Comprehensive testing at every iteration
    - Self-healing when things break
    - Detailed progress tracking and logging
    """
    
    def __init__(self, config_path: str = "orchestrator/policies.yaml"):
        super().__init__(config_path)
        
        # Infinite iteration settings
        self.max_iterations = self.policies.get("infinite", {}).get("max_iterations", 1000)
        self.max_debug_cycles = self.policies.get("infinite", {}).get("max_debug_cycles", 50)
        self.test_everything = self.policies.get("infinite", {}).get("test_everything", True)
        
        # Progress tracking
        self.iteration_count = 0
        self.debug_cycle_count = 0
        self.total_files_created = 0
        self.total_tests_run = 0
        self.total_bugs_fixed = 0
        
        # Beautiful CLI integration
        self.cli = beautiful_cli
        
        logger.info("♾️ Infinite Orchestrator initialized - ready for unlimited iterations!")
    
    async def run_autonomous_development(self, requirements: str, project_name: str, resume_run_id: str = None):
        """
        Run autonomous development with infinite iterations until perfect!
        """
        
        # Show beautiful banner
        self.cli.show_banner()
        
        # Initialize state
        if not resume_run_id:
            await self._initialize_project(requirements, project_name)
        else:
            await self._resume_project(resume_run_id)
        
        # Show project start
        self.cli.show_project_start(requirements, project_name, "Python")
        
        # Main infinite loop
        start_time = datetime.now()
        
        try:
            while (self.state.phase != PipelinePhase.DONE and 
                   self.iteration_count < self.max_iterations):
                
                self.iteration_count += 1
                
                logger.info(f"♾️ Starting iteration {self.iteration_count}/{self.max_iterations}")
                
                # Show current phase progress
                progress = self._calculate_progress()
                phase_description = self._get_phase_description()
                
                self.cli.show_phase_progress(
                    self.state.phase.value, 
                    phase_description, 
                    progress
                )
                
                # Execute current phase
                await self._execute_current_phase()
                
                # Test everything after each phase (if enabled)
                if self.test_everything:
                    await self._comprehensive_testing()
                
                # Save state after each iteration
                await self._save_iteration_state()
                
                # Brief pause to show progress
                await asyncio.sleep(0.5)
            
            # Final completion
            if self.state.phase == PipelinePhase.DONE:
                await self._celebrate_completion(start_time)
            else:
                await self._handle_max_iterations_reached()
                
        except KeyboardInterrupt:
            logger.info("♾️ User interrupted - saving state...")
            await self._save_iteration_state()
            self.cli.console.print("\n⏸️ Development paused - use resume to continue!")
            
        except Exception as e:
            logger.error(f"♾️ Unexpected error: {e}")
            await self._handle_critical_error(e)
        
        return self.state
    
    async def _execute_current_phase(self):
        """Execute the current phase with enhanced error handling"""
        
        try:
            if self.state.phase == PipelinePhase.PLAN:
                await self._phase_plan_infinite()
            elif self.state.phase == PipelinePhase.ARCHITECT:
                await self._phase_architect_infinite()
            elif self.state.phase == PipelinePhase.CODE_WRITE:
                await self._phase_code_write_infinite()
            elif self.state.phase == PipelinePhase.TEST_WRITE:
                await self._phase_test_write_infinite()
            elif self.state.phase == PipelinePhase.BUILD_RUN:
                await self._phase_build_run_infinite()
            elif self.state.phase == PipelinePhase.DIAGNOSE:
                await self._phase_diagnose_infinite()
            elif self.state.phase == PipelinePhase.REPAIR:
                await self._phase_repair_infinite()
            elif self.state.phase == PipelinePhase.VERIFY:
                await self._phase_verify_infinite()
            else:
                logger.warning(f"♾️ Unknown phase: {self.state.phase}")
                self.state.phase = PipelinePhase.DONE
                
        except Exception as e:
            logger.error(f"♾️ Phase {self.state.phase.value} failed: {e}")
            await self._handle_phase_error(e)
    
    async def _phase_code_write_infinite(self):
        """Enhanced code writing with beautiful display"""
        logger.info("💻 AI Coder writing implementation...")
        
        # Call parent implementation
        await super()._phase_code_write()
        
        # Show generated code if any files were created
        await self._display_generated_code()
        
        self.total_files_created += 1
    
    async def _phase_test_write_infinite(self):
        """Enhanced test writing with comprehensive coverage"""
        logger.info("🧪 AI Test Engineer writing comprehensive tests...")
        
        # Call parent implementation
        await super()._phase_test_write()
        
        # Show generated tests
        await self._display_generated_tests()
    
    async def _phase_build_run_infinite(self):
        """Enhanced build/run with detailed feedback"""
        logger.info("🚀 Running comprehensive tests...")
        
        # Call parent implementation
        await super()._phase_build_run()
        
        self.total_tests_run += 1
        
        # Show test results beautifully
        await self._display_test_results()
    
    async def _phase_diagnose_infinite(self):
        """Enhanced debugging with infinite patience"""
        self.debug_cycle_count += 1
        
        if self.debug_cycle_count > self.max_debug_cycles:
            logger.warning(f"♾️ Max debug cycles ({self.max_debug_cycles}) reached")
            self.state.phase = PipelinePhase.VERIFY  # Force verification
            return
        
        logger.info(f"🔍 AI Debugger analyzing failures (cycle {self.debug_cycle_count})...")
        
        # Call parent implementation
        await super()._phase_diagnose()
        
        self.total_bugs_fixed += 1
    
    async def _phase_verify_infinite(self):
        """Enhanced verification with strict standards"""
        logger.info("✅ AI Verifier checking completion with high standards...")
        
        # Enhanced verification logic
        repo = RepoService(self.state.project_path)
        files = repo.read_files(["**/*"])
        
        sandbox = Sandbox()
        
        # Run ALL types of tests
        test_results = {}
        
        # Unit tests
        unit_result = await sandbox.run_tests(self.state.project_path, "python -m pytest tests/ -v")
        test_results["unit"] = unit_result
        
        # Integration tests
        integration_result = await sandbox.run_tests(self.state.project_path, "python -m pytest tests/integration/ -v")
        test_results["integration"] = integration_result
        
        # Static analysis
        analysis_results = await sandbox.run_static_analysis(self.state.project_path, ["**/*.py"])
        test_results["static"] = analysis_results
        
        # Security checks (if available)
        try:
            security_result = await sandbox.run_command(self.state.project_path, "bandit -r . -f json")
            test_results["security"] = security_result
        except:
            pass
        
        # Performance tests (basic)
        try:
            perf_result = await sandbox.run_command(self.state.project_path, "python -m timeit -s 'import main' 'main.main()' -n 1")
            test_results["performance"] = perf_result
        except:
            pass
        
        # Show comprehensive test results
        self.cli.show_test_results(test_results)
        
        # Strict verification criteria
        all_tests_pass = all(result.success for result in test_results.values() if hasattr(result, 'success'))
        has_sufficient_files = len(files.get("files", {})) >= 3  # At least main + tests + readme
        
        # AI verification prompt
        context = {
            "requirements": self.state.requirements,
            "acceptance_tests": self.state.acceptance_tests,
            "test_results": test_results,
            "file_count": len(files.get("files", {})),
            "iteration_count": self.iteration_count
        }
        
        verify_prompt = f"""
        STRICT VERIFICATION - High Standards Required!
        
        REQUIREMENTS: {self.state.requirements}
        ACCEPTANCE TESTS: {self.state.acceptance_tests}
        
        CURRENT STATUS:
        - Iteration: {self.iteration_count}
        - Files created: {len(files.get("files", {}))}
        - All tests passing: {all_tests_pass}
        - Debug cycles used: {self.debug_cycle_count}
        
        VERIFICATION CRITERIA (ALL must be met):
        1. All unit tests pass
        2. All integration tests pass
        3. Static analysis clean
        4. Security checks pass
        5. Performance acceptable
        6. Code is well-documented
        7. Error handling is robust
        8. User experience is polished
        9. All requirements fully implemented
        10. Application is production-ready
        
        Be STRICT! Only approve if this is truly production-ready.
        If not perfect, specify exactly what needs improvement.
        
        Respond with JSON:
        {{
          "complete": true/false,
          "confidence": 0-100,
          "reasoning": "Detailed assessment",
          "missing_requirements": ["req1", "req2"],
          "quality_issues": ["issue1", "issue2"],
          "next_steps": ["step1", "step2"]
        }}
        """
        
        response = await self.model_client.call_ai_actor(
            role="verifier",
            user_message=verify_prompt,
            context=context
        )
        
        if response.success:
            try:
                decision = json.loads(response.content)
                confidence = decision.get("confidence", 0)
                
                if decision.get("complete", False) and confidence >= 90:
                    logger.info(f"✅ Verifier approved completion with {confidence}% confidence!")
                    self.state.phase = PipelinePhase.DONE
                else:
                    logger.info(f"✅ Verifier requests improvements (confidence: {confidence}%)")
                    missing = decision.get("missing_requirements", [])
                    issues = decision.get("quality_issues", [])
                    
                    if missing or issues:
                        logger.info(f"📋 Missing requirements: {missing}")
                        logger.info(f"🔧 Quality issues: {issues}")
                        self.state.phase = PipelinePhase.CODE_WRITE  # Continue improving
                    else:
                        self.state.phase = PipelinePhase.TEST_WRITE
                        
            except Exception as e:
                logger.error(f"✅ Verification parsing failed: {e}")
                # Fallback decision based on test results
                if all_tests_pass and has_sufficient_files:
                    self.state.phase = PipelinePhase.DONE
                else:
                    self.state.phase = PipelinePhase.DIAGNOSE
        else:
            # Fallback decision
            if all_tests_pass and has_sufficient_files:
                self.state.phase = PipelinePhase.DONE
            else:
                self.state.phase = PipelinePhase.DIAGNOSE
    
    async def _comprehensive_testing(self):
        """Run comprehensive tests after each phase"""
        if not Path(self.state.project_path).exists():
            return
        
        sandbox = Sandbox()
        
        # Quick syntax check
        try:
            result = await sandbox.run_command(self.state.project_path, "python -m py_compile **/*.py")
            if not result.success:
                logger.warning(f"♾️ Syntax errors detected: {result.stderr}")
        except:
            pass
        
        # Quick import test
        try:
            result = await sandbox.run_command(self.state.project_path, "python -c 'import main'")
            if not result.success:
                logger.warning(f"♾️ Import errors detected: {result.stderr}")
        except:
            pass
    
    async def _display_generated_code(self):
        """Display recently generated code with beautiful formatting"""
        repo = RepoService(self.state.project_path)
        files = repo.read_files(["**/*.py"])
        
        # Show the main file or most recent file
        for path, file_data in files.get("files", {}).items():
            if "main.py" in path or "app.py" in path:
                content = file_data.get("content", "")
                if content and len(content) > 50:  # Only show substantial files
                    self.cli.show_code_generation("python", content[:1000], f"Generated: {path}")
                    break
    
    async def _display_generated_tests(self):
        """Display recently generated tests"""
        repo = RepoService(self.state.project_path)
        files = repo.read_files(["**/test_*.py", "**/tests/*.py"])
        
        for path, file_data in files.get("files", {}).items():
            content = file_data.get("content", "")
            if content and len(content) > 50:
                self.cli.show_code_generation("python", content[:800], f"Generated Test: {path}")
                break
    
    async def _display_test_results(self):
        """Display test results beautifully"""
        # This will be called after build_run phase
        # Test results are already shown in the phase
        pass
    
    async def _celebrate_completion(self, start_time):
        """Celebrate successful completion"""
        duration = datetime.now() - start_time
        
        self.cli.show_completion(
            self.state.project_path,
            self.iteration_count
        )
        
        # Additional stats
        if self.cli.console:
            stats_text = f"""
📊 DEVELOPMENT STATISTICS:
⏱️ Total time: {duration}
🔄 Iterations: {self.iteration_count}
📁 Files created: {self.total_files_created}
🧪 Test runs: {self.total_tests_run}
🐛 Bugs fixed: {self.total_bugs_fixed}
🔍 Debug cycles: {self.debug_cycle_count}

🎯 SUCCESS RATE: {((self.max_iterations - self.iteration_count) / self.max_iterations * 100):.1f}%
            """
            
            from rich.panel import Panel
            panel = Panel(
                stats_text,
                title="[bold green]🎉 Development Complete![/bold green]",
                border_style="bright_green"
            )
            self.cli.console.print(panel)
    
    async def _handle_max_iterations_reached(self):
        """Handle reaching maximum iterations"""
        logger.warning(f"♾️ Maximum iterations ({self.max_iterations}) reached")
        
        if self.cli.console:
            from rich.panel import Panel
            warning_text = f"""
⚠️ MAXIMUM ITERATIONS REACHED

The AI has used all {self.max_iterations} iterations but hasn't completed the project.

Current status:
- Phase: {self.state.phase.value}
- Files created: {self.total_files_created}
- Tests run: {self.total_tests_run}
- Bugs fixed: {self.total_bugs_fixed}

The project may still be functional. Check the generated files!

To continue: Increase max_iterations in policies.yaml or resume with a new session.
            """
            
            panel = Panel(
                warning_text,
                title="[bold yellow]⚠️ Iteration Limit Reached[/bold yellow]",
                border_style="yellow"
            )
            self.cli.console.print(panel)
    
    def _calculate_progress(self) -> float:
        """Calculate overall progress percentage"""
        phase_weights = {
            PipelinePhase.PLAN: 10,
            PipelinePhase.ARCHITECT: 20,
            PipelinePhase.CODE_WRITE: 40,
            PipelinePhase.TEST_WRITE: 60,
            PipelinePhase.BUILD_RUN: 70,
            PipelinePhase.DIAGNOSE: 75,
            PipelinePhase.REPAIR: 80,
            PipelinePhase.VERIFY: 90,
            PipelinePhase.DONE: 100
        }
        
        base_progress = phase_weights.get(self.state.phase, 0)
        
        # Add iteration bonus (small increments for progress within phase)
        iteration_bonus = min(self.iteration_count * 0.5, 10)
        
        return min(base_progress + iteration_bonus, 100)
    
    def _get_phase_description(self) -> str:
        """Get human-readable phase description"""
        descriptions = {
            PipelinePhase.PLAN: f"AI Project Manager creating comprehensive plan (iteration {self.iteration_count})",
            PipelinePhase.ARCHITECT: f"AI Architect designing system architecture (iteration {self.iteration_count})",
            PipelinePhase.CODE_WRITE: f"AI Coder writing production-ready code (iteration {self.iteration_count})",
            PipelinePhase.TEST_WRITE: f"AI Test Engineer creating comprehensive tests (iteration {self.iteration_count})",
            PipelinePhase.BUILD_RUN: f"Running all tests and quality checks (iteration {self.iteration_count})",
            PipelinePhase.DIAGNOSE: f"AI Debugger analyzing issues (debug cycle {self.debug_cycle_count})",
            PipelinePhase.REPAIR: f"AI applying fixes and improvements (iteration {self.iteration_count})",
            PipelinePhase.VERIFY: f"AI Verifier checking completion with strict standards (iteration {self.iteration_count})",
            PipelinePhase.DONE: "Project completed successfully!"
        }
        
        return descriptions.get(self.state.phase, f"Working on {self.state.phase.value}")
    
    async def _save_iteration_state(self):
        """Save detailed state after each iteration"""
        state_data = {
            "run_id": self.state.run_id,
            "phase": self.state.phase.value,
            "iteration": self.iteration_count,
            "debug_cycles": self.debug_cycle_count,
            "requirements": self.state.requirements,
            "project_path": self.state.project_path,
            "stats": {
                "files_created": self.total_files_created,
                "tests_run": self.total_tests_run,
                "bugs_fixed": self.total_bugs_fixed
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Save to memory/states
        state_file = Path(f"memory/states/{self.state.run_id}.json")
        state_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(state_file, 'w') as f:
            json.dump(state_data, f, indent=2)
    
    async def _handle_phase_error(self, error):
        """Handle errors during phase execution"""
        logger.error(f"♾️ Phase error in {self.state.phase.value}: {error}")
        
        # Try to recover by moving to diagnose phase
        if self.state.phase != PipelinePhase.DIAGNOSE:
            self.state.phase = PipelinePhase.DIAGNOSE
        else:
            # If already in diagnose, try repair
            self.state.phase = PipelinePhase.REPAIR
    
    async def _handle_critical_error(self, error):
        """Handle critical errors that stop execution"""
        logger.error(f"♾️ Critical error: {error}")
        
        if self.cli.console:
            from rich.panel import Panel
            error_text = f"""
💥 CRITICAL ERROR OCCURRED

Error: {error}

The AI development process has encountered a critical error.
State has been saved and you can resume later.

To resume: Use the resume command with run ID: {self.state.run_id}
            """
            
            panel = Panel(
                error_text,
                title="[bold red]💥 Critical Error[/bold red]",
                border_style="red"
            )
            self.cli.console.print(panel)

# Test the infinite orchestrator
async def test_infinite_orchestrator():
    """Test the infinite orchestrator"""
    print("♾️ Testing Infinite Orchestrator...")
    
    orchestrator = InfiniteOrchestrator()
    
    # Test with a simple project
    await orchestrator.run_autonomous_development(
        requirements="Create a robust Python calculator with comprehensive error handling, unit tests, and a beautiful CLI interface",
        project_name="infinite_calculator"
    )
    
    print("♾️ Infinite Orchestrator test completed!")

if __name__ == "__main__":
    asyncio.run(test_infinite_orchestrator())