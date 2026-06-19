"""
MCP Policy Client
-----------------
The bridge the agent uses to talk to the MCP policy server.

It tries to reach the live MCP server over HTTP. If the server isn't
running (e.g. quick local test), it falls back to an embedded copy of
the policy so the demo still works. In a production deployment you would
remove the fallback and require the live server.
"""

import json
import urllib.request
import urllib.error


# Fallback policy, identical to the server's. Used only if the live
# MCP server can't be reached, so the demo never hard-crashes.
_FALLBACK_POLICY = {
    "meals": {"max_amount": 75.00, "receipt_required_above": 25.00},
    "travel": {"max_amount": 2000.00, "receipt_required_above": 50.00},
    "software": {"max_amount": 500.00, "receipt_required_above": 0.00},
    "office_supplies": {"max_amount": 200.00, "receipt_required_above": 50.00},
}


class PolicyMCPClient:
    def __init__(self, server_url="http://localhost:8421"):
        self.server_url = server_url

    def get_policy(self, category: str):
        """Ask the MCP server for the policy on a category."""
        payload = json.dumps({"tool": "get_policy", "category": category}).encode()
        req = urllib.request.Request(
            self.server_url,
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=2) as resp:
                data = json.loads(resp.read())
                return data.get("policy")
        except (urllib.error.URLError, urllib.error.HTTPError, OSError):
            # Server not reachable - use the embedded fallback so the
            # agent can still run.
            return _FALLBACK_POLICY.get(category)
