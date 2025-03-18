# Zotero MCP Server

A Model Context Protocol (MCP) server that integrates with Zotero, allowing AI applications to access and manipulate Zotero libraries.

## Features

- Search for items in Zotero libraries
- Get citations and bibliographies
- Add new items to Zotero libraries
- Access collections and items
- Support for both personal and group libraries

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/zotero-mcp-server.git
   cd zotero-mcp-server
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Linux/macOS:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file with your Zotero API credentials:
   ```
   ZOTERO_API_KEY=your_api_key_here
   ZOTERO_USER_ID=your_numeric_user_id_here
   # ZOTERO_GROUP_ID=your_group_id_here  # Uncomment to use a group library
   ```

   You need to set either `ZOTERO_USER_ID` (for personal libraries) or `ZOTERO_GROUP_ID` (for group libraries).

3. If you're not sure how to find your Zotero user ID, run:
   ```bash
   ./find_zotero_id.py
   ```

## Usage

### Running the Server

```bash
python src/server.py
```

The server will start and listen for JSON-RPC requests on standard input/output.

### Testing the Server

```bash
./simple_test.py
```

This will run a series of tests to verify that the server is working correctly.

### Integration with AI Applications

The Zotero MCP server can be integrated with AI applications that support the Model Context Protocol. See the `USAGE_GUIDE.md` file for detailed examples.

## Available Resources

- `zotero://collections`: List of collections in the Zotero library
- `zotero://items/top`: Top-level items in the Zotero library
- `zotero://items/recent`: Recently added or modified items in the Zotero library
- `zotero://collections/{collection_key}/items`: Items in a specific Zotero collection
- `zotero://items/{item_key}`: Details of a specific Zotero item
- `zotero://items/{item_key}/citation/{style}`: Citation for a specific Zotero item in a specific style

## Available Tools

- `search_items`: Search for items in the Zotero library
- `get_citation`: Get citation for a specific item
- `add_item`: Add a new item to the Zotero library
- `get_bibliography`: Get bibliography for multiple items

## Documentation

For more detailed information, see:

- `USAGE_GUIDE.md`: Comprehensive usage guide
- `test_client.py`: Interactive test client
- `simple_test.py`: Simple test script
- `find_zotero_id.py`: Helper script to find your Zotero IDs

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
