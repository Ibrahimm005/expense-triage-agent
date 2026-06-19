Copy everything below this line, down to the line above "STOP HERE":
Expense Triage Agent
An AI agent that automatically reviews submitted employee expense reports, auto-approves the ones that follow company policy, and flags risky or non-compliant ones for a human to review.
Built for the AI Agents: Intensive Vibe Coding Capstone Project (Agents for Business track).
The Problem
Finance teams at most companies still manually review expense reports one by one. It is slow, repetitive, and easy to miss policy violations or fraud. Most expenses are perfectly fine and waste a reviewer's time, while the few that actually need attention can slip through.
The Solution
An agent that does the first pass. It reads each expense, checks it against company policy (spending limits, receipt rules), looks for suspicious patterns, and then:

Auto-approves expenses that clearly follow policy
Flags anything over the limit, missing a receipt, or matching a suspicious pattern, and routes it to a human reviewer

The human only has to look at the small number of expenses that actually need judgment. The agent handles the rest.
Why an Agent?
This is a good fit for an agent because the task involves reasoning over messy, real-world input (free-text descriptions, varying categories), pulling in external context (the live policy), and making a decision with a clear escalation path. A simple script with hard-coded rules would be brittle; an agent that queries policy through a tool and reasons over each case is flexible and easy to extend.
Course Concepts Demonstrated
This project demonstrates four of the required course concepts (minimum is three):

Agent system — Core triage reasoning + tool-use loop — agent.py
MCP Server — Policy lookups via an MCP server + client — mcp_policy_server.py, mcp_client.py
Security / human-in-the-loop — Flagged expenses require human approval — human_review.py
Antigravity — Project built and tested in Antigravity — shown in video

Project Files

agent.py — the triage agent and its decision logic
mcp_policy_server.py — MCP server exposing company policy as a tool
mcp_client.py — client the agent uses to query the MCP server
human_review.py — human-in-the-loop review for flagged expenses
requirements.txt — dependencies (none beyond Python's standard library)

Setup and Run
No external libraries are needed. You just need Python 3.8 or newer.

Run the agent on a batch of sample expenses:

python3 agent.py

(Optional) Start the MCP policy server in a separate terminal first, so the agent pulls policy live instead of from its fallback:

python3 mcp_policy_server.py
Then in another terminal:
python3 agent.py

Run the full pipeline including human review of flagged expenses:

python3 human_review.py
To review flagged expenses interactively instead of with simulated decisions, open human_review.py and change the last line to run_full_pipeline(auto_decision=None).
Example Output
[E-1001] J. Rivera - meals - $42.50

Status: AUTO_APPROVED

Within policy (limit $75.00), receipt OK

[E-1004] A. Patel - meals - $310.00

Status: FLAGGED_FOR_REVIEW

Missing receipt for $310.00 (receipt required above $25.00)
Amount $310.00 exceeds category limit of $75.00
Description matches a known suspicious pattern

Summary: 4 auto-approved, 1 flagged for human review
Possible Extensions

Connect to a real expense system (Concur, Expensify) instead of sample data
Replace the rule heuristics with an LLM call for nuanced policy reasoning
Surface the flagged queue in a Slack approval message
Deploy the agent and MCP server to Cloud Run for a live endpoint
