"""
MCP Policy Server
-----------------
A Model Context Protocol (MCP) server that exposes company expense
policy rules as a queryable tool. The triage agent connects to this
server to look up spending limits and receipt requirements per category,
instead of hard-coding them.

This mirrors the MCP pattern from the course (Day 2): an agent connecting
to an external server for grounded, real-time data instead of relying on
training data.

Run standalone with:  python mcp_policy_server.py
"""

import json
from http.server import HTTPServer, BaseHTTPRequestHandler


# The company expense policy. In a real deployment this would live in a
# database or HR system; the MCP server is the clean interface to it.
COMPANY_POLICY = {
    "meals": {
        "max_amount": 75.00,
        "receipt_required_above": 25.00,
    },
    "travel": {
        "max_amount": 2000.00,
        "receipt_required_above": 50.00,
    },
    "software": {
        "max_amount": 500.00,
        "receipt_required_above": 0.00,
    },
    "office_supplies": {
        "max_amount": 200.00,
        "receipt_required_above": 50.00,
    },
}


def get_policy_for_category(category: str):
    """The single 'tool' this MCP server exposes."""
    return COMPANY_POLICY.get(category)


class MCPRequestHandler(BaseHTTPRequestHandler):
    """
    Minimal MCP-style JSON endpoint.
    POST a body like: {"tool": "get_policy", "category": "meals"}
    """

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            request = json.loads(body)
        except json.JSONDecodeError:
            self._respond(400, {"error": "invalid JSON"})
            return

        tool = request.get("tool")

        if tool == "list_tools":
            self._respond(200, {
                "tools": [
                    {
                        "name": "get_policy",
                        "description": "Look up the expense policy (max amount, "
                                       "receipt rules) for a given category.",
                        "parameters": {"category": "string"},
                    }
                ]
            })
        elif tool == "get_policy":
            category = request.get("category", "")
            policy = get_policy_for_category(category)
            if policy is None:
                self._respond(404, {"error": f"no policy for '{category}'"})
            else:
                self._respond(200, {"category": category, "policy": policy})
        else:
            self._respond(400, {"error": f"unknown tool '{tool}'"})

    def _respond(self, code, payload):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode())

    def log_message(self, *args):
        # Quiet the default request logging for a cleaner demo
        pass


def serve(port=8421):
    server = HTTPServer(("localhost", port), MCPRequestHandler)
    print(f"MCP Policy Server running on http://localhost:{port}")
    print("Exposing tool: get_policy(category)")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down MCP Policy Server.")
        server.shutdown()


if __name__ == "__main__":
    serve()
