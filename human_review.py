"""
Human-in-the-Loop Review
------------------------
The security / safety layer. Expenses the agent flags are NEVER
auto-actioned. They are routed to a human reviewer who must explicitly
approve or reject them. This is the "human-in-the-loop" pattern from the
course's security unit: the agent assists, but a person stays in control
of consequential decisions.

This module simulates the reviewer step. In a real system the flagged
queue would surface in a dashboard or Slack approval message.
"""

from agent import ExpenseStatus, TriageResult


def review_flagged(results: list, auto_decision: str = None) -> list:
    """
    Walk through every flagged expense and get a human decision.

    auto_decision: if provided ("approve"/"reject"), used for all flagged
    items instead of prompting. This lets the demo run non-interactively.
    Leave as None for a real interactive review.
    """
    decisions = []

    flagged = [r for r in results if r.status == ExpenseStatus.FLAGGED_FOR_REVIEW]

    if not flagged:
        print("No flagged expenses. Nothing for a human to review.")
        return decisions

    print(f"\n{len(flagged)} expense(s) need human review:\n")

    for r in flagged:
        print(f"  [{r.expense.expense_id}] {r.expense.employee} - "
              f"${r.expense.amount:.2f} ({r.expense.category})")
        print(f"      \"{r.expense.description}\"")
        for reason in r.reasons:
            print(f"      ! {reason}")

        if auto_decision in ("approve", "reject"):
            choice = auto_decision
            print(f"      > human decision (simulated): {choice.upper()}")
        else:
            choice = input("      Approve or reject? [a/r]: ").strip().lower()
            choice = "approve" if choice.startswith("a") else "reject"

        final = (ExpenseStatus.AUTO_APPROVED if choice == "approve"
                 else ExpenseStatus.REJECTED)
        decisions.append((r.expense.expense_id, final))
        print()

    return decisions


def run_full_pipeline(auto_decision="reject"):
    """End-to-end: triage every expense, then human-review the flagged ones."""
    from agent import ExpenseTriageAgent, Expense
    from mcp_client import PolicyMCPClient

    client = PolicyMCPClient()
    agent = ExpenseTriageAgent(client)

    expenses = [
        Expense("E-1001", "J. Rivera", "meals", 42.50,
                "Team lunch with client", receipt_attached=True),
        Expense("E-1004", "A. Patel", "meals", 310.00,
                "Dinner - cash advance for team event", receipt_attached=False),
        Expense("E-1006", "L. Nguyen", "travel", 2400.00,
                "Hotel for offsite", receipt_attached=True),
    ]

    print("=" * 60)
    print("FULL PIPELINE: Agent triage -> Human review")
    print("=" * 60)

    results = [agent.triage(e) for e in expenses]

    for r in results:
        print(f"[{r.expense.expense_id}] -> {r.status.value.upper()}")

    decisions = review_flagged(results, auto_decision=auto_decision)

    if decisions:
        print("Final human decisions on flagged items:")
        for expense_id, status in decisions:
            print(f"  {expense_id}: {status.value.upper()}")


if __name__ == "__main__":
    # Default to a non-interactive run so it works anywhere.
    # Set auto_decision=None to review interactively.
    run_full_pipeline(auto_decision="reject")
