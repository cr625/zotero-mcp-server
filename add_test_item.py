#!/usr/bin/env python3
"""
Script to add a test item to the Zotero library.

This script adds a test article to the Zotero library to verify that
the API key has write access and that we're connecting to the correct library.
"""

import os
import sys
import json
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Add a test item to the Zotero library."""
    print("Add Test Item to Zotero Library")
    print("===============================")
    
    # Start a new server process
    print("\nStarting Zotero MCP server...")
    server_process = start_server()
    
    if not server_process:
        print("Failed to start server. Exiting.")
        return
    
    try:
        # Add a test item
        print("\nAdding test item...")
        response = send_request(server_process, {
            "jsonrpc": "2.0",
            "method": "call_tool",
            "params": {
                "name": "add_item",
                "arguments": {
                    "item_type": "journalArticle",
                    "title": "Test Article for Zotero MCP Server",
                    "creators": [
                        {
                            "creatorType": "author",
                            "firstName": "John",
                            "lastName": "Doe"
                        },
                        {
                            "creatorType": "author",
                            "firstName": "Jane",
                            "lastName": "Smith"
                        }
                    ],
                    "additional_fields": {
                        "publicationTitle": "Journal of Testing",
                        "volume": "1",
                        "issue": "1",
                        "pages": "1-10",
                        "date": "2025",
                        "abstractNote": "This is a test article to verify that the Zotero MCP server can add items to the library."
                    }
                }
            },
            "id": 1
        })
        
        if response and "result" in response and "content" in response["result"]:
            print("Success!")
            content = response["result"]["content"][0]["text"]
            result = json.loads(content)
            
            if result.get("success"):
                item_key = result["successful"]["0"]["key"]
                print(f"Test item added successfully with key: {item_key}")
                
                # Get the item details
                print("\nRetrieving the added item...")
                response = send_request(server_process, {
                    "jsonrpc": "2.0",
                    "method": "read_resource",
                    "params": {
                        "uri": f"zotero://items/{item_key}"
                    },
                    "id": 2
                })
                
                if response and "result" in response and "contents" in response["result"]:
                    print("Success!")
                    content = response["result"]["contents"][0]["text"]
                    item = json.loads(content)
                    print(f"Item details: {json.dumps(item, indent=2)}")
                else:
                    print("Failed to retrieve the added item.")
            else:
                print("Failed to add test item:")
                print(json.dumps(result, indent=2))
        else:
            print("Failed to add test item.")
            if response:
                print(f"Response: {json.dumps(response, indent=2)}")
        
        # Check if we're using a personal or group library
        print("\nChecking library type...")
        
        # Get the server's stderr output to see which library it's using
        server_output = server_process.stderr.readline()
        while server_output:
            if "Initialized Zotero client for user" in server_output:
                user_id = server_output.split("user ")[-1].strip()
                print(f"Using personal library with user ID: {user_id}")
                break
            elif "Initialized Zotero client for group" in server_output:
                group_id = server_output.split("group ")[-1].strip()
                print(f"Using group library with ID: {group_id}")
                print("To use your personal library, make sure ZOTERO_GROUP_ID is not set in the .env file")
                print("We've updated the server to prioritize the personal library, so please try again.")
                break
            server_output = server_process.stderr.readline()
        
        if not server_output:
            print("Could not determine which library is being used.")
            print("Please check the server logs for more information.")
    
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
