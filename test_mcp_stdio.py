#!/usr/bin/env python3
"""
Test script for Zendesk MCP Server via Docker stdio.

This script tests the MCP protocol communication over stdio by:
1. Sending an initialization request
2. Listing available tools
3. Listing available prompts
4. Listing available resources

Usage:
    python test_mcp_stdio.py

Or with Docker:
    docker run --rm -i --env-file .env zendesk-mcp-server < test_commands.json
"""

import json
import subprocess
import sys
from typing import Dict, Any


def send_mcp_request(method: str, params: Dict[str, Any] = None, request_id: int = 1) -> Dict[str, Any]:
    """Send an MCP JSON-RPC request and return the response."""
    request = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method,
    }
    if params:
        request["params"] = params
    
    return request


def test_mcp_server():
    """Test the MCP server via Docker stdio."""
    
    # Check if .env file exists
    import os
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    if not os.path.exists(env_file):
        print("Warning: .env file not found. The server may fail without Zendesk credentials.")
        print("Create a .env file with:")
        print("  ZENDESK_SUBDOMAIN=your-subdomain")
        print("  ZENDESK_EMAIL=your-email@example.com")
        print("  ZENDESK_API_KEY=your-api-token")
        print()
    
    # Prepare Docker command
    docker_cmd = [
        "docker", "run", "--rm", "-i"
    ]
    
    if os.path.exists(env_file):
        docker_cmd.extend(["--env-file", env_file])
    
    docker_cmd.append("zendesk-mcp-server")
    
    print(f"Starting Docker container: {' '.join(docker_cmd)}")
    print("=" * 60)
    
    try:
        # Start the Docker container
        process = subprocess.Popen(
            docker_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0
        )
        
        # Send initialization request
        print("\n1. Sending initialization request...")
        init_request = send_mcp_request(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            },
            request_id=1
        )
        
        request_json = json.dumps(init_request) + "\n"
        print(f"Sent: {request_json.strip()}")
        process.stdin.write(request_json)
        process.stdin.flush()
        
        # Read initialization response
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print(f"Received: {json.dumps(response, indent=2)}")
            
            if "result" in response:
                print("✓ Initialization successful!")
            else:
                print("✗ Initialization failed!")
                print(f"Error: {response.get('error', 'Unknown error')}")
                return
        
        # Send initialized notification
        print("\n2. Sending initialized notification...")
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        notification_json = json.dumps(initialized_notification) + "\n"
        print(f"Sent: {notification_json.strip()}")
        process.stdin.write(notification_json)
        process.stdin.flush()
        
        # List tools
        print("\n3. Listing available tools...")
        tools_request = send_mcp_request("tools/list", request_id=2)
        request_json = json.dumps(tools_request) + "\n"
        print(f"Sent: {request_json.strip()}")
        process.stdin.write(request_json)
        process.stdin.flush()
        
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print(f"Received: {json.dumps(response, indent=2)}")
            if "result" in response and "tools" in response["result"]:
                print(f"✓ Found {len(response['result']['tools'])} tools:")
                for tool in response["result"]["tools"]:
                    print(f"  - {tool['name']}: {tool['description']}")
        
        # List prompts
        print("\n4. Listing available prompts...")
        prompts_request = send_mcp_request("prompts/list", request_id=3)
        request_json = json.dumps(prompts_request) + "\n"
        print(f"Sent: {request_json.strip()}")
        process.stdin.write(request_json)
        process.stdin.flush()
        
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print(f"Received: {json.dumps(response, indent=2)}")
            if "result" in response and "prompts" in response["result"]:
                print(f"✓ Found {len(response['result']['prompts'])} prompts:")
                for prompt in response["result"]["prompts"]:
                    print(f"  - {prompt['name']}: {prompt['description']}")
        
        # List resources
        print("\n5. Listing available resources...")
        resources_request = send_mcp_request("resources/list", request_id=4)
        request_json = json.dumps(resources_request) + "\n"
        print(f"Sent: {request_json.strip()}")
        process.stdin.write(request_json)
        process.stdin.flush()
        
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print(f"Received: {json.dumps(response, indent=2)}")
            if "result" in response and "resources" in response["result"]:
                print(f"✓ Found {len(response['result']['resources'])} resources:")
                for resource in response["result"]["resources"]:
                    print(f"  - {resource['name']}: {resource['uri']}")
        
        print("\n" + "=" * 60)
        print("Test completed!")
        
        # Close stdin to signal end of input
        process.stdin.close()
        
        # Wait for process to finish (ignore cleanup errors)
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.terminate()
            process.wait(timeout=2)
        except Exception:
            # Ignore cleanup errors - test already succeeded
            pass
        
    except FileNotFoundError:
        print("Error: Docker not found. Please install Docker and ensure it's in your PATH.")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("Error: Docker command timed out.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    test_mcp_server()

