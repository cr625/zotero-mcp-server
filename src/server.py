#!/usr/bin/env python3
"""
Zotero MCP Server - Model Context Protocol server for Zotero integration.

This server provides tools and resources for interacting with Zotero libraries,
using the latest MCP paradigms and the official Python SDK.
"""

import os
import sys
import json
import logging
from typing import Any, Optional
from dotenv import load_dotenv
from pyzotero import zotero
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger('zotero-mcp-server')

# Load environment variables
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("Zotero MCP Server")

# Global Zotero client instance
zot: Optional[zotero.Zotero] = None


def init_zotero_client():
    """Initialize the Zotero client with credentials from environment."""
    global zot

    api_key = os.getenv('ZOTERO_API_KEY')
    user_id = os.getenv('ZOTERO_USER_ID')
    group_id = os.getenv('ZOTERO_GROUP_ID')

    if not api_key:
        logger.error("ZOTERO_API_KEY environment variable not set")
        return

    try:
        # Prioritize user library over group library
        if user_id:
            zot = zotero.Zotero(user_id, 'user', api_key)
            logger.info(f"Initialized Zotero client for user {user_id}")
        elif group_id:
            zot = zotero.Zotero(group_id, 'group', api_key)
            logger.info(f"Initialized Zotero client for group {group_id}")
        else:
            logger.error("Either ZOTERO_USER_ID or ZOTERO_GROUP_ID must be set")
    except Exception as e:
        logger.error(f"Error initializing Zotero client: {str(e)}")


def ensure_client():
    """Ensure Zotero client is initialized."""
    if zot is None:
        raise RuntimeError("Zotero client not initialized. Check API credentials.")


# ============================================================================
# RESOURCES - Read-only data access
# ============================================================================

@mcp.resource("zotero://collections")
def get_collections() -> str:
    """List of collections in the Zotero library."""
    ensure_client()
    collections = zot.collections()
    return json.dumps(collections, indent=2)


@mcp.resource("zotero://items/top")
def get_top_items() -> str:
    """Top-level items in the Zotero library."""
    ensure_client()
    items = zot.top(limit=50)
    return json.dumps(items, indent=2)


@mcp.resource("zotero://items/recent")
def get_recent_items() -> str:
    """Recently added or modified items in the Zotero library."""
    ensure_client()
    items = zot.items(limit=20, sort="dateModified", direction="desc")
    return json.dumps(items, indent=2)


@mcp.resource("zotero://collections/{collection_key}/items")
def get_collection_items(collection_key: str) -> str:
    """Items in a specific Zotero collection."""
    ensure_client()
    items = zot.collection_items(collection_key)
    return json.dumps(items, indent=2)


@mcp.resource("zotero://items/{item_key}")
def get_item(item_key: str) -> str:
    """Details of a specific Zotero item."""
    ensure_client()
    item = zot.item(item_key)
    return json.dumps(item, indent=2)


@mcp.resource("zotero://items/{item_key}/citation/{style}")
def get_item_citation(item_key: str, style: str) -> str:
    """Citation for a specific Zotero item in a specific style."""
    ensure_client()
    citation = zot.item(item_key, format="citation", style=style)
    return citation


# ============================================================================
# TOOLS - Actions and operations
# ============================================================================

@mcp.tool()
def search_items(
    query: str,
    collection_key: Optional[str] = None,
    limit: int = 20
) -> str:
    """
    Search for items in the Zotero library.

    Args:
        query: Search query string
        collection_key: Optional collection key to search within
        limit: Maximum number of results to return (default: 20)

    Returns:
        JSON string containing search results
    """
    ensure_client()

    search_params = {"q": query, "limit": limit}

    if collection_key:
        items = zot.collection_items_top(collection_key, **search_params)
    else:
        items = zot.items(**search_params)

    result = {
        "query": query,
        "count": len(items),
        "results": items
    }

    return json.dumps(result, indent=2)


