#!/usr/bin/env python3
"""
📋 JSON Schemas - Tool Calling & Response Validation
Phase B: Structured AI communication

Defines all JSON schemas for AI actors and tool interactions.
"""

import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ToolCallSchema:
    """Schema for a tool call from AI"""
    name: str
    parameters: Dict[str, Any]

@dataclass
class AIActorResponse:
    """Structured response from an AI actor"""
    reasoning: str
    tool_calls: List[ToolCallSchema]
    confidence: float = 1.0
    next_steps: List[str] = None

class SchemaValidator:
    """Validates AI responses against expected schemas"""
    
    def __init__(self):
        self.schemas = self._load_schemas()
    
    def validate_ai_response(self, response_text: str, expected_format: str = "tool_calling") -> Dict[str, Any]:
        """
        Validate and parse AI response
        
        Args:
            response_text: Raw response from AI
            expected_format: Expected response format
            
        Returns:
            Parsed and validated response
        """
        try:
            # Try to extract JSON from response
            json_data = self._extract_json(response_text)
            
            if json_data:
                # Validate against schema
                if expected_format == "tool_calling":
                    return self._validate_tool_calling_response(json_data)
                elif expected_format == "plan":
                    return self._validate_plan_response(json_data)
                elif expected_format == "architecture":
                    return self._validate_architecture_response(json_data)
            
            # Fallback: treat as plain text
            return {
                "success": True,
                "type": "text",
                "content": response_text,
                "reasoning": response_text,
                "tool_calls": []
            }
            
        except Exception as e:
            logger.error(f"📋 Schema validation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "raw_response": response_text
            }
    
    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from AI response text"""
        # Look for JSON blocks
        import re
        
        # Try to find JSON in code blocks
        json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        matches = re.findall(json_pattern, text, re.DOTALL)
        
        if matches:
            try:
                return json.loads(matches[0])
            except json.JSONDecodeError:
                pass
        
        # Try to find JSON without code blocks
        json_pattern = r'(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})'
        matches = re.findall(json_pattern, text, re.DOTALL)
        
        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue
        
        return None
    
    def _validate_tool_calling_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate tool calling response format"""
        result = {
            "success": True,
            "type": "tool_calling",
            "reasoning": data.get("reasoning", ""),
            "tool_calls": []
        }
        
        # Validate tool calls
        tool_calls = data.get("tool_calls", [])
        for call in tool_calls:
            if isinstance(call, dict) and "name" in call and "parameters" in call:
                result["tool_calls"].append({
                    "name": call["name"],
                    "parameters": call["parameters"]
                })
            else:
                logger.warning(f"📋 Invalid tool call format: {call}")
        
        return result
    
    def _validate_plan_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate project plan response"""
        return {
            "success": True,
            "type": "plan",
            "plan": data.get("plan", ""),
            "milestones": data.get("milestones", []),
            "acceptance_tests": data.get("acceptance_tests", []),
            "repo_layout": data.get("repo_layout", []),
            "risks": data.get("risks", [])
        }
    
    def _validate_architecture_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate architecture response"""
        return {
            "success": True,
            "type": "architecture",
            "pattern": data.get("pattern", ""),
            "components": data.get("components", []),
            "interfaces": data.get("interfaces", []),
            "tech_stack": data.get("tech_stack", {}),
            "scaffold": data.get("scaffold", [])
        }
    
    def _load_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Load all JSON schemas"""
        return {
            "tool_calling": {
                "type": "object",
                "properties": {
                    "reasoning": {"type": "string"},
                    "tool_calls": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "parameters": {"type": "object"}
                            },
                            "required": ["name", "parameters"]
                        }
                    }
                },
                "required": ["reasoning", "tool_calls"]
            },
            
            "project_plan": {
                "type": "object",
                "properties": {
                    "plan": {"type": "string"},
                    "milestones": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "acceptance_tests": {
                        "type": "array", 
                        "items": {"type": "string"}
                    },
                    "repo_layout": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "path": {"type": "string"},
                                "purpose": {"type": "string"}
                            }
                        }
                    }
                }
            },
            
            "architecture": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string"},
                    "components": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "purpose": {"type": "string"},
                                "responsibilities": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                }
                            }
                        }
                    },
                    "tech_stack": {"type": "object"}
                }
            }
        }

# AI Actor Response Templates
class ResponseTemplates:
    """Templates for AI actor responses"""
    
    @staticmethod
    def pm_response_template() -> str:
        """Template for Project Manager responses"""
        return """
