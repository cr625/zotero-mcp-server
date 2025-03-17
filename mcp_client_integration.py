#!/usr/bin/env python3
"""
Example of how to modify the existing MCP client to use the Zotero MCP server.

This file shows the changes needed to integrate the Zotero MCP server with the
existing AI Ethical Decision-Making application's MCP client.
"""

import os
import json
import subprocess
from typing import Dict, List, Any, Optional

class MCPClient:
    """Client for interacting with the MCP server."""
    
    def __init__(self, server_path: Optional[str] = None, zotero_server_path: Optional[str] = None):
        """
        Initialize the MCP client.
        
        Args:
            server_path: Path to the MCP server script (optional)
            zotero_server_path: Path to the Zotero MCP server script (optional)
        """
        self.server_path = server_path or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'mcp', 'server_complete_with_run.py')
        self.zotero_server_path = zotero_server_path or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'zotero-mcp-server', 'src', 'server.py')
        self.server_process = None
        self.zotero_server_process = None
    
    def start_server(self, server_type: str = "ethical-dm"):
        """
        Start the MCP server process.
        
        Args:
            server_type: Type of server to start (ethical-dm or zotero)
        """
        if server_type == "ethical-dm":
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
        elif server_type == "zotero":
            if self.zotero_server_process is None or self.zotero_server_process.poll() is not None:
                # Server not running, start it
                self.zotero_server_process = subprocess.Popen(
                    ['python', self.zotero_server_path],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1  # Line buffered
                )
    
    def stop_server(self, server_type: str = "ethical-dm"):
        """
        Stop the MCP server process.
        
        Args:
            server_type: Type of server to stop (ethical-dm or zotero)
        """
        if server_type == "ethical-dm":
            if self.server_process is not None and self.server_process.poll() is None:
                # Server running, stop it
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
                self.server_process = None
        elif server_type == "zotero":
            if self.zotero_server_process is not None and self.zotero_server_process.poll() is None:
                # Server running, stop it
                self.zotero_server_process.terminate()
                self.zotero_server_process.wait(timeout=5)
                self.zotero_server_process = None
    
    def _send_request(self, request_type: str, params: Dict[str, Any], server_type: str = "ethical-dm") -> Dict[str, Any]:
        """
        Send a request to the MCP server.
        
        Args:
            request_type: Type of request
            params: Request parameters
            server_type: Type of server to send request to (ethical-dm or zotero)
            
        Returns:
            Response from the server
        """
        # Ensure server is running
        self.start_server(server_type)
        
        # Prepare request
        request = {
            "jsonrpc": "2.0",
            "method": request_type,
            "params": params,
            "id": 1
        }
        
        # Send request to appropriate server
        if server_type == "ethical-dm":
            server_process = self.server_process
        elif server_type == "zotero":
            server_process = self.zotero_server_process
        else:
            raise ValueError(f"Invalid server type: {server_type}")
        
        # Send request
        server_process.stdin.write(json.dumps(request) + '\n')
        server_process.stdin.flush()
        
        # Read response
        response_line = server_process.stdout.readline()
        response = json.loads(response_line)
        
        # Check for errors
        if "error" in response:
            raise Exception(f"MCP server error: {response['error']['message']}")
        
        return response["result"]
    
    # Existing methods for the ethical-dm server
    
    def get_guidelines(self, domain: str = "military-medical-triage") -> Dict[str, Any]:
        """
        Get guidelines for a specific domain.
        
        Args:
            domain: Domain to get guidelines for (military-medical-triage, engineering-ethics, us-law-practice)
            
        Returns:
            Dictionary containing guidelines
        """
        response = self._send_request(
            "read_resource",
            {"uri": f"ethical-dm://guidelines/{domain}"},
            server_type="ethical-dm"
        )
        
        # Parse JSON content
        content = response["contents"][0]["text"]
        return json.loads(content)
    
    # ... other existing methods ...
    
    # New methods for the Zotero MCP server
    
    def get_zotero_collections(self) -> Dict[str, Any]:
        """
        Get collections from the Zotero library.
        
        Returns:
            Dictionary containing collections
        """
        response = self._send_request(
            "read_resource",
            {"uri": "zotero://collections"},
            server_type="zotero"
        )
        
        # Parse JSON content
        content = response["contents"][0]["text"]
        return json.loads(content)
    
    def get_zotero_recent_items(self) -> Dict[str, Any]:
        """
        Get recent items from the Zotero library.
        
        Returns:
            Dictionary containing recent items
        """
        response = self._send_request(
            "read_resource",
            {"uri": "zotero://items/recent"},
            server_type="zotero"
        )
        
        # Parse JSON content
        content = response["contents"][0]["text"]
        return json.loads(content)
    
    def search_zotero_items(self, query: str, collection_key: Optional[str] = None, limit: int = 20) -> Dict[str, Any]:
        """
        Search for items in the Zotero library.
        
        Args:
            query: Search query
            collection_key: Collection key to search in (optional)
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
                    "collection_key": collection_key,
                    "limit": limit
                }
            },
            server_type="zotero"
        )
        
        # Parse JSON content
        content = response["content"][0]["text"]
        return json.loads(content)
    
    def get_zotero_citation(self, item_key: str, style: str = "apa") -> str:
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
            },
            server_type="zotero"
        )
        
        # Return citation text
        return response["content"][0]["text"]
    
    def add_zotero_item(self, item_type: str, title: str, creators: Optional[List[Dict[str, str]]] = None,
                        collection_key: Optional[str] = None, additional_fields: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Add a new item to the Zotero library.
        
        Args:
            item_type: Item type (e.g., journal, book, webpage)
            title: Item title
            creators: Item creators (authors, editors, etc.)
            collection_key: Collection key to add the item to (optional)
            additional_fields: Additional fields for the item (e.g., date, url, publisher)
            
        Returns:
            Dictionary containing response from the server
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
            },
            server_type="zotero"
        )
        
        # Parse JSON content
        content = response["content"][0]["text"]
        return json.loads(content)
    
    def get_zotero_bibliography(self, item_keys: List[str], style: str = "apa") -> str:
        """
        Get bibliography for multiple Zotero items.
        
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
            },
            server_type="zotero"
        )
        
        # Return bibliography text
        return response["content"][0]["text"]
    
    def get_references_for_scenario(self, scenario_id: int, limit: int = 5) -> Dict[str, Any]:
        """
        Get references for a specific scenario.
        
        Args:
            scenario_id: Scenario ID
            limit: Maximum number of results to return
            
        Returns:
            Dictionary containing references
        """
        from app.models import Scenario
        
        # Get scenario
        scenario = Scenario.query.get(scenario_id)
        if not scenario:
            return {"error": f"Scenario with ID {scenario_id} not found"}
        
        # Create query from scenario
        query = f"{scenario.name} {scenario.description}"
        
        # Add character information
        for char in scenario.characters:
            query += f" {char.name} {char.role}"
            for cond in char.conditions:
                query += f" {cond.name}"
        
        # Search for references
        return self.search_zotero_items(query, limit=limit)


# Example usage
if __name__ == "__main__":
    # Initialize MCP client
    client = MCPClient()
    
    # Start both servers
    client.start_server("ethical-dm")
    client.start_server("zotero")
    
    try:
        # Get guidelines from ethical-dm server
        guidelines = client.get_guidelines()
        print("Guidelines:", guidelines)
        
        # Get collections from Zotero server
        collections = client.get_zotero_collections()
        print("Zotero Collections:", collections)
        
        # Search for items in Zotero
        search_results = client.search_zotero_items("medical ethics")
        print("Search Results:", search_results)
    
    finally:
        # Stop both servers
        client.stop_server("ethical-dm")
        client.stop_server("zotero")
