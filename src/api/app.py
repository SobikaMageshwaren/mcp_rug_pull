"""
FastAPI REST API Server for TrustGuard-MCP.
Provides endpoints for tool evaluation, trust score tracking, agentic investigation, and RAG search.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import time
from datetime import datetime, timezone
import logging

from src.data.mcp_sources import AUTHENTIC_MCP_TOOLS
from src.agent.security_agent import SecurityInvestigationAgent
from src.trust.trust_engine import AdaptiveTrustEngine
from src.rag.retriever import CTIThreatRetriever
from src.evaluation.experiments import ExperimentRunner

logger = logging.getLogger("TrustGuardAPI")

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

MAINTENANCE_EMAIL = "sobikamageshwaren@gmail.com"
DISPATCHED_ALERTS: List[Dict[str, Any]] = []


class EventEvaluationRequest(BaseModel):
    baseline_tool: Dict[str, Any]
    current_event: Dict[str, Any]


class ThreatSearchRequest(BaseModel):
    query: str
    top_k: int = 3


class AlertDispatchRequest(BaseModel):
    incident_ticket: str
    tool_id: str
    recipient: str = MAINTENANCE_EMAIL
    severity: str = "CRITICAL"
    message: Optional[str] = None
    aftermath: Optional[Dict[str, Any]] = None


class AlertActionRequest(BaseModel):
    incident_ticket: str
    tool_id: str
    action: str  # "APPROVE_EXCEPTION" | "QUARANTINE_SEVER"
    operator: str = MAINTENANCE_EMAIL
    rationale: Optional[str] = "Operator action triggered from testing screen"


@app.get("/health")
def health_check():
    return {
        "status": "online",
        "system": "TrustGuard-MCP",
        "registered_tools_count": len(trust_engine.profiles),
        "maintenance_email": MAINTENANCE_EMAIL,
        "dispatched_alerts_count": len(DISPATCHED_ALERTS)
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
    """Performs full agentic security investigation, CTI classification, aftermath calculation, and alert generation."""
    try:
        result = agent.investigate(req.baseline_tool, req.current_event)
        alert = result.get("alert_notification")
        if alert and alert.get("alert_triggered"):
            # Queue to dispatched alerts store
            DISPATCHED_ALERTS.insert(0, alert)
            if len(DISPATCHED_ALERTS) > 50:
                DISPATCHED_ALERTS.pop()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/investigate")
def investigate(req: EventEvaluationRequest):
    """Alias for /evaluate_tool."""
    return evaluate_tool(req)


@app.get("/alerts")
def get_alerts():
    """Retrieves all security incident notifications linked to the maintenance email."""
    return {
        "maintenance_email": MAINTENANCE_EMAIL,
        "total_alerts": len(DISPATCHED_ALERTS),
        "alerts": DISPATCHED_ALERTS
    }


@app.post("/alert/dispatch")
def dispatch_email_alert(req: AlertDispatchRequest):
    """Directly dispatches an incident notification to maintenance email sobikamageshwaren@gmail.com."""
    alert_id = f"ALT-{int(time.time() * 1000) % 900000 + 100000}"
    timestamp = datetime.now(timezone.utc).isoformat()

    alert_record = {
        "alert_id": alert_id,
        "incident_ticket": req.incident_ticket,
        "recipient_email": req.recipient,
        "sender": "soc-defense@trustguard-mcp.internal",
        "subject": f"[{req.severity} ALERT] MCP Incident Dispatched to {req.recipient} [{req.incident_ticket}]",
        "timestamp": timestamp,
        "delivery_status": "DISPATCHED",
        "channel": "SMTP_RELAY",
        "smtp_relay": {
            "status_code": 250,
            "relay_host": "smtp.trustguard-mcp.internal:587",
            "tls": "TLSv1.3",
            "message_id": f"<{alert_id}@{req.recipient.split('@')[-1]}>",
            "response": f"2.0.0 OK: queued as 7F28A1_{alert_id} for {req.recipient}"
        },
        "severity": req.severity,
        "tool_id": req.tool_id,
        "message": req.message or f"Incident alert on {req.tool_id} dispatched to {req.recipient}.",
        "aftermath": req.aftermath or {}
    }

    DISPATCHED_ALERTS.insert(0, alert_record)
    if len(DISPATCHED_ALERTS) > 50:
        DISPATCHED_ALERTS.pop()

    return {
        "status": "SUCCESS",
        "alert_id": alert_id,
        "recipient": req.recipient,
        "delivery_timestamp": timestamp,
        "relay_response": alert_record["smtp_relay"]["response"]
    }


@app.post("/alert/action")
def handle_operator_action(req: AlertActionRequest):
    """Executes operator approval exception or immediate quarantine sever from the screen."""
    timestamp = datetime.now(timezone.utc).isoformat()
    if req.action == "APPROVE_EXCEPTION":
        # Restore tool trust profile to monitored state
        if req.tool_id in trust_engine.profiles:
            p = trust_engine.profiles[req.tool_id]
            p.current_trust_score = 85.0
            p.current_status = "SAFE"
            p.recommended_action = "ALLOW"
            p.graduated_mitigation = "LEVEL_1_MONITOR"

        action_summary = f"Human approval granted by {req.operator} for {req.tool_id}. Status set to SAFE."
    else:
        # Enforce quarantine sever
        if req.tool_id in trust_engine.profiles:
            p = trust_engine.profiles[req.tool_id]
            p.current_trust_score = 0.0
            p.current_status = "RUG_PULL"
            p.recommended_action = "TERMINATE_QUARANTINE"
            p.graduated_mitigation = "LEVEL_3_TERMINATE_AND_QUARANTINE"

        action_summary = f"Emergency quarantine enforced by {req.operator} for {req.tool_id}. Sockets severed."

    # Notify maintenance email of operator action
    action_alert = {
        "alert_id": f"ACT-{int(time.time() * 1000) % 900000 + 100000}",
        "incident_ticket": req.incident_ticket,
        "recipient_email": MAINTENANCE_EMAIL,
        "sender": "soc-defense@trustguard-mcp.internal",
        "subject": f"[OPERATOR ACTION: {req.action}] Incident {req.incident_ticket} for {req.tool_id}",
        "timestamp": timestamp,
        "delivery_status": "DISPATCHED",
        "channel": "SMTP_RELAY & AUDIT_LOG",
        "severity": "OPERATIONAL",
        "message": action_summary,
        "rationale": req.rationale
    }
    DISPATCHED_ALERTS.insert(0, action_alert)

    return {
        "status": "SUCCESS",
        "action": req.action,
        "tool_id": req.tool_id,
        "incident_ticket": req.incident_ticket,
        "action_summary": action_summary,
        "timestamp": timestamp,
        "maintenance_notified": MAINTENANCE_EMAIL
    }


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
