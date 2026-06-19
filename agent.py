"""
Expense Triage Agent
---------------------
A business agent that reviews submitted expense reports against company
policy, auto-approves clean expenses, and flags risky/non-compliant ones
for human review (human-in-the-loop).

Built for the AI Agents: Intensive Vibe Coding Capstone Project.

Concepts demonstrated:
  1. Agent system (this file) - reasoning + tool use loop
  2. MCP Server integration (mcp_policy_server.py) - policy lookups
  3. Security / human-in-the-loop - flagged expenses require approval
"""

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ExpenseStatus(Enum):
    AUTO_APPROVED = "auto_approved"
    FLAGGED_FOR_REVIEW = "flagged_for_review"
    REJECTED = "rejected"


@dataclass
class Expense:
    expense_id: str
    employee: str
    category: str          # e.g. "meals", "travel", "software", "office_supplies"
    amount: float
    description: str
    receipt_attached: bool = True


@dataclass
class TriageResult:
    expense: Expense
    status: ExpenseStatus
    reasons: list = field(default_factory=list)


class ExpenseTriageAgent:
    """
    The core agent. It pulls policy rules from the MCP policy server
    (see mcp_policy_server.py), reasons over each expense, and decides
    whether to auto-approve, flag, or reject it.
    """

    def __init__(self, policy_client):
        # policy_client is our MCP server client (see mcp_client.py)
        self.policy_client = policy_client

    def triage(self, expense: Expense) -> TriageResult:
        reasons = []

        # 1. Pull the policy limit for this category from the MCP server
        policy = self.policy_client.get_policy(expense.category)

        if policy is None:
            reasons.append(f"No policy found for category '{expense.category}'")
            return TriageResult(expense, ExpenseStatus.FLAGGED_FOR_REVIEW, reasons)

        # 2. Security check: missing receipt above a threshold is a red flag
        if not expense.receipt_attached and expense.amount > policy["receipt_required_above"]:
            reasons.append(
                f"Missing receipt for ${expense.amount:.2f} "
                f"(receipt required above ${policy['receipt_required_above']:.2f})"
            )

        # 3. Policy limit check
        if expense.amount > policy["max_amount"]:
            reasons.append(
                f"Amount ${expense.amount:.2f} exceeds category limit "
                f"of ${policy['max_amount']:.2f}"
            )

        # 4. Suspicious pattern check (very simple heuristic for demo purposes)
        if self._looks_suspicious(expense):
            reasons.append("Description matches a known suspicious pattern")

        # 5. Decide outcome
        if reasons:
            return TriageResult(expense, ExpenseStatus.FLAGGED_FOR_REVIEW, reasons)

        reasons.append(f"Within policy (limit ${policy['max_amount']:.2f}), receipt OK")
        return TriageResult(expense, ExpenseStatus.AUTO_APPROVED, reasons)

    @staticmethod
    def _looks_suspicious(expense: Expense) -> bool:
        red_flags = ["cash advance", "personal", "gift card", "round trip to"]
        text = expense.description.lower()
        return any(flag in text for flag in red_flags)


def run_demo():
    """Run the agent over a small batch of sample expenses."""
    from mcp_client import PolicyMCPClient

    print("=" * 60)
    print("EXPENSE TRIAGE AGENT - Demo Run")
    print("=" * 60)

    client = PolicyMCPClient()
    agent = ExpenseTriageAgent(client)

    sample_expenses = [
        Expense("E-1001", "J. Rivera", "meals", 42.50,
                "Team lunch with client", receipt_attached=True),
        Expense("E-1002", "K. Chen", "travel", 1850.00,
                "Flight to conference", receipt_attached=True),
        Expense("E-1003", "M. Torres", "office_supplies", 15.00,
                "Notebook and pens", receipt_attached=False),
        Expense("E-1004", "A. Patel", "meals", 310.00,
                "Dinner - cash advance for team event", receipt_attached=False),
        Expense("E-1005", "S. Brooks", "software", 89.00,
                "Annual subscription renewal", receipt_attached=True),
    ]

    results = [agent.triage(e) for e in sample_expenses]

    for r in results:
        print(f"\n[{r.expense.expense_id}] {r.expense.employee} - "
              f"{r.expense.category} - ${r.expense.amount:.2f}")
        print(f"  Status: {r.status.value.upper()}")
        for reason in r.reasons:
            print(f"  - {reason}")

    approved = sum(1 for r in results if r.status == ExpenseStatus.AUTO_APPROVED)
    flagged = sum(1 for r in results if r.status == ExpenseStatus.FLAGGED_FOR_REVIEW)

    print("\n" + "=" * 60)
    print(f"Summary: {approved} auto-approved, {flagged} flagged for human review")
    print("=" * 60)


if __name__ == "__main__":
    run_demo()
