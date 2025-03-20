"""Server functions for SmartHub operations."""
from mcp.server.fastmcp import FastMCP
from typing import Dict, List, Optional
from datetime import datetime

# Constants
USER_AGENT = "mcp_smarthub/0.1.0"
BASE_URL = "https://am-hub.sqprod.co/smb"

INSTRUCTIONS = """
SmartHub MCP Server provides tools for analyzing your book of business:

1. Book Analysis:
   - GPV trends and churn risk
   - Product adoption tracking
   - Engagement monitoring

2. Variable Compensation Metrics:
   - GPV Growth & Retention (60%)
   - AR Growth (40%)
   - NNRO Requirements
   - Contract Multiplier Impact

3. Custom Analysis:
   - Save analysis templates
   - Batch analysis
   - Custom merchant segments
"""

mcp = FastMCP("mcp_smarthub", instructions=INSTRUCTIONS)

@mcp.tool()
def analyze_merchants(
    ldap: str,
    analysis_type: str = "gpv_trends",
    time_period: str = "last_90_days",
    filters: Optional[Dict] = None
) -> Dict:
    """
    Analyze merchants based on various criteria.
    
    Args:
        ldap (str): Your LDAP username
        analysis_type (str): Type of analysis:
            - gpv_trends: Analyze GPV patterns
            - churn_risk: Identify churn risks
            - product_opportunities: Find cross-sell opportunities
        time_period (str): Time period for analysis
        filters (dict, optional): Additional filters
    
    Returns:
        dict: Analysis results with count prefix
    """
    try:
        # Example analysis results - we'll replace with real Snowflake queries later
        merchants = [
            {
                "name": "Jimmy O Neil's Whiskey and Alehouse",
                "location_by_city": "Melbourne",
                "industry": "Food and B... Bar club lounge",
                "gpv": {
                    "current": "201K",
                    "previous": "250K",
                    "change_pct": -19.6
                },
                "alerts": ["GPV decline > 15%"],
                "recommended_actions": [
                    "Schedule check-in call",
                    "Review pricing structure",
                    "Discuss marketing tools"
                ]
            }
        ]

        return {
            "ok": True,
            "analysis_type": analysis_type,
            "time_period": time_period,
            "results": {
                "total_found": len(merchants),  # Count prefix
                "merchants": merchants,
                "summary": {
                    "total_analyzed": len(merchants),
                    "timestamp": datetime.now().isoformat()
                }
            },
            "web_url": f"{BASE_URL}/focus?ldap={ldap}"
        }

    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "error_type": "unexpected",
            "request_id": datetime.now().isoformat()  # For tracking issues
        }

@mcp.tool()
def get_variable_comp_metrics(
    ldap: str,
    quarter: str = "current"
) -> Dict:
    """
    Get variable compensation metrics tracking.
    
    Args:
        ldap (str): Your LDAP username
        quarter (str): Which quarter to analyze (current, previous, ytd)
    
    Returns:
        dict: Variable compensation metrics and progress
    """
    try:
        return {
            "ok": True,
            "quarter": quarter,
            "metrics": {
                "gpv_growth": {
                    "weight": "60%",
                    "current_progress": "15%",
                    "target": "20%",
                    "at_risk_gpv": "1.2M",
                    "opportunities": [
                        {
                            "merchant": "Jimmy O Neil's",
                            "potential_impact": "$50K",
                            "recommended_actions": [
                                "Review pricing structure",
                                "Discuss marketing tools"
                            ]
                        }
                    ]
                },
                "ar_growth": {
                    "weight": "40%",
                    "current_progress": "25%",
                    "target": "30%",
                    "opportunities": [
                        {
                            "merchant": "Jervis Bay Seafish",
                            "product": "Square Online",
                            "potential_ar": "$5K"
                        }
                    ]
                },
                "nnro_progress": {
                    "completed": 45,
                    "target": 60,
                    "remaining_days": 15,
                    "pace": "On track"
                }
            },
            "web_url": f"{BASE_URL}/focus?ldap={ldap}"
        }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "error_type": "unexpected",
            "request_id": datetime.now().isoformat()
        }
