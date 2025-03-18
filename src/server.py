#!/usr/bin/env python3
import json
import os
import sys
import asyncio
import logging
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from pyzotero import zotero

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger('zotero-mcp-server')

# Load environment variables
load_dotenv()

class ZoteroMCPServer:
    """MCP server for Zotero integration."""
    
    def __init__(self):
        """Initialize the MCP server."""
        self.jsonrpc_id = 0
        
        # Get Zotero API credentials from environment variables
        self.api_key = os.getenv('ZOTERO_API_KEY')
        self.user_id = os.getenv('ZOTERO_USER_ID')
        self.group_id = os.getenv('ZOTERO_GROUP_ID')
        
        # Initialize Zotero client
        self._init_zotero_client()
    
    def _init_zotero_client(self):
        """Initialize the Zotero client."""
        if not self.api_key:
            logger.error("ZOTERO_API_KEY environment variable not set")
            self.zot = None
            return
        
        try:
            # Prioritize user library over group library
            if self.user_id:
                # User library
                self.zot = zotero.Zotero(self.user_id, 'user', self.api_key)
                logger.info(f"Initialized Zotero client for user {self.user_id}")
                # Clear group_id to ensure we don't use it
                self.group_id = None
            elif self.group_id:
                # Group library
                self.zot = zotero.Zotero(self.group_id, 'group', self.api_key)
                logger.info(f"Initialized Zotero client for group {self.group_id}")
            else:
                logger.error("Either ZOTERO_USER_ID or ZOTERO_GROUP_ID must be set")
                self.zot = None
        except Exception as e:
            logger.error(f"Error initializing Zotero client: {str(e)}")
            self.zot = None
    
    async def run(self):
        """Run the MCP server."""
        logger.info("Zotero MCP server running on stdio")
        
        # Process stdin/stdout
        while True:
            try:
                # Read request from stdin
                request_line = await self._read_line()
                if not request_line:
                    continue
                
                # Parse request
                request = json.loads(request_line)
                
                # Process request
                response = await self._process_request(request)
                
                # Send response
                print(json.dumps(response), flush=True)
            except Exception as e:
                logger.error(f"Error processing request: {str(e)}")
                # Send error response
                error_response = {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32000,
                        "message": f"Internal error: {str(e)}"
                    },
                    "id": self.jsonrpc_id
                }
                print(json.dumps(error_response), flush=True)
    
    async def _read_line(self):
        """Read a line from stdin."""
        return sys.stdin.readline().strip()
    
    async def _process_request(self, request):
        """Process a JSON-RPC request."""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        self.jsonrpc_id = request_id
        
        # Process method
        if method == "list_resources":
            result = await self._handle_list_resources(params)
        elif method == "list_resource_templates":
            result = await self._handle_list_resource_templates(params)
        elif method == "read_resource":
            result = await self._handle_read_resource(params)
        elif method == "list_tools":
            result = await self._handle_list_tools(params)
        elif method == "call_tool":
            result = await self._handle_call_tool(params)
        else:
            # Method not found
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                },
                "id": request_id
            }
        
        # Return result
        return {
            "jsonrpc": "2.0",
            "result": result,
            "id": request_id
        }
    
    async def _handle_list_resources(self, params):
        """Handle request to list available resources."""
        return {
            "resources": [
                {
                    "uri": "zotero://collections",
                    "name": "Zotero Collections",
                    "mimeType": "application/json",
                    "description": "List of collections in the Zotero library"
                },
                {
                    "uri": "zotero://items/top",
                    "name": "Top-Level Items",
                    "mimeType": "application/json",
                    "description": "Top-level items in the Zotero library"
                },
                {
                    "uri": "zotero://items/recent",
                    "name": "Recent Items",
                    "mimeType": "application/json",
                    "description": "Recently added or modified items in the Zotero library"
                }
            ]
        }
    
    async def _handle_list_resource_templates(self, params):
        """Handle request to list available resource templates."""
        return {
            "resourceTemplates": [
                {
                    "uriTemplate": "zotero://collections/{collection_key}/items",
                    "name": "Collection Items",
                    "mimeType": "application/json",
                    "description": "Items in a specific Zotero collection"
                },
                {
                    "uriTemplate": "zotero://items/{item_key}",
                    "name": "Item Details",
                    "mimeType": "application/json",
                    "description": "Details of a specific Zotero item"
                },
                {
                    "uriTemplate": "zotero://items/{item_key}/citation/{style}",
                    "name": "Item Citation",
                    "mimeType": "text/plain",
                    "description": "Citation for a specific Zotero item in a specific style"
                }
            ]
        }
    
    async def _handle_read_resource(self, params):
        """Handle request to read a resource."""
        uri = params.get("uri")
        
        if not self.zot:
            return {
                "error": {
                    "code": -32000,
                    "message": "Zotero client not initialized. Check API credentials."
                }
            }
        
        try:
            # Handle static resources
            if uri == "zotero://collections":
                collections = self.zot.collections()
                return {
                    "contents": [
                        {
                            "uri": uri,
                            "mimeType": "application/json",
                            "text": json.dumps(collections, indent=2)
                        }
                    ]
                }
            elif uri == "zotero://items/top":
                items = self.zot.top(limit=50)
                return {
                    "contents": [
                        {
                            "uri": uri,
                            "mimeType": "application/json",
                            "text": json.dumps(items, indent=2)
                        }
                    ]
                }
            elif uri == "zotero://items/recent":
                items = self.zot.items(limit=20, sort="dateModified", direction="desc")
                return {
                    "contents": [
                        {
                            "uri": uri,
                            "mimeType": "application/json",
                            "text": json.dumps(items, indent=2)
                        }
                    ]
                }
            
            # Handle resource templates
            if uri.startswith("zotero://collections/") and uri.endswith("/items"):
                collection_key = uri.split("/")[2]
                items = self.zot.collection_items(collection_key)
                return {
                    "contents": [
                        {
                            "uri": uri,
                            "mimeType": "application/json",
                            "text": json.dumps(items, indent=2)
                        }
                    ]
                }
            elif uri.startswith("zotero://items/") and "/citation/" in uri:
                parts = uri.split("/")
                item_key = parts[2]
                style = parts[4]
                citation = self.zot.item(item_key, format="citation", style=style)
                return {
                    "contents": [
                        {
                            "uri": uri,
                            "mimeType": "text/plain",
                            "text": citation
                        }
                    ]
                }
            elif uri.startswith("zotero://items/") and len(uri.split("/")) == 3:
                item_key = uri.split("/")[2]
                item = self.zot.item(item_key)
                return {
                    "contents": [
                        {
                            "uri": uri,
                            "mimeType": "application/json",
                            "text": json.dumps(item, indent=2)
                        }
                    ]
                }
            
            # Resource not found
            return {
                "error": {
                    "code": -32602,
                    "message": f"Resource not found: {uri}"
                }
            }
        except Exception as e:
            logger.error(f"Error reading resource {uri}: {str(e)}")
            return {
                "error": {
                    "code": -32000,
                    "message": f"Error reading resource: {str(e)}"
                }
            }
    
    async def _handle_list_tools(self, params):
        """Handle request to list available tools."""
        return {
            "tools": [
                {
                    "name": "search_items",
                    "description": "Search for items in the Zotero library",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query"
                            },
                            "collection_key": {
                                "type": "string",
                                "description": "Collection key to search in (optional)"
                            },
                            "limit": {
                                "type": "number",
                                "description": "Maximum number of results to return"
                            }
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "get_citation",
                    "description": "Get citation for a specific item",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "item_key": {
                                "type": "string",
                                "description": "Item key"
                            },
                            "style": {
                                "type": "string",
                                "description": "Citation style (e.g., apa, mla, chicago)",
                                "default": "apa"
                            }
                        },
                        "required": ["item_key"]
                    }
                },
                {
                    "name": "add_item",
                    "description": "Add a new item to the Zotero library",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "item_type": {
                                "type": "string",
                                "description": "Item type (e.g., journal, book, webpage)"
                            },
                            "title": {
                                "type": "string",
                                "description": "Item title"
                            },
                            "creators": {
                                "type": "array",
                                "description": "Item creators (authors, editors, etc.)",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "creatorType": {
                                            "type": "string",
                                            "description": "Creator type (e.g., author, editor)"
                                        },
                                        "firstName": {
                                            "type": "string",
                                            "description": "Creator first name"
                                        },
                                        "lastName": {
                                            "type": "string",
                                            "description": "Creator last name"
                                        }
                                    },
                                    "required": ["creatorType", "lastName"]
                                }
                            },
                            "collection_key": {
                                "type": "string",
                                "description": "Collection key to add the item to (optional)"
                            },
                            "additional_fields": {
                                "type": "object",
                                "description": "Additional fields for the item (e.g., date, url, publisher)"
                            }
                        },
                        "required": ["item_type", "title"]
                    }
                },
                {
                    "name": "get_bibliography",
                    "description": "Get bibliography for multiple items",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "item_keys": {
                                "type": "array",
                                "description": "Array of item keys",
                                "items": {
                                    "type": "string"
                                }
                            },
                            "style": {
                                "type": "string",
                                "description": "Citation style (e.g., apa, mla, chicago)",
                                "default": "apa"
                            }
                        },
                        "required": ["item_keys"]
                    }
                }
            ]
        }
    
    async def _handle_call_tool(self, params):
        """Handle request to call a tool."""
        tool_name = params.get("name")
        args = params.get("arguments", {})
        
        if not self.zot:
            return {
                "error": {
                    "code": -32000,
                    "message": "Zotero client not initialized. Check API credentials."
                }
            }
        
        try:
            if tool_name == "search_items":
                if "query" not in args:
                    return {
                        "error": {
                            "code": -32602,
                            "message": "Missing required parameter: query"
                        }
                    }
                
                query = args["query"]
                collection_key = args.get("collection_key")
                limit = args.get("limit", 20)
                
                search_params = {"q": query, "limit": limit}
                
                if collection_key:
                    items = self.zot.collection_items_top(collection_key, **search_params)
                else:
                    items = self.zot.items(**search_params)
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({
                                "query": query,
                                "results": items
                            }, indent=2)
                        }
                    ]
                }
            
            elif tool_name == "get_citation":
                if "item_key" not in args:
                    return {
                        "error": {
                            "code": -32602,
                            "message": "Missing required parameter: item_key"
                        }
                    }
                
                item_key = args["item_key"]
                style = args.get("style", "apa")
                
                citation = self.zot.item(item_key, format="citation", style=style)
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": citation
                        }
                    ]
                }
            
            elif tool_name == "add_item":
                if "item_type" not in args or "title" not in args:
                    return {
                        "error": {
                            "code": -32602,
                            "message": "Missing required parameters: item_type and title"
                        }
                    }
                
                item_type = args["item_type"]
                title = args["title"]
                creators = args.get("creators", [])
                collection_key = args.get("collection_key")
                additional_fields = args.get("additional_fields", {})
                
                # Create item template
                template = self.zot.item_template(item_type)
                
                # Set title
                template["title"] = title
                
                # Set creators
                if creators:
                    template["creators"] = creators
                
                # Set additional fields
                for key, value in additional_fields.items():
                    template[key] = value
                
                # Create item
                response = self.zot.create_items([template])
                
                # Add to collection if specified
                if collection_key and response.get("success"):
                    item_key = response["successful"]["0"]["key"]
                    self.zot.addto_collection(collection_key, [item_key])
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(response, indent=2)
                        }
                    ]
                }
            
            elif tool_name == "get_bibliography":
                if "item_keys" not in args:
                    return {
                        "error": {
                            "code": -32602,
                            "message": "Missing required parameter: item_keys"
                        }
                    }
                
                item_keys = args["item_keys"]
                style = args.get("style", "apa")
                
                # Get bibliography
                bibliography = self.zot.bibliography(item_keys, style=style)
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": bibliography
                        }
                    ]
                }
            
            else:
                return {
                    "error": {
                        "code": -32601,
                        "message": f"Unknown tool: {tool_name}"
                    }
                }
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {str(e)}")
            return {
                "error": {
                    "code": -32000,
                    "message": f"Error calling tool: {str(e)}"
                }
            }

def main():
    """Main entry point for the console script."""
    server = ZoteroMCPServer()
    asyncio.run(server.run())

# Main entry point
if __name__ == "__main__":
    main()
