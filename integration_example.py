#!/usr/bin/env python3
"""
Example of integrating the Zotero MCP server with the AI Ethical Decision-Making application.

This script demonstrates how to:
1. Configure the MCP client to use the Zotero MCP server
2. Use the Zotero MCP server to search for references
3. Get citations for references
4. Add references to a Zotero library
"""

import os
import json
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ZoteroMCPClient:
    """Client for interacting with the Zotero MCP server."""
    
    def __init__(self, server_path=None):
        """
        Initialize the Zotero MCP client.
        
        Args:
            server_path: Path to the Zotero MCP server script (optional)
        """
        self.server_path = server_path or os.path.join(os.path.dirname(__file__), 'src', 'server.py')
        self.server_process = None
    
    def start_server(self):
        """Start the Zotero MCP server process."""
        if self.server_process is None or self.server_process.poll() is not None:
            # Server not running, start it
            self.server_process = subprocess.Popen(
                ['python', self.server_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1  # Line buffered
            )
    
    def stop_server(self):
        """Stop the Zotero MCP server process."""
        if self.server_process is not None and self.server_process.poll() is None:
            # Server running, stop it
            self.server_process.terminate()
            self.server_process.wait(timeout=5)
            self.server_process = None
    
    def _send_request(self, request_type, params):
        """
        Send a request to the Zotero MCP server.
        
        Args:
            request_type: Type of request
            params: Request parameters
            
        Returns:
            Response from the server
        """
        # Ensure server is running
        self.start_server()
        
        # Prepare request
        request = {
            "jsonrpc": "2.0",
            "method": request_type,
            "params": params,
            "id": 1
        }
        
        # Send request
        self.server_process.stdin.write(json.dumps(request) + '\n')
        self.server_process.stdin.flush()
        
        # Read response
        response_line = self.server_process.stdout.readline()
        response = json.loads(response_line)
        
        # Check for errors
        if "error" in response:
            raise Exception(f"Zotero MCP server error: {response['error']['message']}")
        
        return response["result"]
    
    def get_collections(self):
        """
        Get collections from the Zotero library.
        
        Returns:
            List of collections
        """
        response = self._send_request(
            "read_resource",
            {"uri": "zotero://collections"}
        )
        
        # Parse JSON content
        content = response["contents"][0]["text"]
        return json.loads(content)
    
    def get_recent_items(self):
        """
        Get recent items from the Zotero library.
        
        Returns:
            List of recent items
        """
        response = self._send_request(
            "read_resource",
            {"uri": "zotero://items/recent"}
        )
        
        # Parse JSON content
        content = response["contents"][0]["text"]
        return json.loads(content)
    
    def search_items(self, query, collection_key=None, limit=20):
        """
        Search for items in the Zotero library.
        
        Args:
            query: Search query
            collection_key: Collection key to search in (optional)
            limit: Maximum number of results to return
            
        Returns:
            Search results
        """
        response = self._send_request(
            "call_tool",
            {
                "name": "search_items",
                "arguments": {
                    "query": query,
                    "collection_key": collection_key,
                    "limit": limit
                }
            }
        )
        
        # Parse JSON content
        content = response["content"][0]["text"]
        return json.loads(content)
    
    def get_citation(self, item_key, style="apa"):
        """
        Get citation for a specific item.
        
        Args:
            item_key: Item key
            style: Citation style (e.g., apa, mla, chicago)
            
        Returns:
            Citation text
        """
        response = self._send_request(
            "call_tool",
            {
                "name": "get_citation",
                "arguments": {
                    "item_key": item_key,
                    "style": style
                }
            }
        )
        
        # Return citation text
        return response["content"][0]["text"]
    
    def add_item(self, item_type, title, creators=None, collection_key=None, additional_fields=None):
        """
        Add a new item to the Zotero library.
        
        Args:
            item_type: Item type (e.g., journal, book, webpage)
            title: Item title
            creators: Item creators (authors, editors, etc.)
            collection_key: Collection key to add the item to (optional)
            additional_fields: Additional fields for the item (e.g., date, url, publisher)
            
        Returns:
            Response from the server
        """
        response = self._send_request(
            "call_tool",
            {
                "name": "add_item",
                "arguments": {
                    "item_type": item_type,
                    "title": title,
                    "creators": creators or [],
                    "collection_key": collection_key,
                    "additional_fields": additional_fields or {}
                }
            }
        )
        
        # Parse JSON content
        content = response["content"][0]["text"]
        return json.loads(content)
    
    def get_bibliography(self, item_keys, style="apa"):
        """
        Get bibliography for multiple items.
        
        Args:
            item_keys: Array of item keys
            style: Citation style (e.g., apa, mla, chicago)
            
        Returns:
            Bibliography text
        """
        response = self._send_request(
            "call_tool",
            {
                "name": "get_bibliography",
                "arguments": {
                    "item_keys": item_keys,
                    "style": style
                }
            }
        )
        
        # Return bibliography text
        return response["content"][0]["text"]


def integrate_with_ethical_dm():
    """
    Example of integrating the Zotero MCP server with the AI Ethical Decision-Making application.
    
    This function demonstrates how to:
    1. Configure the MCP client to use the Zotero MCP server
    2. Use the Zotero MCP server to search for references
    3. Get citations for references
    4. Add references to a Zotero library
    """
    # Initialize the Zotero MCP client
    zotero_client = ZoteroMCPClient()
    
    # Start the server
    zotero_client.start_server()
    
    try:
        # Search for references related to medical ethics
        print("Searching for references related to medical ethics...")
        search_results = zotero_client.search_items("medical ethics")
        
        # Print search results
        print(f"Found {len(search_results['results'])} references")
        
        # If there are search results, get citations for the first 3
        if search_results["results"]:
            print("\nCitations:")
            for i, item in enumerate(search_results["results"][:3]):
                item_key = item["key"]
                citation = zotero_client.get_citation(item_key)
                print(f"{i+1}. {citation}")
        
        # Add a new reference
        print("\nAdding a new reference...")
        new_item = zotero_client.add_item(
            item_type="journalArticle",
            title="Ethical Considerations in Military Medical Triage",
            creators=[
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
            additional_fields={
                "publicationTitle": "Journal of Military Ethics",
                "volume": "15",
                "issue": "2",
                "pages": "123-145",
                "date": "2023",
                "abstractNote": "This article discusses ethical considerations in military medical triage scenarios."
            }
        )
        
        print("New reference added successfully")
        
        # Get recent items to verify the new reference was added
        print("\nRecent items:")
        recent_items = zotero_client.get_recent_items()
        for i, item in enumerate(recent_items[:3]):
            print(f"{i+1}. {item.get('data', {}).get('title', 'No title')}")
    
    finally:
        # Stop the server
        zotero_client.stop_server()


def modify_mcp_client_for_zotero():
    """
    Example of how to modify the existing MCP client to use the Zotero MCP server.
    
    This function demonstrates the changes needed to integrate the Zotero MCP server
    with the existing AI Ethical Decision-Making application.
    """
    print("To integrate the Zotero MCP server with the existing application, you need to:")
    print("1. Add the Zotero MCP server path to the MCP client")
    print("2. Add methods to interact with the Zotero MCP server")
    print("3. Use the Zotero MCP server in the application")
    
    print("\nHere's an example of how to modify the existing MCP client:")
    print('''
    # In app/services/mcp_client.py
    
    def get_zotero_references(self, query, limit=5):
        """
        Get references from Zotero matching a query.
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            
        Returns:
            Dictionary containing search results
        """
        response = self._send_request(
            "call_tool",
            {
                "name": "search_items",
                "arguments": {
                    "query": query,
                    "limit": limit
                }
            }
        )
        
        # Parse JSON content
        content = response["content"][0]["text"]
        return json.loads(content)
    
    def get_zotero_citation(self, item_key, style="apa"):
        """
        Get citation for a specific Zotero item.
        
        Args:
            item_key: Item key
            style: Citation style (e.g., apa, mla, chicago)
            
        Returns:
            Citation text
        """
        response = self._send_request(
            "call_tool",
            {
                "name": "get_citation",
                "arguments": {
                    "item_key": item_key,
                    "style": style
                }
            }
        )
        
        # Return citation text
        return response["content"][0]["text"]
    ''')
    
    print("\nAnd here's an example of how to use it in the application:")
    print('''
    # In app/routes/scenarios.py
    
    @bp.route("/scenario/<int:id>/references")
    def scenario_references(id):
        # Get scenario
        scenario = Scenario.query.get_or_404(id)
        
        # Create a query from the scenario
        query = f"{scenario.name} {scenario.description}"
        
        # Get references from Zotero
        mcp_client = MCPClient()
        references = mcp_client.get_zotero_references(query)
        
        # Render template
        return render_template("scenario_references.html", scenario=scenario, references=references)
    ''')


if __name__ == "__main__":
    # Example usage
    integrate_with_ethical_dm()
    
    print("\n" + "-" * 80 + "\n")
    
    # Example of how to modify the existing MCP client
    modify_mcp_client_for_zotero()
