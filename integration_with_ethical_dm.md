# Integrating Zotero MCP Server with AI Ethical Decision-Making Application

This document provides instructions for integrating the Zotero MCP server with the existing AI Ethical Decision-Making application.

## Overview

The Zotero MCP server provides tools and resources for accessing and managing academic references from Zotero. By integrating it with the AI Ethical Decision-Making application, you can:

1. Search for academic references related to ethical scenarios
2. Retrieve citations for references
3. Add references to a Zotero library
4. Generate bibliographies for ethical case studies

## Installation

1. Clone the Zotero MCP server repository:
   ```bash
   git clone https://github.com/your-username/zotero-mcp-server.git
   ```

2. Install dependencies:
   ```bash
   cd zotero-mcp-server
   pip install -r requirements.txt
   ```

3. Configure your Zotero API credentials:
   - Copy `.env.example` to `.env`
   - Edit `.env` to add your Zotero API key, user ID, and optionally group ID

## Configuration

To integrate the Zotero MCP server with the AI Ethical Decision-Making application, you need to modify the MCP client configuration.

### Option 1: Add Zotero MCP Server to Existing MCP Client

Modify the `app/services/mcp_client.py` file to add methods for interacting with the Zotero MCP server:

```python
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
```

### Option 2: Use a Separate Zotero MCP Client

Alternatively, you can use the `ZoteroMCPClient` class from `integration_example.py` as a separate client for interacting with the Zotero MCP server.

## Usage Examples

### Example 1: Search for References Related to a Scenario

```python
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
```

### Example 2: Add References to a Case Study

```python
# In app/routes/cases.py

@bp.route("/case/<int:id>/add_reference", methods=["POST"])
def add_reference_to_case(id):
    # Get case
    case = Case.query.get_or_404(id)
    
    # Get form data
    title = request.form.get("title")
    authors = request.form.get("authors")
    journal = request.form.get("journal")
    year = request.form.get("year")
    
    # Parse authors
    creators = []
    for author in authors.split(";"):
        if author.strip():
            parts = author.strip().split(",")
            if len(parts) >= 2:
                creators.append({
                    "creatorType": "author",
                    "lastName": parts[0].strip(),
                    "firstName": parts[1].strip()
                })
    
    # Add reference to Zotero
    mcp_client = MCPClient()
    response = mcp_client.add_item(
        item_type="journalArticle",
        title=title,
        creators=creators,
        additional_fields={
            "publicationTitle": journal,
            "date": year
        }
    )
    
    # Add reference to case
    if response.get("success"):
        item_key = response["successful"]["0"]["key"]
        citation = mcp_client.get_zotero_citation(item_key)
        
        # Save citation to case
        case.references = case.references or []
        case.references.append({
            "item_key": item_key,
            "citation": citation
        })
        db.session.commit()
        
        flash("Reference added successfully", "success")
    else:
        flash("Error adding reference", "error")
    
    return redirect(url_for("cases.case_detail", id=id))
```

### Example 3: Generate Bibliography for a Case Study

```python
# In app/routes/cases.py

@bp.route("/case/<int:id>/bibliography")
def case_bibliography(id):
    # Get case
    case = Case.query.get_or_404(id)
    
    # Get reference item keys
    item_keys = [ref["item_key"] for ref in case.references or []]
    
    if not item_keys:
        flash("No references found", "warning")
        return redirect(url_for("cases.case_detail", id=id))
    
    # Get bibliography
    mcp_client = MCPClient()
    bibliography = mcp_client.get_bibliography(item_keys)
    
    # Render template
    return render_template("case_bibliography.html", case=case, bibliography=bibliography)
```

## Template Examples

### Example 1: Scenario References Template

```html
<!-- app/templates/scenario_references.html -->
{% extends "base.html" %}

{% block content %}
<h1>References for {{ scenario.name }}</h1>

<div class="card mb-4">
    <div class="card-header">
        <h2>Scenario Details</h2>
    </div>
    <div class="card-body">
        <p><strong>Name:</strong> {{ scenario.name }}</p>
        <p><strong>Description:</strong> {{ scenario.description }}</p>
    </div>
</div>

<div class="card">
    <div class="card-header">
        <h2>Related References</h2>
    </div>
    <div class="card-body">
        {% if references.results %}
            <ul class="list-group">
                {% for item in references.results %}
                    <li class="list-group-item">
                        <h5>{{ item.data.title }}</h5>
                        {% if item.data.creators %}
                            <p>
                                <strong>Authors:</strong>
                                {% for creator in item.data.creators %}
                                    {{ creator.lastName }}, {{ creator.firstName }}{% if not loop.last %}; {% endif %}
                                {% endfor %}
                            </p>
                        {% endif %}
                        {% if item.data.publicationTitle %}
                            <p><strong>Journal:</strong> {{ item.data.publicationTitle }}</p>
                        {% endif %}
                        {% if item.data.date %}
                            <p><strong>Date:</strong> {{ item.data.date }}</p>
                        {% endif %}
                        <a href="#" class="btn btn-primary btn-sm">Add to Case</a>
                    </li>
                {% endfor %}
            </ul>
        {% else %}
            <p>No references found.</p>
        {% endif %}
    </div>
</div>
{% endblock %}
```

## Conclusion

By integrating the Zotero MCP server with the AI Ethical Decision-Making application, you can enhance the application with academic reference management capabilities. This integration allows users to search for relevant references, add them to case studies, and generate bibliographies, making the application more useful for academic and research purposes.