Analyze the requirements and create a comprehensive project plan.

Respond in this JSON format:
{
  "reasoning": "Your analysis of the requirements and planning decisions",
  "plan": "Overall project description and approach",
  "milestones": [
    "Milestone 1: Description",
    "Milestone 2: Description"
  ],
  "acceptance_tests": [
    "Test 1: Specific acceptance criteria",
    "Test 2: Specific acceptance criteria"
  ],
  "repo_layout": [
    {"path": "src/main.py", "purpose": "Application entry point"},
    {"path": "tests/", "purpose": "Test files"}
  ],
  "risks": [
    "Risk 1: Description and mitigation",
    "Risk 2: Description and mitigation"
  ],
  "tool_calls": [
    {
      "name": "repo_write",
      "parameters": {
        "edits": [
          {
            "path": "README.md",
            "mode": "create",
            "content": "Project README content"
          }
        ],
        "message": "Initial project structure"
      }
    }
  ]
}
"""
    
    @staticmethod
    def architect_response_template() -> str:
        """Template for Architect responses"""
        return """
Design the software architecture for this project.

Respond in this JSON format:
{
  "reasoning": "Your architectural decisions and rationale",
  "pattern": "Architectural pattern name (e.g., MVC, microservices)",
  "components": [
    {
      "name": "ComponentName",
      "purpose": "What this component does",
      "responsibilities": ["Responsibility 1", "Responsibility 2"],
      "interfaces": ["Interface 1", "Interface 2"]
    }
  ],
  "tech_stack": {
    "language": "python",
    "framework": "fastapi",
    "database": "sqlite",
    "testing": "pytest"
  },
  "tool_calls": [
    {
      "name": "repo_write",
      "parameters": {
        "edits": [
          {
            "path": "src/architecture.md",
            "mode": "create",
            "content": "Architecture documentation"
          }
        ],
        "message": "Add architecture documentation"
      }
    }
  ]
}
"""
    
    @staticmethod
    def coder_response_template() -> str:
        """Template for Coder responses"""
        return """
Implement the requested functionality with clean, working code.

Respond in this JSON format:
{
  "reasoning": "Your implementation approach and decisions",
  "implementation_notes": "Key aspects of the implementation",
  "tool_calls": [
    {
      "name": "repo_write",
      "parameters": {
        "edits": [
          {
            "path": "src/module.py",
            "mode": "create",
            "content": "Complete working code here"
          }
        ],
        "message": "Implement [feature description]"
      }
    }
  ]
}
"""

# Test the schema validator
def test_schema_validator():
    """Test the schema validator"""
    print("🧪 Testing Schema Validator...")
    
    validator = SchemaValidator()
    
    # Test valid tool calling response
    valid_response = """
    Looking at this requirement, I need to create a basic structure.
    
    ```json
    {
      "reasoning": "Creating initial project structure",
      "tool_calls": [
        {
          "name": "repo_write",
          "parameters": {
            "edits": [{"path": "main.py", "mode": "create", "content": "print('hello')"}],
            "message": "Initial file"
          }
        }
      ]
    }
    ```
    """
    
    result = validator.validate_ai_response(valid_response)
    print(f"✅ Valid response: success={result['success']}")
    print(f"   Tool calls: {len(result.get('tool_calls', []))}")
    
    # Test invalid response
    invalid_response = "This is just plain text without JSON"
    result = validator.validate_ai_response(invalid_response)
    print(f"✅ Plain text response: success={result['success']}, type={result.get('type')}")
    
    print("🧪 Schema Validator test completed!")

if __name__ == "__main__":
    test_schema_validator()