"""SmartHub MCP Extension."""
from mcp import Server, tool

class SmartHubServer(Server):
    """SmartHub MCP Server."""

    @tool()
    def analyze_merchants(
        self,
        ldap: str,
        analysis_type: str = "net_new"
    ) -> dict:
        """Analyze merchants based on various criteria."""
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
