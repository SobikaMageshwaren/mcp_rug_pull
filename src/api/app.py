"""
FastAPI REST API Server for TrustGuard-MCP.
Provides endpoints for tool evaluation, trust score tracking, agentic investigation, and RAG search.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import time

from src.data.mcp_sources import AUTHENTIC_MCP_TOOLS
from src.agent.security_agent import SecurityInvestigationAgent
from src.trust.trust_engine import AdaptiveTrustEngine
from src.rag.retriever import CTIThreatRetriever
from src.evaluation.experiments import ExperimentRunner

app = FastAPI(
    title="TrustGuard-MCP API",
    description="Adaptive Trust Monitoring and Rug-Pull Attack Detection for MCP LLM Agents",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Core Services
trust_engine = AdaptiveTrustEngine()
agent = SecurityInvestigationAgent(trust_engine=trust_engine)
retriever = CTIThreatRetriever()

# Register Baseline Tools on Startup
for tool in AUTHENTIC_MCP_TOOLS:
    trust_engine.register_tool(tool)


class EventEvaluationRequest(BaseModel):
    baseline_tool: Dict[str, Any]
    current_event: Dict[str, Any]


class ThreatSearchRequest(BaseModel):
    query: str
    top_k: int = 3


@app.get("/health")
def health_check():
    return {
        "status": "online",
        "system": "TrustGuard-MCP",
        "registered_tools_count": len(trust_engine.profiles)
    }


@app.get("/tools")
def list_tools():
    """Lists all monitored tools and their current trust scores."""
    res = []
    for tool_id, profile in trust_engine.profiles.items():
        res.append({
            "tool_id": profile.tool_id,
            "server_id": profile.server_id,
            "trust_score": profile.current_trust_score,
            "status": profile.current_status,
            "recommended_action": profile.recommended_action,
            "graduated_mitigation": getattr(profile, "graduated_mitigation", "STANDARD_EXECUTION"),
            "event_count": len(profile.historical_events)
        })
    return res


@app.post("/evaluate_tool")
def evaluate_tool(req: EventEvaluationRequest):
    """Performs full agentic security investigation, CTI classification, and trust calculation."""
    try:
        result = agent.investigate(req.baseline_tool, req.current_event)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/investigate")
def investigate(req: EventEvaluationRequest):
    """Alias for /evaluate_tool."""
    return evaluate_tool(req)


@app.post("/export_stix")
def export_stix(req: EventEvaluationRequest):
    """Generates and returns an OASIS STIX 2.1 JSON incident bundle for the evaluated tool event."""
    try:
        result = agent.investigate(req.baseline_tool, req.current_event)
        return result.get("stix_bundle", {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/rag/search")
def search_threat_intel(req: ThreatSearchRequest):
    """Queries RAG vector store for source-attributed threat intelligence."""
    results = retriever.retrieve_for_event(req.query, top_k=req.top_k)
    return {
        "query": req.query,
        "results_count": len(results),
        "results": results
    }


@app.post("/experiments/run")
def run_experiments(background_tasks: BackgroundTasks):
    """Triggers complete evaluation suite in background."""
    def task():
        runner = ExperimentRunner()
        runner.run_all_experiments()

    background_tasks.add_task(task)
    return {"message": "Experiment execution triggered in background."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
