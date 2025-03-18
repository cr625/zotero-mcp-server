# Integrating Zotero MCP Server with AI Ethical Decision-Making

This guide provides examples of how to integrate the Zotero MCP server with your AI Ethical Decision-Making application.

## Prerequisites

- Zotero MCP server installed and configured
- AI Ethical Decision-Making application

## Integration Examples

### 1. Searching for References Related to Ethical Scenarios

```python
# In your scenario view route
@bp.route("/scenario/<int:id>/references")
def scenario_references(id):
    # Get scenario
    scenario = Scenario.query.get_or_404(id)
    
    # Create a query from the scenario
    query = f"{scenario.name} {scenario.description}"
    
    # Get references from Zotero
    mcp_client = MCPClient()
    references = mcp_client.search_zotero_items(query)
    
    # Render template
    return render_template("scenario_references.html", scenario=scenario, references=references)
```

### 2. Adding Citations to Case Studies

```python
# In your case study creation route
@bp.route("/case_study/create", methods=["GET", "POST"])
def create_case_study():
    form = CaseStudyForm()
    
    if form.validate_on_submit():
        # Create case study
        case_study = CaseStudy(
            title=form.title.data,
            description=form.description.data,
            # ...
        )
        db.session.add(case_study)
        db.session.commit()
        
        # Add citation to Zotero
        mcp_client = MCPClient()
        mcp_client.add_zotero_item(
            item_type="document",
            title=case_study.title,
            creators=[
                {
                    "creatorType": "author",
                    "firstName": current_user.first_name,
                    "lastName": current_user.last_name
                }
            ],
            additional_fields={
                "abstractNote": case_study.description,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "url": url_for("case_study.view", id=case_study.id, _external=True)
            }
        )
        
        flash("Case study created successfully!")
        return redirect(url_for("case_study.view", id=case_study.id))
    
    return render_template("case_study/create.html", form=form)
```

### 3. Generating Bibliographies for Research Papers

```python
# In your research paper view route
@bp.route("/research_paper/<int:id>/bibliography")
def research_paper_bibliography(id):
    # Get research paper
    paper = ResearchPaper.query.get_or_404(id)
    
    # Get references
    references = paper.references
    
    # Get item keys
    item_keys = [ref.zotero_key for ref in references if ref.zotero_key]
    
    # Get bibliography
    mcp_client = MCPClient()
    bibliography = mcp_client.get_zotero_bibliography(item_keys)
    
    # Render template
    return render_template("research_paper/bibliography.html", paper=paper, bibliography=bibliography)
```

## MCP Client Implementation

Here's an example of how to implement the MCP client for your AI Ethical Decision-Making application:

```python
# app/services/mcp_client.py

import json
import subprocess
from typing import List, Dict, Any, Optional

class MCPClient:
    """Client for interacting with MCP servers."""
    
    def __init__(self):
        """Initialize the MCP client."""
        self.zotero_server_path = "/path/to/zotero-mcp-server/src/server.py"
    
    def _send_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
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
    
    def search_zotero_items(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for items in the Zotero library."""
        response = self._send_request(
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
        response = self._send_request(
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
        response = self._send_request(
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
        response = self._send_request(
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
```

## Template Examples

### Scenario References Template

```html
<!-- app/templates/scenario_references.html -->

{% extends "base.html" %}

{% block content %}
<h1>{{ scenario.name }}</h1>
<p>{{ scenario.description }}</p>

<h2>References</h2>
{% if references %}
<ul class="references-list">
    {% for ref in references %}
    <li>
        <h3>{{ ref.data.title }}</h3>
        {% if ref.data.creators %}
        <p>
            {% for creator in ref.data.creators %}
            {{ creator.lastName }}, {{ creator.firstName }}{% if not loop.last %}; {% endif %}
            {% endfor %}
        </p>
        {% endif %}
        {% if ref.data.publicationTitle %}
        <p><em>{{ ref.data.publicationTitle }}</em>, {{ ref.data.volume }}({{ ref.data.issue }}), {{ ref.data.pages }}</p>
        {% endif %}
        {% if ref.data.date %}
        <p>{{ ref.data.date }}</p>
        {% endif %}
        {% if ref.data.abstractNote %}
        <p>{{ ref.data.abstractNote }}</p>
        {% endif %}
    </li>
    {% endfor %}
</ul>
{% else %}
<p>No references found.</p>
{% endif %}
{% endblock %}
```

### Bibliography Template

```html
<!-- app/templates/research_paper/bibliography.html -->

{% extends "base.html" %}

{% block content %}
<h1>{{ paper.title }} - Bibliography</h1>

<div class="bibliography">
    {{ bibliography | safe }}
</div>

<a href="{{ url_for('research_paper.view', id=paper.id) }}" class="btn btn-primary">Back to Paper</a>
{% endblock %}
```

## Conclusion

By integrating the Zotero MCP server with your AI Ethical Decision-Making application, you can provide rich bibliographic functionality to your users, including:

- Searching for relevant references
- Adding citations to case studies
- Generating bibliographies for research papers

This integration enhances the research capabilities of your application and provides a seamless experience for users working with ethical scenarios and case studies.
