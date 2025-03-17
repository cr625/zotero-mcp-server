#!/usr/bin/env python3
"""
Simple test script for the Zotero MCP server.

This script tests the basic functionality of the Zotero MCP server
by sending JSON-RPC requests directly to the server.
"""

import json
import subprocess
import sys

def send_request(request):
    """
    Send a JSON-RPC request to the server and return the response.
    
    Args:
        request: The JSON-RPC request object
        
    Returns:
        The JSON-RPC response object
    """
    # Convert request to JSON
    request_json = json.dumps(request)
    
    # Use subprocess to send the request to the server
    process = subprocess.Popen(
        ['curl', '-s', '-X', 'POST', '-d', request_json, 'http://localhost:8080'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Get the response
    stdout, stderr = process.communicate()
    
    if stderr:
        print(f"Error: {stderr}", file=sys.stderr)
        return None
    
    # Parse the response
    try:
        response = json.loads(stdout)
        return response
    except json.JSONDecodeError:
        print(f"Error decoding response: {stdout}", file=sys.stderr)
        return None

def test_list_resources():
    """Test the list_resources method."""
    request = {
        "jsonrpc": "2.0",
        "method": "list_resources",
        "params": {},
        "id": 1
    }
    
    print("Testing list_resources...")
    response = send_request(request)
    
    if response and "result" in response:
        print("Success!")
        print(f"Resources: {json.dumps(response['result'], indent=2)}")
    else:
        print("Failed to list resources.")

def test_search_items():
    """Test the search_items tool."""
    request = {
        "jsonrpc": "2.0",
        "method": "call_tool",
        "params": {
            "name": "search_items",
            "arguments": {
                "query": "medical ethics",
                "limit": 5
            }
        },
        "id": 2
    }
    
    print("\nTesting search_items...")
    response = send_request(request)
    
    if response and "result" in response:
        print("Success!")
        print(f"Search results: {json.dumps(response['result'], indent=2)}")
    else:
        print("Failed to search items.")

def test_add_item():
    """Test the add_item tool."""
    request = {
        "jsonrpc": "2.0",
        "method": "call_tool",
        "params": {
            "name": "add_item",
            "arguments": {
                "item_type": "journalArticle",
                "title": "Ethical Considerations in Military Medical Triage",
                "creators": [
                    {
                        "creatorType": "author",
                        "firstName": "John",
                        "lastName": "Smith"
                    },
                    {
                        "creatorType": "author",
                        "firstName": "Jane",
                        "lastName": "Doe"
                    }
                ],
                "additional_fields": {
                    "publicationTitle": "Journal of Military Ethics",
                    "volume": "15",
                    "issue": "2",
                    "pages": "123-145",
                    "date": "2023",
                    "abstractNote": "This article discusses ethical considerations in military medical triage scenarios."
                }
            }
        },
        "id": 3
    }
    
    print("\nTesting add_item...")
    response = send_request(request)
    
    if response and "result" in response:
        print("Success!")
        print(f"Add item result: {json.dumps(response['result'], indent=2)}")
    else:
        print("Failed to add item.")

def test_get_recent_items():
    """Test the get_recent_items resource."""
    request = {
        "jsonrpc": "2.0",
        "method": "read_resource",
        "params": {
            "uri": "zotero://items/recent"
        },
        "id": 4
    }
    
    print("\nTesting get_recent_items...")
    response = send_request(request)
    
    if response and "result" in response:
        print("Success!")
        print(f"Recent items: {json.dumps(response['result'], indent=2)}")
    else:
        print("Failed to get recent items.")

if __name__ == "__main__":
    print("Testing Zotero MCP Server...")
    print("Note: This script assumes the server is running on http://localhost:8080")
    print("If the server is running on a different port or using stdio, this script won't work.")
    print("In that case, you can modify the script to use the appropriate transport.")
    
    test_list_resources()
    test_search_items()
    test_add_item()
    test_get_recent_items()
