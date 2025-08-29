#!/usr/bin/env python3
"""
🧠 Model Client - AI Integration Layer
Phase B: Connect your 30B model to the autonomous system

Integrates with your existing Qwen3-Coder 30B model via Ollama.
"""

import json
import asyncio
import requests
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging
import time

logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    """Configuration for the AI model"""
    host: str = "http://172.26.240.1:11434"
    model_name: str = "qwen3-coder:30b-a3b-q4_K_M"
    timeout: int = None  # No timeout - let it think as long as needed
    max_retries: int = 1

@dataclass
class AIResponse:
    """Response from AI model"""
    success: bool
    content: str
    tokens_used: int = 0
    execution_time: float = 0.0
    error: Optional[str] = None
    retry_count: int = 0

class ModelClient:
    """
    Client for interacting with your 30B model via Ollama.
    
    Handles role-based prompting, JSON function calling, and retries.
    """
    
    def __init__(self, config: ModelConfig = None):
        self.config = config or ModelConfig()
        self.session = requests.Session()
        
        # Role-specific system prompts (from the blueprint)
        self.role_prompts = self._load_role_prompts()
        
        logger.info(f"🧠 Model client initialized: {self.config.model_name}")
    
    async def call_ai_actor(
        self, 
        role: str, 
        user_message: str, 
        context: Dict[str, Any] = None,
        tools: List[Dict] = None,
        temperature: float = None
    ) -> AIResponse:
        """
        Call an AI actor with role-specific prompting
        
        Args:
            role: AI actor role (pm, architect, coder, test_engineer, debugger, verifier)
            user_message: The main message/task for the AI
            context: Additional context (project info, previous results, etc.)
            tools: Available tools for function calling
            temperature: Override default temperature for this role
            
        Returns:
            AIResponse with the AI's response
        """
        start_time = time.time()
        
        # Get role-specific system prompt
        system_prompt = self.role_prompts.get(role, self.role_prompts["default"])
        
        # Build full prompt with context
        full_prompt = self._build_prompt(system_prompt, user_message, context, tools)
        
        # Get role-specific temperature
        if temperature is None:
            temperature = self._get_role_temperature(role)
        
        # Make the API call with retries
        for attempt in range(self.config.max_retries):
            try:
                logger.info(f"🧠 Calling {role} actor (attempt {attempt + 1})")
                
                response = await self._make_ollama_request(full_prompt, temperature)
                
                if response.success:
                    response.execution_time = time.time() - start_time
                    response.retry_count = attempt
                    logger.info(f"🧠 {role} actor responded successfully in {response.execution_time:.2f}s")
                    return response
                else:
                    logger.warning(f"🧠 {role} actor failed (attempt {attempt + 1}): {response.error}")
                    if attempt == self.config.max_retries - 1:
                        return response
                    
                    # Wait before retry
                    await asyncio.sleep(2 ** attempt)
                    
            except Exception as e:
                logger.error(f"🧠 Error calling {role} actor: {e}")
                if attempt == self.config.max_retries - 1:
                    return AIResponse(
                        success=False,
                        content="",
                        error=str(e),
                        execution_time=time.time() - start_time,
                        retry_count=attempt
                    )
        
        return AIResponse(success=False, content="", error="Max retries exceeded")
    
    async def _make_ollama_request(self, prompt: str, temperature: float) -> AIResponse:
        """Make request to Ollama API or return mock response"""
        
        try:
            payload = {
                "model": self.config.model_name,
                "prompt": prompt,
                "stream": True,  # Enable streaming for real-time updates
                "options": {
                    "temperature": temperature,
                    "top_p": 0.9,
                    "max_tokens": 4000
                }
            }
            
            # Stream the response to show progress
            print(f"🧠 AI is thinking... (using {self.config.model_name})")
            
            response = requests.post(
                f"{self.config.host}/api/generate",
                json=payload,
                timeout=None,  # No timeout
                stream=True  # Stream for real-time updates
            )
            
            if response.status_code == 200:
                full_content = ""
                tokens_used = 0
                
                # Process streaming response
                for line in response.iter_lines():
                    if line:
                        try:
                            chunk = json.loads(line.decode('utf-8'))
                            if 'response' in chunk:
                                new_text = chunk['response']
                                full_content += new_text
                                
                                # Show progress every few tokens
                                if len(full_content) % 100 == 0:
                                    print(f"🔄 Generated {len(full_content)} characters...")
                                
                                # Show code snippets as they're generated
                                if any(keyword in new_text for keyword in ['def ', 'class ', 'import ', 'from ', 'if __name__', '#!/usr/bin']):
                                    print(f"💡 AI is writing: {new_text.strip()}")
                                
                                # Show when AI is creating files
                                if '"path":' in new_text and '.py' in new_text:
                                    print(f"📄 AI is creating a file: {new_text.strip()}")
                                
                                # Show progress every 50 characters instead of 100
                                if len(full_content) % 50 == 0 and len(full_content) > 0:
                                    print(f"🔄 Generated {len(full_content)} characters... Latest: {new_text[-20:].strip()}")
                            
                            if chunk.get('done', False):
                                tokens_used = chunk.get('eval_count', 0)
                                print(f"✅ AI finished! Generated {len(full_content)} characters, {tokens_used} tokens")
                                break
                                
                        except json.JSONDecodeError:
                            continue
                
                return AIResponse(
                    success=True,
                    content=full_content,
                    tokens_used=tokens_used
                )
            else:
                return AIResponse(
                    success=False,
                    content="",
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                
        except requests.exceptions.Timeout:
            return AIResponse(
                success=False,
                content="",
                error="Request timed out"
            )
        except Exception as e:
            return AIResponse(
                success=False,
                content="",
                error=str(e)
            )
    
    def _generate_mock_response(self, prompt: str) -> AIResponse:
        """Generate mock AI responses for testing"""
        import time
        import random
        
        # Simulate processing time
        time.sleep(random.uniform(0.5, 2.0))
        
        # Generate role-appropriate mock responses
        if "Project Manager" in prompt or "requirements" in prompt.lower():
            content = """# Project Plan: Hello World Script

## Milestones
1. **Setup** - Create project structure
2. **Implementation** - Write hello.py script  
3. **Testing** - Add unit tests
4. **Documentation** - Add README

## File Structure
```
hello_world/
├── hello.py          # Main script
├── test_hello.py     # Unit tests  
├── README.md         # Documentation
└── requirements.txt  # Dependencies
```

## Acceptance Tests
- Script runs without errors
- Outputs "Hello, World!" exactly
- Tests pass with 100% coverage"""

        elif "architect" in prompt.lower() or "architecture" in prompt.lower():
            content = """# Architecture Design

## Technology Stack
- **Language**: Python 3.8+
- **Testing**: pytest
- **Structure**: Simple script-based

## Module Design
```python
# hello.py - Main module
def main():
    print("Hello, World!")

if __name__ == "__main__":
    main()
```

## Dependencies
- No external dependencies required
- Standard library only"""

        elif "test" in prompt.lower():
            content = """# Test Implementation

```python
# test_hello.py
import hello

def test_hello_output(capsys):
    hello.main()
    captured = capsys.readouterr()
    assert captured.out.strip() == "Hello, World!"

def test_main_function_exists():
    assert hasattr(hello, 'main')
    assert callable(hello.main)
```"""

        elif "coder" in prompt.lower() or "implement" in prompt.lower():
            content = """# Implementation

```python
#!/usr/bin/env python3
\"\"\"
Simple Hello World script
\"\"\"

def main():
    \"\"\"Print Hello, World! to stdout\"\"\"
    print("Hello, World!")

if __name__ == "__main__":
    main()
```"""

        else:
            content = "Mock AI response generated for testing purposes."
        
        return AIResponse(
            success=True,
            content=content,
            tokens_used=random.randint(50, 200)
        )
    
    def _build_prompt(
        self, 
        system_prompt: str, 
        user_message: str, 
        context: Dict[str, Any] = None,
        tools: List[Dict] = None
    ) -> str:
        """Build the complete prompt for the AI"""
        
        prompt_parts = [system_prompt]
        
        # Add context if provided
        if context:
            prompt_parts.append("\n=== CONTEXT ===")
            for key, value in context.items():
                prompt_parts.append(f"{key}: {value}")
        
        # Add available tools if provided
        if tools:
            prompt_parts.append("\n=== AVAILABLE TOOLS ===")
            for tool in tools:
                prompt_parts.append(f"- {tool['name']}: {tool['description']}")
                prompt_parts.append(f"  Parameters: {json.dumps(tool['parameters'], indent=2)}")
        
        # Add the main user message
        prompt_parts.append(f"\n=== TASK ===\n{user_message}")
        
        # Add output format instructions
        if tools:
            prompt_parts.append("""
=== OUTPUT FORMAT ===
Respond with your analysis and then any tool calls in this JSON format:
{
  "reasoning": "Your thought process and analysis",
  "tool_calls": [
    {
      "name": "tool_name",
      "parameters": {
        "param1": "value1",
        "param2": "value2"
      }
    }
  ]
}

If no tools are needed, use an empty tool_calls array.
""")
        
        return "\n".join(prompt_parts)
    
    def _get_role_temperature(self, role: str) -> float:
        """Get temperature setting for specific role"""
        temperatures = {
            "pm": 0.3,
            "architect": 0.4,
            "coder": 0.2,
            "test_engineer": 0.3,
            "debugger": 0.3,
            "verifier": 0.0
        }
        return temperatures.get(role, 0.3)
    
    def _load_role_prompts(self) -> Dict[str, str]:
        """Load role-specific system prompts"""
        return {
            "pm": """You are a Project Manager AI. Your job is to analyze requirements and create a comprehensive project plan.

CRITICAL RULES - NEVER VIOLATE:
- NEVER plan for demo functionality or example code
- NEVER include sample data or mock content in plans
- ONLY plan for the core functionality requested

You should:
1. Break down requirements into clear, actionable milestones
2. Define acceptance tests that verify the project works
3. Identify potential risks and constraints
4. Create a logical file structure for the project
5. Set realistic scope and avoid feature creep

Output a detailed plan with milestones, acceptance tests, and file structure - no demos or examples.""",

            "architect": """You are a Software Architect AI. Your job is to design robust, scalable software architecture.

CRITICAL RULES - NEVER VIOLATE:
- NEVER design demo or example components
- NEVER include sample data structures
- ONLY design the core architecture requested

You should:
1. Choose appropriate architectural patterns (MVC, microservices, etc.)
2. Define module boundaries and interfaces
3. Select appropriate technologies and frameworks
4. Design data models and database schemas
5. Plan for scalability, security, and maintainability
6. Create scaffolding and boilerplate code

Design architecture that follows best practices and is appropriate for the project scope - no demos or examples.""",

            "coder": """You are a Senior Developer AI. Your job is to write clean, working code.

CRITICAL RULES - NEVER VIOLATE:
- NEVER create demo functions, example usage, or sample code
- NEVER add main() functions with demonstrations
- NEVER include test examples in production code
- NEVER create mock data or placeholder content
- NEVER add "if __name__ == '__main__'" demo blocks
- ONLY write the core functionality requested

You should:
1. Implement ONLY the core features requested - nothing extra
2. Write production-ready code with proper error handling
3. Follow coding best practices and conventions
4. Add meaningful comments and docstrings for the actual functionality
5. Ensure code is testable and maintainable
6. Use appropriate design patterns

Write complete, functional code that actually works - no placeholders, TODOs, demos, or examples.""",

            "test_engineer": """You are a Test Engineer AI. Your job is to create comprehensive tests.

CRITICAL RULES - NEVER VIOLATE:
- NEVER create demo test data or example scenarios
- NEVER add sample usage in test files
- NEVER create mock implementations in tests
- ONLY write actual test cases that verify functionality

You should:
1. Write unit tests for all functions and classes
2. Create integration tests for component interactions
3. Design acceptance tests based on requirements
4. Add property-based tests for edge cases
5. Ensure tests are deterministic and reliable
6. Achieve good test coverage

Create tests that actually verify the code works correctly - no demos or examples.""",

            "debugger": """You are a Debugger AI. Your job is to find and fix bugs.

You should:
1. Analyze error messages and stack traces
2. Identify the root cause of failures
3. Propose minimal fixes that address the issue
4. Add regression tests to prevent the bug from recurring
5. Consider edge cases and potential side effects

Provide precise, minimal patches that fix the actual problem.""",

            "verifier": """You are a Verifier AI. Your job is to decide if the project is complete and working.

You should:
1. Check that all tests pass
2. Verify code coverage meets requirements
3. Ensure static analysis passes (linting, type checking)
4. Confirm acceptance criteria are met
5. Validate that the project actually works as specified

Only approve completion when the project truly meets all requirements.""",

            "default": """You are a helpful AI assistant focused on software development. Provide clear, accurate, and actionable responses."""
        }

# Test the model client
async def test_model_client():
    """Test the model client"""
    print("🧪 Testing Model Client...")
    
    client = ModelClient()
    
    # Test simple PM call
    response = await client.call_ai_actor(
        role="pm",
        user_message="Create a plan for building a simple calculator app",
        context={"language": "python", "complexity": "simple"}
    )
    
    print(f"✅ PM Response: success={response.success}")
    if response.success:
        print(f"   Content preview: {response.content[:200]}...")
        print(f"   Execution time: {response.execution_time:.2f}s")
    else:
        print(f"   Error: {response.error}")
    
    print("🧪 Model Client test completed!")

if __name__ == "__main__":
    asyncio.run(test_model_client())