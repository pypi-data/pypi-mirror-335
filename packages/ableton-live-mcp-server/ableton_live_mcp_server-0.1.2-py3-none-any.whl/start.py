#!/usr/bin/env python
"""
Convenience script to start both Ableton MCP server components.
"""
import os
import subprocess
import time
import sys
import signal
import atexit

daemon_process = None
server_process = None

def cleanup():
    """Kill child processes on exit."""
    global daemon_process, server_process
    
    print("Shutting down processes...")
    if daemon_process:
        print("Terminating OSC daemon...")
        try:
            os.kill(daemon_process.pid, signal.SIGTERM)
        except:
            pass
    
    if server_process:
        print("Terminating MCP server...")
        try:
            os.kill(server_process.pid, signal.SIGTERM)
        except:
            pass

def main():
    global daemon_process, server_process
    
    # Register cleanup handler
    atexit.register(cleanup)
    
    # Start OSC daemon
    print("Starting Ableton OSC daemon...")
    try:
        daemon_process = subprocess.Popen(
            ["ableton-osc-daemon"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
    except FileNotFoundError:
        print("Error: ableton-osc-daemon not found. Make sure you've installed the package.")
        sys.exit(1)
    
    # Wait for daemon to start
    time.sleep(2)
    print("OSC daemon started.")
    
    # Start MCP server
    print("Starting Ableton MCP server...")
    try:
        server_process = subprocess.Popen(
            ["ableton-mcp-server"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
    except FileNotFoundError:
        print("Error: ableton-mcp-server not found. Make sure you've installed the package.")
        sys.exit(1)
    
    print("MCP server started.")
    
    # Print output from both processes
    print("\n--- Ableton Live MCP Server Log ---")
    print("(Press Ctrl+C to exit)\n")
    
    try:
        while True:
            # Display daemon output
            if daemon_process.poll() is not None:
                print("OSC daemon exited with code:", daemon_process.returncode)
                break
            
            if daemon_process.stdout:
                line = daemon_process.stdout.readline()
                if line:
                    print("[OSC daemon]", line, end="")
            
            # Display server output
            if server_process.poll() is not None:
                print("MCP server exited with code:", server_process.returncode)
                break
                
            if server_process.stdout:
                line = server_process.stdout.readline()
                if line:
                    print("[MCP server]", line, end="")
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\nCaught keyboard interrupt, shutting down...")
    
    finally:
        cleanup()

if __name__ == "__main__":
    main() 