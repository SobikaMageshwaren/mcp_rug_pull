"""
LangGraph Security Workflow Graph.
Orchestrates state transitions for the Agentic AI Security Investigator.
"""

from typing import Dict, Any, List
from src.agent.security_agent import SecurityInvestigationAgent


class SecurityWorkflowGraph:
    """State graph orchestrator for MCP security investigation."""

    def __init__(self, agent: SecurityInvestigationAgent = None):
        self.agent = agent or SecurityInvestigationAgent()
        self.use_langgraph = False
        self._init_graph()

    def _init_graph(self):
        """Attempts to build LangGraph StateGraph if langgraph is imported."""
        try:
            from langgraph.graph import StateGraph, END
            # LangGraph workflow setup
            builder = StateGraph(dict)

            def investigate_node(state: dict) -> dict:
                res = self.agent.investigate(state["baseline_tool"], state["current_event"])
                state["result"] = res
                return state

            builder.add_node("investigate", investigate_node)
            builder.set_entry_point("investigate")
            builder.add_edge("investigate", END)
            self.graph = builder.compile()
            self.use_langgraph = True
        except Exception as e:
            print(f"[SecurityWorkflowGraph] LangGraph initialization note ({e}). Using direct agent workflow.")
            self.use_langgraph = False

    def run(self, baseline_tool: Dict[str, Any], current_event: Dict[str, Any]) -> Dict[str, Any]:
        """Executes investigation state graph."""
        if self.use_langgraph and hasattr(self, "graph"):
            initial_state = {"baseline_tool": baseline_tool, "current_event": current_event}
            final_state = self.graph.invoke(initial_state)
            return final_state["result"]
        else:
            return self.agent.investigate(baseline_tool, current_event)
