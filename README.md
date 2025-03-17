# Zotero MCP Server

A Model Context Protocol (MCP) server that integrates with Zotero for academic reference management.

## Overview

This MCP server provides tools and resources for accessing and managing academic references from Zotero. It can be used to:

- Search for references in a Zotero library
- Retrieve reference details
- Get citations in various formats
- Add references to a Zotero library
- Organize references into collections

## Installation

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure your Zotero API key (see Configuration section)

## Configuration

The server requires a Zotero API key to access your Zotero library. You can obtain an API key from the [Zotero settings page](https://www.zotero.org/settings/keys).

Set the following environment variables:

- `ZOTERO_API_KEY`: Your Zotero API key
- `ZOTERO_USER_ID`: Your Zotero user ID (for personal libraries)
- `ZOTERO_GROUP_ID`: Your Zotero group ID (for group libraries, optional)

## Usage

Run the server:

```bash
python src/server.py
```

The server communicates using JSON-RPC over stdio, following the Model Context Protocol.

## Integration with AI Ethical Decision-Making Simulator

This server can be integrated with the AI Ethical Decision-Making Simulator by adding it to the MCP client configuration.

## License

MIT