@mcp.tool()
def get_citation(item_key: str, style: str = "apa") -> str:
    """
    Get citation for a specific item.

    Args:
        item_key: The Zotero item key
        style: Citation style (e.g., apa, mla, chicago). Default: apa

    Returns:
        Formatted citation string
    """
    ensure_client()
    citation = zot.item(item_key, format="citation", style=style)
    return citation


@mcp.tool()
def add_item(
    item_type: str,
    title: str,
    creators: Optional[list[dict[str, str]]] = None,
    collection_key: Optional[str] = None,
    additional_fields: Optional[dict[str, Any]] = None
) -> str:
    """
    Add a new item to the Zotero library.

    Args:
        item_type: Item type (e.g., journalArticle, book, webpage)
        title: Item title
        creators: List of creators with format [{"creatorType": "author", "firstName": "...", "lastName": "..."}]
        collection_key: Optional collection key to add the item to
        additional_fields: Additional fields (e.g., date, url, publisher)

    Returns:
        JSON string with creation response
    """
    ensure_client()

    # Create item template
    template = zot.item_template(item_type)

    # Set title
    template["title"] = title

    # Set creators
    if creators:
        template["creators"] = creators

    # Set additional fields
    if additional_fields:
        for key, value in additional_fields.items():
            template[key] = value

    # Create item
    response = zot.create_items([template])

    # Add to collection if specified
    if collection_key and response.get("success"):
        item_key = response["successful"]["0"]["key"]
        zot.addto_collection(collection_key, [item_key])

    return json.dumps(response, indent=2)


@mcp.tool()
def get_bibliography(item_keys: list[str], style: str = "apa") -> str:
    """
    Get bibliography for multiple items.

    Args:
        item_keys: List of Zotero item keys
        style: Citation style (e.g., apa, mla, chicago). Default: apa

    Returns:
        Formatted bibliography string
    """
    ensure_client()
    bibliography = zot.bibliography(item_keys, style=style)
    return bibliography


@mcp.tool()
def create_collection(name: str, parent_key: Optional[str] = None) -> str:
    """
    Create a new collection in the Zotero library.

    Args:
        name: Name of the new collection
        parent_key: Optional parent collection key for nested collections

    Returns:
        JSON string with creation response
    """
    ensure_client()

    collection_data = {"name": name}
    if parent_key:
        collection_data["parentCollection"] = parent_key

    response = zot.create_collections([collection_data])
    return json.dumps(response, indent=2)


@mcp.tool()
def update_item(
    item_key: str,
    updates: dict[str, Any]
) -> str:
    """
    Update an existing item in the Zotero library.

    Args:
        item_key: The Zotero item key to update
        updates: Dictionary of fields to update

    Returns:
        JSON string with update response
    """
    ensure_client()

    # Get the existing item
    item = zot.item(item_key)

    # Update fields
    for key, value in updates.items():
        item[key] = value

    # Update the item
    response = zot.update_item(item)
    return json.dumps(response, indent=2)


@mcp.tool()
def delete_item(item_key: str) -> str:
    """
    Delete an item from the Zotero library.

    Args:
        item_key: The Zotero item key to delete

    Returns:
        Success message
    """
    ensure_client()

    # Get item version for deletion
    item = zot.item(item_key)
    version = item.get('version')

    # Delete the item
    zot.delete_item(item, version=version)

    return json.dumps({"success": True, "message": f"Item {item_key} deleted"})


@mcp.tool()
def get_item_types() -> str:
    """
    Get list of all available Zotero item types.

    Returns:
        JSON string containing all item types
    """
    ensure_client()
    item_types = zot.item_types()
    return json.dumps(item_types, indent=2)


@mcp.tool()
def get_item_fields(item_type: str) -> str:
    """
    Get available fields for a specific item type.

    Args:
        item_type: The item type to get fields for (e.g., journalArticle, book)

    Returns:
        JSON string containing available fields
    """
    ensure_client()
    fields = zot.item_type_fields(item_type)
    return json.dumps(fields, indent=2)


def main():
    """Main entry point for the server."""
    logger.info("Starting Zotero MCP Server")

    # Initialize Zotero client
    init_zotero_client()

    # Run the MCP server (stdio transport by default)
    mcp.run()


if __name__ == "__main__":
    main()
