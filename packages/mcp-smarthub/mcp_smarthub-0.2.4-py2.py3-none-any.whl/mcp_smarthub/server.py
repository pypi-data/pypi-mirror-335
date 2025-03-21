"""Server functions for SmartHub operations."""
from typing import Optional, Dict
from mcp.server.fastmcp import FastMCP

# Update the instructions for your MCP server
instructions = """
SmartHub MCP Server provides tools for analyzing your book of business:

1. Book Analysis:
   - GPV trends and churn risk
   - Product adoption tracking
   - Engagement monitoring

2. Variable Compensation Metrics:
   - GPV Growth & Retention (60%)
   - AR Growth (40%)
   - NNRO Requirements
""".strip()

# Create an MCP server
mcp = FastMCP("mcp_smarthub", instructions=instructions)

@mcp.tool()
def analyze_merchants(
    ldap: str,
    analysis_type: str = "net_new",
    filters: Optional[Dict] = None
) -> dict:
    """
    Analyze merchants based on various criteria.
    
    Args:
        ldap (str): Your LDAP username
        analysis_type (str): Type of analysis:
            - net_new: New merchants in your book
            - gpv_trends: GPV patterns analysis
        filters (dict, optional): Additional filters
    
    Returns:
        dict: Analysis results including merchant list and summary
    """
    merchants = [
        {
            "name": "Jimmy O Neil's Whiskey and Alehouse",
            "location_by_city": "Melbourne",
            "industry": "Food and B... Bar club lounge",
            "gpv": {
                "current": "201K",
                "previous": "250K",
                "change_pct": -19.6
            }
        }
    ]

    return {
        "ok": True,
        "merchants": merchants,
        "web_url": f"https://am-hub.sqprod.co/smb/focus?ldap={ldap}"
    }
