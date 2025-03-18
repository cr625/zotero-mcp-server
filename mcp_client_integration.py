#!/usr/bin/env python3
"""
Example of how to integrate the Zotero MCP server with the AI Ethical Decision-Making application.

This file shows how to modify the existing MCP client to support the Zotero MCP server.
"""

import json
import subprocess
import os
from typing import List, Dict, Any, Optional, Union

class MCPClient:
    """Client for interacting with MCP servers."""
    
    def __init__(self):
        """Initialize the MCP client."""
        # Path to the Zotero MCP server
        self.zotero_server_path = os.path.join(os.path.dirname(__file__), "src", "server.py")
        
        # Path to the ontology MCP server (existing server)
        self.ontology_server_path = "/path/to/ontology/server.py"
    
    def _send_request_to_zotero(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send a request to the Zotero MCP server."""
        # Create request
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1
        }
        
        # Convert request to JSON
        request_json = json.dumps(request)
        
        # Send request to server
        process = subprocess.Popen(
            ["python", self.zotero_server_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send request
        stdout, stderr = process.communicate(input=request_json + "\n")
        
        # Parse response
        try:
            response = json.loads(stdout)
            return response
        except json.JSONDecodeError:
            raise Exception(f"Invalid response from server: {stdout}")
    
    def _send_request_to_ontology(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send a request to the ontology MCP server."""
        # Create request
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1
        }
        
        # Convert request to JSON
        request_json = json.dumps(request)
        
        # Send request to server
        process = subprocess.Popen(
            ["python", self.ontology_server_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send request
        stdout, stderr = process.communicate(input=request_json + "\n")
        
        # Parse response
        try:
            response = json.loads(stdout)
            return response
        except json.JSONDecodeError:
            raise Exception(f"Invalid response from server: {stdout}")
    
    # Existing methods for the ontology MCP server
    
    def get_ontology(self, domain: str) -> Dict[str, Any]:
        """Get the ontology for a domain."""
        response = self._send_request_to_ontology(
            method="read_resource",
            params={
                "uri": f"ontology://{domain}"
            }
        )
        
        if "result" in response and "contents" in response["result"]:
            content = response["result"]["contents"][0]["text"]
            return json.loads(content)
        
        return {}
    
    def get_ethical_guidelines(self, domain: str) -> List[Dict[str, Any]]:
        """Get ethical guidelines for a domain."""
        response = self._send_request_to_ontology(
            method="call_tool",
            params={
                "name": "get_guidelines",
                "arguments": {
                    "domain": domain
                }
            }
        )
        
        if "result" in response and "content" in response["result"]:
            content = response["result"]["content"][0]["text"]
            return json.loads(content)
        
        return []
    
    def evaluate_decision(self, domain: str, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a decision against ethical guidelines."""
        response = self._send_request_to_ontology(
            method="call_tool",
            params={
                "name": "evaluate_decision",
                "arguments": {
                    "domain": domain,
                    "decision": decision
                }
            }
        )
        
        if "result" in response and "content" in response["result"]:
            content = response["result"]["content"][0]["text"]
            return json.loads(content)
        
        return {}
    
    # New methods for the Zotero MCP server
    
    def search_zotero_items(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for items in the Zotero library."""
        response = self._send_request_to_zotero(
            method="call_tool",
            params={
                "name": "search_items",
                "arguments": {
                    "query": query,
                    "limit": limit
                }
            }
        )
        
        if "result" in response and "content" in response["result"]:
            content = response["result"]["content"][0]["text"]
            results = json.loads(content)
            return results["results"]
        
        return []
    
    def add_zotero_item(self, item_type: str, title: str, creators: List[Dict[str, str]], additional_fields: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Add an item to the Zotero library."""
        response = self._send_request_to_zotero(
            method="call_tool",
            params={
                "name": "add_item",
                "arguments": {
                    "item_type": item_type,
                    "title": title,
                    "creators": creators,
                    "additional_fields": additional_fields or {}
                }
            }
        )
        
        if "result" in response and "content" in response["result"]:
            content = response["result"]["content"][0]["text"]
            result = json.loads(content)
            
            if result.get("success"):
                return result["successful"]["0"]["key"]
        
        return None
    
    def get_zotero_citation(self, item_key: str, style: str = "apa") -> str:
        """Get a citation for an item in the Zotero library."""
        response = self._send_request_to_zotero(
            method="call_tool",
            params={
                "name": "get_citation",
                "arguments": {
                    "item_key": item_key,
                    "style": style
                }
            }
        )
        
        if "result" in response and "content" in response["result"]:
            return response["result"]["content"][0]["text"]
        
        return ""
    
    def get_zotero_bibliography(self, item_keys: List[str], style: str = "apa") -> str:
        """Get a bibliography for items in the Zotero library."""
        response = self._send_request_to_zotero(
            method="call_tool",
            params={
                "name": "get_bibliography",
                "arguments": {
                    "item_keys": item_keys,
                    "style": style
                }
            }
        )
        
        if "result" in response and "content" in response["result"]:
            return response["result"]["content"][0]["text"]
        
        return ""
    
    def get_zotero_collections(self) -> List[Dict[str, Any]]:
        """Get collections from the Zotero library."""
        response = self._send_request_to_zotero(
            method="read_resource",
            params={
                "uri": "zotero://collections"
            }
        )
        
        if "result" in response and "contents" in response["result"]:
            content = response["result"]["contents"][0]["text"]
            return json.loads(content)
        
        return []
    
    def get_zotero_items(self, collection_key: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get items from the Zotero library."""
        if collection_key:
            uri = f"zotero://collections/{collection_key}/items"
        else:
            uri = "zotero://items/top"
        
        response = self._send_request_to_zotero(
            method="read_resource",
            params={
                "uri": uri
            }
        )
        
        if "result" in response and "contents" in response["result"]:
            content = response["result"]["contents"][0]["text"]
            return json.loads(content)
        
        return []
    
    def get_zotero_item(self, item_key: str) -> Optional[Dict[str, Any]]:
        """Get an item from the Zotero library."""
        response = self._send_request_to_zotero(
            method="read_resource",
            params={
                "uri": f"zotero://items/{item_key}"
            }
        )
        
        if "result" in response and "contents" in response["result"]:
            content = response["result"]["contents"][0]["text"]
            return json.loads(content)
        
        return None

# Example usage
if __name__ == "__main__":
    client = MCPClient()
    
    # Search for items
    print("Searching for items...")
    items = client.search_zotero_items("ethics")
    
    if items:
        print(f"Found {len(items)} items:")
        for i, item in enumerate(items[:5]):
            if "data" in item and "title" in item["data"]:
                print(f"  {i+1}. {item['data']['title']}")
    else:
        print("No items found.")
    
    # Get collections
    print("\nGetting collections...")
    collections = client.get_zotero_collections()
    
    if collections:
        print(f"Found {len(collections)} collections:")
        for i, collection in enumerate(collections[:5]):
            if "data" in collection and "name" in collection["data"]:
                print(f"  {i+1}. {collection['data']['name']}")
    else:
        print("No collections found.")
