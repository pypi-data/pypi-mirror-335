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
import socket
import argparse

daemon_process = None
server_process = None

def cleanup():
    """Kill child processes on exit."""
    global daemon_process, server_process
    
    print("\nShutting down processes...")
    if daemon_process and daemon_process.poll() is None:
        print("Terminating OSC daemon...")
        try:
            if sys.platform == 'win32':
                daemon_process.terminate()
            else:
                os.kill(daemon_process.pid, signal.SIGTERM)
        except Exception as e:
            print(f"Error terminating OSC daemon: {e}")
    
    if server_process and server_process.poll() is None:
        print("Terminating MCP server...")
        try:
            if sys.platform == 'win32':
                server_process.terminate()
            else:
                os.kill(server_process.pid, signal.SIGTERM)
        except Exception as e:
            print(f"Error terminating MCP server: {e}")

def wait_for_port(host, port, timeout=10):
    """Wait for a port to be ready."""
    start_time = time.time()
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                s.connect((host, port))
                return True
        except (socket.timeout, ConnectionRefusedError):
            if time.time() - start_time > timeout:
                return False
            time.sleep(0.5)

def main():
    global daemon_process, server_process
    
    parser = argparse.ArgumentParser(description="Start Ableton Live MCP components")
    parser.add_argument("--osc-host", default="127.0.0.1", help="Host for the OSC daemon")
    parser.add_argument("--osc-port", type=int, default=65432, help="Port for the OSC daemon")
    parser.add_argument("--mcp-host", default="127.0.0.1", help="Host for the MCP server")
    parser.add_argument("--mcp-port", type=int, default=8000, help="Port for the MCP server")
    parser.add_argument("--ableton-host", default="127.0.0.1", help="Host for Ableton Live")
    parser.add_argument("--ableton-port", type=int, default=11000, help="Port for sending to Ableton Live") 
    parser.add_argument("--receive-port", type=int, default=11001, help="Port for receiving from Ableton Live")
    parser.add_argument("--debug", action="store_true", help="Show debug output from both processes")
    args = parser.parse_args()
    
    # Set environment variables for the MCP server
    env = os.environ.copy()
    env["MCP_HOST"] = args.mcp_host
    env["MCP_PORT"] = str(args.mcp_port)
    
    # Register cleanup handler
    atexit.register(cleanup)
    
    # Start OSC daemon
    print("Starting Ableton OSC daemon...")
    try:
        cmd = [
            "ableton-osc-daemon",
            "--socket-host", args.osc_host,
            "--socket-port", str(args.osc_port),
            "--ableton-host", args.ableton_host,
            "--ableton-port", str(args.ableton_port),
            "--receive-port", str(args.receive_port)
        ]
        
        if args.debug:
            daemon_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
        else:
            daemon_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL if not args.debug else None,
                stderr=subprocess.DEVNULL if not args.debug else None
            )
    except FileNotFoundError:
        print("Error: ableton-osc-daemon not found. Make sure you've installed the package.")
        sys.exit(1)
    
    # Wait for OSC daemon to start and verify it's running
    print(f"Waiting for OSC daemon to start on {args.osc_host}:{args.osc_port}...")
    if not wait_for_port(args.osc_host, args.osc_port, timeout=10):
        print("Error: OSC daemon failed to start or is not responding.")
        cleanup()
        sys.exit(1)
        
    print(f"OSC daemon started successfully on {args.osc_host}:{args.osc_port}")
    
    # Start MCP server
    print("Starting Ableton MCP server...")
    try:
        if args.debug:
            server_process = subprocess.Popen(
                ["ableton-mcp-server"],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
        else:
            server_process = subprocess.Popen(
                ["ableton-mcp-server"],
                env=env,
                stdout=subprocess.DEVNULL if not args.debug else None,
                stderr=subprocess.DEVNULL if not args.debug else None
            )
    except FileNotFoundError:
        print("Error: ableton-mcp-server not found. Make sure you've installed the package.")
        cleanup()
        sys.exit(1)
    
    # Wait for MCP server to start and verify it's running
    print(f"Waiting for MCP server to start on {args.mcp_host}:{args.mcp_port}...")
    if not wait_for_port(args.mcp_host, args.mcp_port, timeout=10):
        print("Warning: MCP server may not have started correctly.")
    else:
        print(f"MCP server started successfully on {args.mcp_host}:{args.mcp_port}")
    
    print("\n--- Ableton Live MCP Server Running ---")
    print("Connections:")
    print(f"• OSC Daemon: {args.osc_host}:{args.osc_port}")
    print(f"• MCP Server: {args.mcp_host}:{args.mcp_port}")
    print(f"• Ableton Live: {args.ableton_host}:{args.ableton_port}")
    print(f"• Receive Port: {args.receive_port}")
    print("\nNOTE: Make sure AbletonOSC control surface is enabled in Ableton Live's preferences")
    print("Press Ctrl+C to exit\n")
    
    if args.debug:
        try:
            while True:
                # Monitor both processes
                daemon_alive = daemon_process and daemon_process.poll() is None
                server_alive = server_process and server_process.poll() is None
                
                if not (daemon_alive and server_alive):
                    print("One or both processes have exited:")
                    if not daemon_alive:
                        print(f"OSC daemon exited with code: {daemon_process.returncode if daemon_process else 'N/A'}")
                    if not server_alive:
                        print(f"MCP server exited with code: {server_process.returncode if server_process else 'N/A'}")
                    break
                
                # Print output in debug mode
                if daemon_process and daemon_process.stdout:
                    while True:
                        line = daemon_process.stdout.readline()
                        if not line:
                            break
                        print(f"[OSC] {line.rstrip()}")
                
                if server_process and server_process.stdout:
                    while True:
                        line = server_process.stdout.readline()
                        if not line:
                            break
                        print(f"[MCP] {line.rstrip()}")
                
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nShutting down...")
    else:
        # In non-debug mode, just wait for processes to end
        try:
            while True:
                daemon_alive = daemon_process and daemon_process.poll() is None
                server_alive = server_process and server_process.poll() is None
                
                if not (daemon_alive and server_alive):
                    break
                    
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\nShutting down...")

if __name__ == "__main__":
    main() 