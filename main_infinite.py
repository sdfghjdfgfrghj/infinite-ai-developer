#!/usr/bin/env python3
"""
♾️ Infinite AI Developer - Main Entry Point
The ultimate autonomous AI that can iterate forever until perfection!

This integrates the beautiful CLI with infinite iterations.
"""

import asyncio
import argparse
import sys
from pathlib import Path
import logging

# Add project to path
sys.path.append(str(Path(__file__).parent))

from orchestrator.infinite_orchestrator import InfiniteOrchestrator
from ui.beautiful_cli import beautiful_cli

# Set up beautiful logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Main CLI interface for infinite AI development"""
    
    parser = argparse.ArgumentParser(
        description="♾️ Infinite AI Developer - Build perfect software with unlimited iterations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main_infinite.py build "Create a robust task manager with user auth and real-time updates"
  python main_infinite.py build "Build a complete e-commerce API with payment processing"
  python main_infinite.py resume run-abc123
  python main_infinite.py status run-abc123
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Build command
    build_parser = subparsers.add_parser('build', help='Build a project with infinite iterations')
    build_parser.add_argument('requirements', help='Natural language description of what to build')
    build_parser.add_argument('--project', '-p', help='Project name (auto-generated if not provided)')
    build_parser.add_argument('--max-iterations', '-i', type=int, default=1000, help='Maximum iterations (default: 1000)')
    
    # Resume command
    resume_parser = subparsers.add_parser('resume', help='Resume a previous infinite run')
    resume_parser.add_argument('run_id', help='Run ID to resume')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Check status of an infinite run')
    status_parser.add_argument('run_id', help='Run ID to check')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test the infinite orchestrator')
    test_parser.add_argument('--simple', action='store_true', help='Run a simple test project')
    
    args = parser.parse_args()
    
    if not args.command:
        # Show beautiful banner and help
        beautiful_cli.show_banner()
        parser.print_help()
        return
    
    try:
        if args.command == 'build':
            await handle_build_command(args)
        elif args.command == 'resume':
            await handle_resume_command(args)
        elif args.command == 'status':
            await handle_status_command(args)
        elif args.command == 'test':
            await handle_test_command(args)
            
    except KeyboardInterrupt:
        print("\n⏸️ Development paused by user - state saved!")
    except Exception as e:
        print(f"\n💥 Error: {e}")
        logger.exception("Unexpected error occurred")

async def handle_build_command(args):
    """Handle the infinite build command"""
    
    # Generate project name if not provided
    project_name = args.project
    if not project_name:
        import re
        from datetime import datetime
        # Create project name from requirements
        clean_req = re.sub(r'[^a-zA-Z0-9\s]', '', args.requirements.lower())
        words = clean_req.split()[:3]  # First 3 words
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_name = f"{'_'.join(words)}_{timestamp}"
    
    print(f"♾️ Starting infinite autonomous development...")
    print(f"📝 Requirements: {args.requirements}")
    print(f"📁 Project: {project_name}")
    print(f"🔄 Max iterations: {args.max_iterations}")
    print(f"🎯 Goal: Perfect, production-ready application!")
    
    # Initialize the infinite orchestrator
    orchestrator = InfiniteOrchestrator()
    
    # Override max iterations if specified
    if args.max_iterations != 1000:
        orchestrator.max_iterations = args.max_iterations
    
    # Start infinite autonomous development
    result = await orchestrator.run_autonomous_development(
        requirements=args.requirements,
        project_name=project_name
    )
    
    # Show final results
    if result.phase.value == "DONE":
        print(f"\n🎉 PERFECT APPLICATION COMPLETED!")
        print(f"📁 Location: {result.project_path}")
        print(f"🔄 Total iterations: {orchestrator.iteration_count}")
        print(f"🧪 Tests run: {orchestrator.total_tests_run}")
        print(f"🐛 Bugs fixed: {orchestrator.total_bugs_fixed}")
        
        print(f"\n🚀 YOUR APPLICATION IS READY:")
        print(f"1. cd {result.project_path}")
        print(f"2. pip install -r requirements.txt")
        print(f"3. python main.py")
        print(f"\n✨ Enjoy your AI-built, production-ready application!")
    else:
        print(f"\n⏸️ Development paused at {result.phase.value}")
        print(f"🔄 Iterations used: {orchestrator.iteration_count}/{orchestrator.max_iterations}")
        print(f"🔄 Run ID: {result.run_id} (use 'resume' to continue)")

async def handle_resume_command(args):
    """Handle the resume command"""
    print(f"♾️ Resuming infinite development: {args.run_id}")
    
    orchestrator = InfiniteOrchestrator()
    
    try:
        result = await orchestrator.run_autonomous_development(
            requirements="",  # Will be loaded from state
            project_name="",  # Will be loaded from state
            resume_run_id=args.run_id
        )
        
        print(f"✅ Resume completed - final phase: {result.phase.value}")
        
    except FileNotFoundError:
        print(f"❌ Run ID {args.run_id} not found")
    except Exception as e:
        print(f"❌ Resume failed: {e}")

async def handle_status_command(args):
    """Handle the status command"""
    print(f"📊 Checking infinite development status: {args.run_id}")
    
    try:
        import json
        state_file = Path(f"memory/states/{args.run_id}.json")
        
        if state_file.exists():
            with open(state_file, 'r') as f:
                state = json.load(f)
            
            print(f"📁 Project: {state.get('project_path', 'Unknown')}")
            print(f"🔄 Phase: {state.get('phase', 'Unknown')}")
            print(f"🔢 Iteration: {state.get('iteration', 0)}")
            print(f"🐛 Debug cycles: {state.get('debug_cycles', 0)}")
            print(f"📝 Requirements: {state.get('requirements', 'Unknown')}")
            
            stats = state.get('stats', {})
            print(f"📊 Files created: {stats.get('files_created', 0)}")
            print(f"🧪 Tests run: {stats.get('tests_run', 0)}")
            print(f"🔧 Bugs fixed: {stats.get('bugs_fixed', 0)}")
            
            timestamp = state.get('timestamp', 'Unknown')
            print(f"⏰ Last update: {timestamp}")
        else:
            print(f"❌ Run ID {args.run_id} not found")
            
    except Exception as e:
        print(f"❌ Status check failed: {e}")

async def handle_test_command(args):
    """Handle the test command"""
    print(f"🧪 Testing Infinite AI Orchestrator...")
    
    orchestrator = InfiniteOrchestrator()
    
    if args.simple:
        # Simple test project
        await orchestrator.run_autonomous_development(
            requirements="Create a simple Python calculator with error handling and tests",
            project_name="test_simple_calc"
        )
    else:
        # More complex test project
        await orchestrator.run_autonomous_development(
            requirements="Create a robust task management CLI application with file persistence, user authentication, and comprehensive testing",
            project_name="test_complex_app"
        )
    
    print("🧪 Infinite orchestrator test completed!")

if __name__ == "__main__":
    asyncio.run(main())