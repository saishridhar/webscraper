#!/usr/bin/env python3
"""
Very simple test for webscraper.py communication.
"""

import asyncio
import sys
import os
import json

async def main():
    print("\n=== Webscraper Simple Test ===")
    
    python_path = os.path.join(os.path.abspath(".venv"), "bin", "python")
    if not os.path.exists(python_path):
        print(f"Error: Python interpreter not found at {python_path}")
        return 1
    
    # Start the webscraper process
    try:
        env = os.environ.copy()
        env["MCP_CLIENT_RUNNING"] = "1"
        env["MCP_DEBUG"] = "1"
        
        print("Starting webscraper.py...")
        process = await asyncio.create_subprocess_exec(
            python_path,
            "webscraper.py",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env
        )
        
        print(f"Webscraper process started with PID {process.pid}")
        
        # Create a task to read and print stderr
        stderr_task = asyncio.create_task(read_stderr(process))
        
        # Wait for process to initialize
        await asyncio.sleep(2)
        
        # Send initialization message
        init_message = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "clientInfo": {
                    "name": "webscraper_test",
                    "version": "1.0.0"
                },
                "protocolVersion": "0.1.0",
                "capabilities": {}
            },
            "id": 1
        }
        
        print("\nSending initialization message...")
        print(f">>> {json.dumps(init_message)}")
        process.stdin.write(json.dumps(init_message).encode() + b"\n")
        await process.stdin.drain()
        
        # Read stdout continuously
        print("Reading responses...")
        stdout_task = asyncio.create_task(read_stdout(process))
        
        # Wait for responses for 5 seconds
        await asyncio.sleep(5)
        
        # Now send a request to list tools
        list_tools_msg = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 2
        }
        
        print("\nSending tools/list request...")
        print(f">>> {json.dumps(list_tools_msg)}")
        process.stdin.write(json.dumps(list_tools_msg).encode() + b"\n")
        await process.stdin.drain()
        
        # Wait for more responses
        await asyncio.sleep(5)
        
        # Cancel reading tasks
        stdout_task.cancel()
        stderr_task.cancel()
        
        # Terminate process
        print("\nTerminating process...")
        process.terminate()
        await asyncio.sleep(0.5)
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

async def read_stdout(process):
    """Read and print all stdout"""
    try:
        while True:
            line = await process.stdout.readline()
            if not line:
                print("EOF on stdout")
                break
                
            decoded = line.decode().strip()
            print(f"STDOUT: {decoded}")
            
            # Try to parse if it looks like JSON
            if decoded.startswith("{"):
                try:
                    json_obj = json.loads(decoded)
                    print(f"Parsed JSON: {json.dumps(json_obj, indent=2)}")
                except json.JSONDecodeError:
                    pass
    except asyncio.CancelledError:
        print("Stdout reading canceled")
    except Exception as e:
        print(f"Error reading stdout: {e}")

async def read_stderr(process):
    """Read and print all stderr"""
    try:
        while True:
            line = await process.stderr.readline()
            if not line:
                print("EOF on stderr")
                break
                
            print(f"STDERR: {line.decode().strip()}")
    except asyncio.CancelledError:
        print("Stderr reading canceled")
    except Exception as e:
        print(f"Error reading stderr: {e}")

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("Interrupted by user")
        sys.exit(130) 