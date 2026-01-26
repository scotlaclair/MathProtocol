"""
MCP Server for MathProtocol

This module exposes MathProtocol as a native tool for AI agents via the
Model Context Protocol (MCP). AI agents can use MathProtocol to constrain
their outputs to deterministic mathematical codes.

MCP Spec: https://modelcontextprotocol.io/
"""

import sys
import os
import json
from typing import Any, Dict

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from mathprotocol import MathProtocol, MockLLM


class MCPServer:
    """
    MCP Server for MathProtocol.
    
    Exposes three tools:
    1. validate_input - Check if input matches protocol
    2. parse_input - Parse input into components
    3. process_request - Full processing pipeline
    """
    
    def __init__(self):
        self.protocol = MathProtocol()
        self.llm = MockLLM()
        
        # Tool definitions per MCP spec
        self.tools = {
            "validate_mathprotocol_input": {
                "description": "Validate if input matches MathProtocol format (TASK-PARAM | CONTEXT)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "input": {
                            "type": "string",
                            "description": "The input string to validate"
                        }
                    },
                    "required": ["input"]
                }
            },
            "parse_mathprotocol_input": {
                "description": "Parse MathProtocol input into task, param, and context",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "input": {
                            "type": "string",
                            "description": "The input string to parse"
                        }
                    },
                    "required": ["input"]
                }
            },
            "process_mathprotocol_request": {
                "description": "Process a complete MathProtocol request and return response",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "input": {
                            "type": "string",
                            "description": "The MathProtocol input (TASK-PARAM | CONTEXT)"
                        }
                    },
                    "required": ["input"]
                }
            },
            "get_mathprotocol_tasks": {
                "description": "Get list of available MathProtocol tasks",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        }
    
    def list_tools(self) -> Dict[str, Any]:
        """
        List all available tools (MCP tools/list endpoint).
        
        Returns:
            Dictionary of tool definitions
        """
        return {"tools": [
            {"name": name, **definition}
            for name, definition in self.tools.items()
        ]}
    
    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool by name (MCP tools/call endpoint).
        
        Args:
            name: Tool name
            arguments: Tool arguments
            
        Returns:
            Tool result
        """
        if name == "validate_mathprotocol_input":
            return self._validate_input(arguments["input"])
        
        elif name == "parse_mathprotocol_input":
            return self._parse_input(arguments["input"])
        
        elif name == "process_mathprotocol_request":
            return self._process_request(arguments["input"])
        
        elif name == "get_mathprotocol_tasks":
            return self._get_tasks()
        
        else:
            return {"error": f"Unknown tool: {name}"}
    
    def _validate_input(self, input_str: str) -> Dict[str, Any]:
        """Validate input format."""
        is_valid = self.protocol.validate_input(input_str)
        
        if is_valid:
            parsed = self.protocol.parse_input(input_str)
            return {
                "valid": True,
                "task": parsed['task'],
                "task_name": self.protocol.get_task_name(parsed['task']),
                "param": parsed['param'],
                "param_name": self.protocol.get_param_name(parsed['param'])
            }
        else:
            return {
                "valid": False,
                "error": "Invalid format. Expected: TASK-PARAM | CONTEXT"
            }
    
    def _parse_input(self, input_str: str) -> Dict[str, Any]:
        """Parse input into components."""
        parsed = self.protocol.parse_input(input_str)
        
        if parsed is None:
            return {"error": "Failed to parse input"}
        
        return {
            "task_code": parsed['task'],
            "task_name": self.protocol.get_task_name(parsed['task']),
            "param_code": parsed['param'],
            "param_name": self.protocol.get_param_name(parsed['param']),
            "context": parsed['context']
        }
    
    def _process_request(self, input_str: str) -> Dict[str, Any]:
        """Process complete request."""
        # Validate
        if not self.protocol.validate_input(input_str):
            return {"error": "Invalid input format"}
        
        # Process
        try:
            response = self.llm.process(input_str)
            parsed_response = self.protocol.parse_response(response)
            
            # Parse input for validation
            parsed_input = self.protocol.parse_input(input_str)
            is_valid_response = self.protocol.validate_response(
                response, 
                parsed_input['task']
            )
            
            return {
                "input": input_str,
                "output": response,
                "response_codes": parsed_response['codes'],
                "response_payload": parsed_response['payload'],
                "valid_response": is_valid_response
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _get_tasks(self) -> Dict[str, Any]:
        """Get list of available tasks."""
        return {
            "tasks": {
                code: {
                    "name": name,
                    "code": code,
                    "type": "classification" if code in self.protocol.CLASSIFICATION_TASKS else "generative"
                }
                for code, name in self.protocol.TASKS.items()
            },
            "parameters": {
                code: name
                for code, name in self.protocol.PARAMS.items()
            }
        }


def start_stdio_server():
    """
    Start MCP server in STDIO mode.
    
    Reads JSON-RPC requests from stdin and writes responses to stdout.
    This is the standard MCP transport protocol.
    """
    server = MCPServer()
    
    print("MathProtocol MCP Server started (STDIO mode)", file=sys.stderr)
    print("Waiting for requests...", file=sys.stderr)
    
    while True:
        try:
            # Read JSON-RPC request from stdin
            line = sys.stdin.readline()
            if not line:
                break
            
            request = json.loads(line)
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")
            
            # Handle request
            if method == "tools/list":
                result = server.list_tools()
            
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                result = server.call_tool(tool_name, arguments)
            
            else:
                result = {"error": f"Unknown method: {method}"}
            
            # Write JSON-RPC response to stdout
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }
            
            print(json.dumps(response), flush=True)
            
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": request.get("id") if 'request' in locals() else None,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
            print(json.dumps(error_response), flush=True)


def test_mcp_server():
    """Test MCP server locally."""
    server = MCPServer()
    
    print("=" * 60)
    print("MCP Server Test")
    print("=" * 60)
    
    # Test 1: List tools
    print("\n[TEST 1] List Tools")
    tools = server.list_tools()
    print(f"Available tools: {len(tools['tools'])}")
    for tool in tools['tools']:
        print(f"  - {tool['name']}")
    
    # Test 2: Validate input
    print("\n[TEST 2] Validate Input")
    result = server.call_tool("validate_mathprotocol_input", {
        "input": "2-1 | Great product!"
    })
    print(f"Valid: {result['valid']}")
    print(f"Task: {result.get('task_name')}")
    
    # Test 3: Parse input
    print("\n[TEST 3] Parse Input")
    result = server.call_tool("parse_mathprotocol_input", {
        "input": "17-1 | Hello World"
    })
    print(f"Task: {result['task_name']} ({result['task_code']})")
    print(f"Param: {result['param_name']} ({result['param_code']})")
    print(f"Context: {result['context']}")
    
    # Test 4: Process request
    print("\n[TEST 4] Process Request")
    result = server.call_tool("process_mathprotocol_request", {
        "input": "2-1 | This is amazing!"
    })
    print(f"Output: {result['output']}")
    print(f"Valid Response: {result['valid_response']}")
    
    # Test 5: Get tasks
    print("\n[TEST 5] Get Tasks")
    result = server.call_tool("get_mathprotocol_tasks", {})
    print(f"Total tasks: {len(result['tasks'])}")
    print(f"Total params: {len(result['parameters'])}")
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_mcp_server()
    else:
        start_stdio_server()
