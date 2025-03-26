#!/usr/bin/env python3
"""
Simple MCP client for testing the webscraper.py server.
This is a minimal implementation that just tests the basic functionality.
"""

import asyncio
import subprocess
import sys
import os
import json
import time
import traceback

async def main():
    print("\n--- Simple MCP Client ---")
    print("Starting webscraper.py...")
    
    # Get the path to the Python executable in the virtual environment
    python_path = os.path.join(os.path.abspath(".venv"), "bin", "python")
    if not os.path.exists(python_path):
        print(f"Error: Python interpreter not found at {python_path}")
        return 1
        
    # Set environment variables
    env = os.environ.copy()
    env["MCP_CLIENT_RUNNING"] = "1"
    env["MCP_DEBUG"] = "1"
    
    # Start the process
    try:
        process = await asyncio.create_subprocess_exec(
            python_path,
            "webscraper.py",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env
        )
        
        print(f"Process started with PID {process.pid}")
        
        # Wait a moment for process initialization
        await asyncio.sleep(2)
        
        # Send initialization message
        init_message = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "clientInfo": {
                    "name": "simple_mcp_client",
                    "version": "1.0.0"
                },
                "protocolVersion": "0.1.0",
                "capabilities": {}
            },
            "id": 1
        }
        
        print("\nSending initialization message...")
        init_msg_str = json.dumps(init_message)
        print(f">>> {init_msg_str}")
        process.stdin.write(init_msg_str.encode() + b"\n")
        await process.stdin.drain()
        
        # Read response - filter debug output
        response = await read_json_response(process)
        if not response:
            print("Error: No valid response received")
            return 1
            
        print(f"\nServer initialized successfully (id: {response.get('id')})")
        
        # Send a simple request to list tools
        list_tools_msg = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 2
        }
        
        print("\nSending tools/list request...")
        list_msg_str = json.dumps(list_tools_msg)
        print(f">>> {list_msg_str}")
        process.stdin.write(list_msg_str.encode() + b"\n")
        await process.stdin.drain()
        
        # Read response with timeout
        try:
            print("Waiting for tools/list response (5s timeout)...")
            resp = await asyncio.wait_for(read_json_response(process), timeout=5)
            if resp:
                print(f"\nTools list received: {json.dumps(resp, indent=2)}")
                return 0
            else:
                print("\nNo valid tools list response")
                return 1
        except asyncio.TimeoutError:
            print("\nTimeout waiting for tools/list response")
            
        # Try to get stderr
        stderr = await process.stderr.read()
        if stderr:
            print(f"\nSTDERR: {stderr.decode('utf-8')}")
            
        return 1
        
    except Exception as e:
        print(f"\nError: {e}")
        traceback.print_exc()
        return 1
    finally:
        # Clean up
        if 'process' in locals() and process.returncode is None:
            print("\nTerminating process...")
            process.terminate()
            await asyncio.sleep(0.5)

async def read_json_response(process):
    """Read and parse a JSON response, filtering out debug messages"""
    while True:
        try:
            line = await process.stdout.readline()
            if not line:
                print("Empty response (EOF)")
                return None
                
            decoded = line.decode('utf-8').strip()
            
            # Print debug messages but don't treat them as responses
            if decoded.startswith("[webscraper.py"):
                print(f"DEBUG: {decoded}")
                continue
                
            # Skip non-JSON lines
            if not decoded.startswith("{"):
                print(f"NON-JSON: {decoded}")
                continue
                
            print(f"<<< {decoded[:100]}..." if len(decoded) > 100 else f"<<< {decoded}")
            
            try:
                return json.loads(decoded)
            except json.JSONDecodeError as e:
                print(f"JSON parse error: {e}")
                
        except Exception as e:
            print(f"Error reading response: {e}")
            return None

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(130) 