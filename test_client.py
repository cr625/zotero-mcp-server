#!/usr/bin/env python3
"""
Simple test client for the Zotero MCP server.

This script tests the basic functionality of the Zotero MCP server
by sending JSON-RPC requests directly to stdin/stdout.
"""

import json
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Main function to test the Zotero MCP server."""
    print("Zotero MCP Server Test Client")
    print("============================")
    print("This client will test the basic functionality of the Zotero MCP server.")
    print("Make sure the server is running in another terminal.")
    print()
    
    while True:
        print("\nChoose a test to run:")
        print("1. List resources")
        print("2. List tools")
        print("3. Search items")
        print("4. Get recent items")
        print("5. Add a new item")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ")
        
        if choice == "1":
            test_list_resources()
        elif choice == "2":
            test_list_tools()
        elif choice == "3":
            query = input("Enter search query (default: 'medical ethics'): ") or "medical ethics"
            test_search_items(query)
        elif choice == "4":
            test_get_recent_items()
        elif choice == "5":
            test_add_item()
        elif choice == "6":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

def test_list_resources():
    """Test the list_resources method."""
    print("\nTesting list_resources...")
    
    # Create a request to list resources
    request = {
        "jsonrpc": "2.0",
        "method": "list_resources",
        "params": {},
        "id": 1
    }
    
    # Send the request and get the response
    response = send_request_to_server(request)
    
    # Print the response
    if response and "result" in response:
        print("Success!")
        resources = response["result"]["resources"]
        print(f"Found {len(resources)} resources:")
        for resource in resources:
            print(f"  - {resource['name']}: {resource['uri']}")
    else:
        print("Failed to list resources.")

def test_list_tools():
    """Test the list_tools method."""
    print("\nTesting list_tools...")
    
    # Create a request to list tools
    request = {
        "jsonrpc": "2.0",
        "method": "list_tools",
        "params": {},
        "id": 1
    }
    
    # Send the request and get the response
    response = send_request_to_server(request)
    
    # Print the response
    if response and "result" in response:
        print("Success!")
        tools = response["result"]["tools"]
        print(f"Found {len(tools)} tools:")
        for tool in tools:
            print(f"  - {tool['name']}: {tool['description']}")
    else:
        print("Failed to list tools.")

def test_search_items(query):
    """Test the search_items tool."""
    print(f"\nTesting search_items with query '{query}'...")
    
    # Create a request to search items
    request = {
        "jsonrpc": "2.0",
        "method": "call_tool",
        "params": {
            "name": "search_items",
            "arguments": {
                "query": query,
                "limit": 5
            }
        },
        "id": 1
    }
    
    # Send the request and get the response
    response = send_request_to_server(request)
    
    # Print the response
    if response and "result" in response:
        print("Success!")
        content = response["result"]["content"][0]["text"]
        results = json.loads(content)
        print(f"Found {len(results['results'])} results for query '{query}':")
        for i, item in enumerate(results["results"]):
            if "data" in item and "title" in item["data"]:
                print(f"  {i+1}. {item['data']['title']}")
            else:
                print(f"  {i+1}. [No title]")
    else:
        print("Failed to search items.")

def test_get_recent_items():
    """Test the get_recent_items resource."""
    print("\nTesting get_recent_items...")
    
    # Create a request to get recent items
    request = {
        "jsonrpc": "2.0",
        "method": "read_resource",
        "params": {
            "uri": "zotero://items/recent"
        },
        "id": 1
    }
    
    # Send the request and get the response
    response = send_request_to_server(request)
    
    # Print the response
    if response and "result" in response:
        print("Success!")
        content = response["result"]["contents"][0]["text"]
        items = json.loads(content)
        print(f"Found {len(items)} recent items:")
        for i, item in enumerate(items[:5]):  # Show only the first 5 items
            if "data" in item and "title" in item["data"]:
                print(f"  {i+1}. {item['data']['title']}")
            else:
                print(f"  {i+1}. [No title]")
    else:
        print("Failed to get recent items.")

def test_add_item():
    """Test the add_item tool."""
    print("\nTesting add_item...")
    
    # Get item details from user
    title = input("Enter item title (default: 'Ethical Considerations in Military Medical Triage'): ") or "Ethical Considerations in Military Medical Triage"
    journal = input("Enter journal name (default: 'Journal of Military Ethics'): ") or "Journal of Military Ethics"
    year = input("Enter publication year (default: '2023'): ") or "2023"
    
    # Create a request to add an item
    request = {
        "jsonrpc": "2.0",
        "method": "call_tool",
        "params": {
            "name": "add_item",
            "arguments": {
                "item_type": "journalArticle",
                "title": title,
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
                    "publicationTitle": journal,
                    "volume": "15",
                    "issue": "2",
                    "pages": "123-145",
                    "date": year,
                    "abstractNote": "This article discusses ethical considerations in military medical triage scenarios."
                }
            }
        },
        "id": 1
    }
    
    # Send the request and get the response
    response = send_request_to_server(request)
    
    # Print the response
    if response and "result" in response:
        print("Success!")
        content = response["result"]["content"][0]["text"]
        result = json.loads(content)
        if result.get("success"):
            print("Item added successfully!")
            item_key = result["successful"]["0"]["key"]
            print(f"Item key: {item_key}")
        else:
            print("Failed to add item:")
            print(json.dumps(result, indent=2))
    else:
        print("Failed to add item.")

def send_request_to_server(request):
    """
    Send a request to the server and get the response.
    
    This function assumes the server is running in another terminal.
    It will prompt the user to copy the request, paste it into the server terminal,
    and then paste the response back.
    
    Args:
        request: The request object to send
        
    Returns:
        The response object from the server
    """
    # Convert request to JSON
    request_json = json.dumps(request)
    
    # Print instructions for the user
    print("\nPlease copy the following request and paste it into the server terminal:")
    print("-" * 80)
    print(request_json)
    print("-" * 80)
    
    # Wait for the user to paste the response
    print("\nAfter pasting the request, copy the response from the server terminal")
    print("and paste it below (press Enter after pasting):")
    
    # Read the response
    response_json = input()
    
    # Parse the response
    try:
        response = json.loads(response_json)
        return response
    except json.JSONDecodeError:
        print("Error: Invalid JSON response")
        return None

if __name__ == "__main__":
    main()
