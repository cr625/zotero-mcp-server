# Zotero MCP Server Usage Guide

This guide provides detailed instructions on how to set up, run, and use the Zotero MCP server with your AI Ethical Decision-Making application.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Running the Server](#running-the-server)
5. [Testing the Server](#testing-the-server)
6. [Integration with AI Ethical Decision-Making](#integration-with-ai-ethical-decision-making)
7. [Advanced Usage](#advanced-usage)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

Before using the Zotero MCP server, you need:

- Python 3.7 or higher
- A Zotero account
- A Zotero API key
- Your Zotero user ID or group ID

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
   # Get your API key from https://www.zotero.org/settings/keys
   ZOTERO_API_KEY=your_api_key_here

   # Your Zotero user ID (for personal libraries)
   # Find this in your Zotero profile URL: https://www.zotero.org/[user_id]
   ZOTERO_USER_ID=your_user_id_here

   # Your Zotero group ID (for group libraries, optional)
   # Find this in your Zotero group URL: https://www.zotero.org/groups/[group_id]
   # ZOTERO_GROUP_ID=your_group_id_here
   ```

   You need to set either `ZOTERO_USER_ID` (for personal libraries) or `ZOTERO_GROUP_ID` (for group libraries).

3. Make sure your Zotero API key has the appropriate permissions:
   - For read-only access: Read permissions for your library
   - For full access: Read/Write permissions for your library

## Running the Server

To run the Zotero MCP server:

```bash
# Activate the virtual environment if not already activated
source venv/bin/activate

# Run the server
python src/server.py
```

The server will start and listen for JSON-RPC requests on standard input/output. You should see output similar to:

```
2025-03-17 19:42:21 - zotero-mcp-server - INFO - Initialized Zotero client for group 5915619
2025-03-17 19:42:21 - zotero-mcp-server - INFO - Zotero MCP server running on stdio
```

## Testing the Server

### Using the Test Client

The repository includes a test client that you can use to test the server's functionality:

```bash
# In a new terminal, activate the virtual environment
source venv/bin/activate

# Run the test client
python test_client.py
```

The test client provides a menu-driven interface to test various server functions:

1. List resources
2. List tools
3. Search items
4. Get recent items
5. Add a new item

Follow the on-screen instructions to test each function.

### Manual Testing

You can also test the server manually by sending JSON-RPC requests directly to the server's standard input. For example:

```json
{"jsonrpc": "2.0", "method": "list_resources", "params": {}, "id": 1}
```

The server will respond with a JSON-RPC response on standard output.

## Integration with AI Ethical Decision-Making

To integrate the Zotero MCP server with your AI Ethical Decision-Making application, you have two options:

### Option 1: Modify the Existing MCP Client

You can modify the existing MCP client in your application to support the Zotero MCP server. See the `mcp_client_integration.py` file for an example of how to do this.

Key changes include:

1. Adding support for multiple server types
2. Adding methods to interact with the Zotero MCP server
3. Using the Zotero MCP server in your application

### Option 2: Use a Separate Zotero MCP Client

Alternatively, you can use a separate client for the Zotero MCP server. See the `integration_example.py` file for an example of how to do this.

### Example Integration

Here's an example of how to use the Zotero MCP server in your application:

```python
# Get references for a scenario
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
```

See the `integration_with_ethical_dm.md` file for more detailed examples.

## Advanced Usage

### Running the Server in the Background

To run the server in the background, you can use a process manager like `supervisor` or `systemd`. Here's an example `systemd` service file:

```ini
[Unit]
Description=Zotero MCP Server
After=network.target

[Service]
User=your_username
WorkingDirectory=/path/to/zotero-mcp-server
ExecStart=/path/to/zotero-mcp-server/venv/bin/python src/server.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### Using Different Zotero Libraries

You can configure the server to use different Zotero libraries by setting the appropriate environment variables:

- For personal libraries, set `ZOTERO_USER_ID`
- For group libraries, set `ZOTERO_GROUP_ID`

You can also create multiple configuration files for different libraries and specify which one to use when starting the server:

```bash
DOTENV_PATH=/path/to/config.env python src/server.py
```

## Troubleshooting

### Common Issues

1. **Authentication Errors**:
   - Make sure your API key is correct and has the appropriate permissions
   - Check that you've set either `ZOTERO_USER_ID` or `ZOTERO_GROUP_ID` correctly

2. **Connection Issues**:
   - Check your internet connection
   - Verify that the Zotero API is available (https://api.zotero.org)

3. **Permission Issues**:
   - Ensure your API key has the necessary permissions for the operations you're trying to perform

### Debugging

To enable more detailed logging, you can set the `LOGLEVEL` environment variable:

```bash
LOGLEVEL=DEBUG python src/server.py
```

This will output more detailed information about the server's operations, which can help diagnose issues.

### Getting Help

If you encounter issues that aren't covered in this guide, you can:

1. Check the Zotero API documentation: https://www.zotero.org/support/dev/web_api/v3/start
2. Check the pyzotero documentation: https://pyzotero.readthedocs.io/
3. Open an issue on the GitHub repository
