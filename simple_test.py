#!/usr/bin/env python3
"""
Simple test script for the Zotero MCP server.

This script creates a new instance of the Zotero MCP server and tests its functionality.
"""

import os
import sys
import json
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Run tests for the Zotero MCP server."""
    print("Simple Zotero MCP Server Test")
    print("=============================")
    
    # Start a new server process
    print("\nStarting Zotero MCP server...")
    server_process = start_server()
    
    if not server_process:
        print("Failed to start server. Exiting.")
        return
    
    try:
        # Test list_resources
        print("\nTesting list_resources...")
        response = send_request(server_process, {
            "jsonrpc": "2.0",
            "method": "list_resources",
            "params": {},
            "id": 1
        })
        
        if response and "result" in response:
            print("Success!")
            resources = response["result"]["resources"]
            print(f"Found {len(resources)} resources:")
            for resource in resources:
                print(f"  - {resource['name']}")
        else:
            print("Failed to list resources.")
        
        # Test list_tools
        print("\nTesting list_tools...")
        response = send_request(server_process, {
            "jsonrpc": "2.0",
            "method": "list_tools",
            "params": {},
            "id": 2
        })
        
        if response and "result" in response:
            print("Success!")
            tools = response["result"]["tools"]
            print(f"Found {len(tools)} tools:")
            for tool in tools:
                print(f"  - {tool['name']}: {tool['description']}")
        else:
            print("Failed to list tools.")
        
        # Test get_recent_items to verify library access
        print("\nTesting get_recent_items...")
        response = send_request(server_process, {
            "jsonrpc": "2.0",
            "method": "read_resource",
            "params": {
                "uri": "zotero://items/recent"
            },
            "id": 3
        })
        
        if response and "result" in response and "contents" in response["result"]:
            print("Success!")
            content = response["result"]["contents"][0]["text"]
            items = json.loads(content)
            print(f"Found {len(items)} recent items in your library")
            if len(items) > 0:
                print("\nHere are the first few items:")
                for i, item in enumerate(items[:5]):
                    if "data" in item and "title" in item["data"]:
                        print(f"  {i+1}. {item['data']['title']}")
                    else:
                        print(f"  {i+1}. [No title]")
            else:
                print("Your library appears to be empty. Please add some items to your Zotero library.")
        else:
            print("Failed to get recent items.")
            if response:
                print(f"Response: {json.dumps(response, indent=2)}")
        
        # Test search_items with different queries
        print("\nTesting search_items with multiple queries...")
        search_queries = ["ethics", "medical", "research", ""]  # Empty string gets all items
        
        for query in search_queries:
            query_display = query if query else "ALL ITEMS"
            print(f"\nSearching for: '{query_display}'...")
            
            response = send_request(server_process, {
                "jsonrpc": "2.0",
                "method": "call_tool",
                "params": {
                    "name": "search_items",
                    "arguments": {
                        "query": query,
                        "limit": 10
                    }
                },
                "id": 4
            })
            
            if response and "result" in response and "content" in response["result"]:
                content = response["result"]["content"][0]["text"]
                results = json.loads(content)
                print(f"Found {len(results['results'])} results for query '{query_display}'")
                
                if len(results['results']) > 0:
                    print("First few results:")
                    for i, item in enumerate(results['results'][:5]):
                        if "data" in item and "title" in item["data"]:
                            print(f"  {i+1}. {item['data']['title']}")
                        else:
                            print(f"  {i+1}. [No title]")
            else:
                print(f"Failed to search for '{query_display}'")
                if response:
                    print(f"Response: {json.dumps(response, indent=2)}")
    
    finally:
        # Stop the server
        print("\nStopping server...")
        server_process.terminate()
        server_process.wait(timeout=5)
        print("Server stopped.")

def start_server():
    """
    Start a new Zotero MCP server process.
    
    Returns:
        The server process, or None if the server failed to start
    """
    try:
        # Get the path to the server script
        server_path = os.path.join(os.path.dirname(__file__), 'src', 'server.py')
        
        # Start the server process
        process = subprocess.Popen(
            [sys.executable, server_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1  # Line buffered
        )
        
        # Wait for the server to start
        for _ in range(10):
            line = process.stderr.readline()
            if "running on stdio" in line:
                print("Server started successfully.")
                return process
        
        # Server didn't start
        print("Server didn't start properly.")
        process.terminate()
        return None
    
    except Exception as e:
        print(f"Error starting server: {str(e)}")
        return None

def send_request(process, request):
    """
    Send a request to the server and get the response.
    
    Args:
        process: The server process
        request: The request object to send
        
    Returns:
        The response object from the server
    """
    try:
        # Convert request to JSON
        request_json = json.dumps(request)
        
        # Send request
        process.stdin.write(request_json + '\n')
        process.stdin.flush()
        
        # Read response
        response_line = process.stdout.readline()
        
        # Parse response
        response = json.loads(response_line)
        return response
    
    except Exception as e:
        print(f"Error sending request: {str(e)}")
        return None

if __name__ == "__main__":
    main()
