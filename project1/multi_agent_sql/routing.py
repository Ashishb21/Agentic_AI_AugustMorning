"""
Conditional routing functions for the multi-agent system.
Determines the flow of the graph based on state conditions.
"""

from typing import Literal

try:
    from state_schema import CustomerServiceState
except ImportError:
    from .state_schema import CustomerServiceState


def route_to_specialist(state: CustomerServiceState) -> Literal[
    "query_agent",
    "sales_agent",
    "refund_agent",
    "analytics_agent",
    "clarification_agent"
]:
    """
    Routes to the appropriate specialist agent based on query classification.

    Args:
        state: Current state with query_type

    Returns:
        Name of the specialist agent to route to
    """
    routing_map = {
        "order_status": "query_agent",
        "product_info": "sales_agent",
        "refund": "refund_agent",
        "analytics": "analytics_agent",
        "unclear": "clarification_agent"
    }

    query_type = state.get("query_type", "unclear")
    agent = routing_map.get(query_type, "clarification_agent")
    print(f"  [Routing] Query type: {query_type} → {agent}")
    return agent


def check_if_complete(state: CustomerServiceState) -> Literal[
    "supervisor_agent",
    "classification_agent",
    "human_handoff"
]:
    """
    Checks if the query has been fully resolved.

    Determines the next step:
    - If escalation needed: route to human
    - If clarification needed: back to classification
    - If complete: to supervisor for final response
    - Otherwise: back to classification for retry

    Args:
        state: Current state with completion flags

    Returns:
        Next node to execute
    """

    # Check escalation flag
    if state.get("escalate_to_human", False):
        print("  [Completion Check] Escalating to human agent...")
        return "human_handoff"

    # Check if needs clarification
    if state.get("needs_clarification", False):
        print("  [Completion Check] Clarification needed, routing back to classification...")
        return "classification_agent"

    # Check if task is complete
    if state.get("is_complete", False):
        print("  [Completion Check] Task complete, routing to supervisor...")
        return "supervisor_agent"

    # Default: unable to process, ask for clarification
    print("  [Completion Check] Unable to process, requesting clarification...")
    return "classification_agent"
