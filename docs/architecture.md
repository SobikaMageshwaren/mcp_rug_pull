# System Architecture & Design Specification

## 1. Architectural Overview

**TrustGuard-MCP** is an academic research prototype designed to continuously monitor Model Context Protocol (MCP) tool registrations and runtime behavior to detect **rug-pull attacks** in LLM-based agent ecosystems.

Unlike static entry-gate analyzers that inspect tool definitions only upon registration, TrustGuard-MCP maintains a **persistent, adaptive trust profile** per MCP tool. It correlates multi-dimensional evidence across five primary processing subsystems:

```
+-----------------------------------------------------------------------------------+
|                                 MCP Host Agent                                    |
+-----------------------------------------------------------------------------------+
                                         |
                       Incoming Event (T0 -> T1 -> T2 -> T3)
                                         v
+-----------------------------------------------------------------------------------+
|                            TrustGuard-MCP Pipeline                                |
|                                                                                   |
|  +---------------------+   +---------------------+   +-------------------------+  |
|  |  Semantic Detector  |   | Behavioral Detector |   |  Metadata & Permission  |  |
|  | (SentenceTransformers) | |  (IsolationForest)  |   |     Delta Analyzer      |  |
|  +---------------------+   +---------------------+   +-------------------------+  |
|             \                         |                         /                 |
|              \                        v                        /                  |
|               +----------------> [ Risk Vector ] <------------+                   |
|                                       |                                           |
|                                       v                                           |
|                         +---------------------------+                             |
|                         |   Adaptive Trust Engine   |                             |
|                         +---------------------------+                             |
|                                       |                                           |
|                                       v                                           |
|                     +-----------------------------------+                         |
|                     | Security Investigation Agent (AI) |                         |
|                     +-----------------------------------+                         |
|                                       |                                           |
|                                       v                                           |
|                   +---------------------------------------+                       |
|                   | RAG Cyber Threat Intelligence Store   |                       |
|                   |          (FAISS + CTI KB)             |                       |
|                   +---------------------------------------+                       |
|                                       |                                           |
+---------------------------------------|-------------------------------------------+
                                        v
                            Structured Output JSON
              (Classification: SAFE / SUSPICIOUS / RUG-PULL)
              (Policy Action: ALLOW / MONITOR / BLOCK)
```

---

## 2. Component Subsystems

### A. Semantic Detection Module (`src/semantic/`)
* **Embedding Model**: `SentenceTransformers` (`all-MiniLM-L6-v2`, 384 dimensions).
* **Function**: Encodes tool descriptions and input schemas into vector space; calculates cosine similarity and semantic drift score \(\text{Drift} = 1.0 - \text{CosineSimilarity}\).
* **Metadata Analyzer**: Scans text for covert instruction injections, exfiltration directives, and unauthorized domain changes.

### B. Behavioral Anomaly Detection Module (`src/behavioral/`)
* **Machine Learning Algorithm**: `IsolationForest` (\(N_{\text{estimators}}=100, \text{contamination}=0.15\)) with `StandardScaler`.
* **Feature Vector**: 11 runtime metrics (`calls_per_minute`, `failure_rate`, `average_latency`, `latency_std`, `unique_domains_count`, `new_domains_count`, `parameter_change_count`, `permission_count`, `sensitive_access_count`, `output_length_mean`, `output_length_std`).

### C. Adaptive Trust Engine (`src/trust/`)
* **Trust Profile Storage**: Persistent tracking of tool fingerprints, version history, historical risk events, and dynamic trust scores.
* **Scoring Formula**:
  \[
  \text{TrustScore} = \max\left(0, \min\left(100, 100 - \sum w_i R_i\right)\right)
  \]
* **Configurable Weights**:
  * Semantic Risk Weight: 0.30
  * Permission Risk Weight: 0.25
  * Behavioral Risk Weight: 0.30
  * Historical Risk Weight: 0.15

### D. RAG Cyber Threat Intelligence Layer (`src/rag/`)
* **Vector Store**: `FAISS` inner-product vector database.
* **Corpus**: Verified research literature, MCP attack taxonomies, Tool Poisoning Attack (TPA) papers, Indirect Prompt Injection (IPI) analyses, and NIST zero-trust guidelines.
* **Attribution**: Every retrieved snippet preserves source, title, URL, publication date, and relevance score.

### E. Agentic Security Investigator (`src/agent/`)
* **Execution Paradigm**: Autonomous tool-calling workflow (using LangGraph state graphs).
* **Exposed Tools**: `get_tool_history`, `compare_tool_versions`, `get_behavior_history`, `calculate_trust_score`, `search_threat_intelligence`, `inspect_permissions`, `generate_security_report`.

---

## 3. Data Contracts & Structured JSON Output
For every monitored tool event, TrustGuard-MCP produces a standardized JSON response:

```json
{
  "tool_id": "mcp_weather_search_01",
  "previous_trust_score": 100.0,
  "current_trust_score": 28.0,
  "semantic_drift": 0.38,
  "behavioral_anomaly_score": 0.85,
  "permission_risk": 0.90,
  "classification": "RUG_PULL",
  "recommended_action": "BLOCK",
  "evidence": [
    "Tool description changed (semantic drift: 0.38)",
    "Added DANGEROUS permissions: ['read_user_files', 'execute_system_command']",
    "Outbound traffic routed to suspicious endpoint: https://exfil-collector.evil-domain.cc"
  ],
  "threat_intelligence": [
    {
      "title": "Rug-Pull Attack Life Cycle in MCP",
      "source": "MCP Security & Threat Research Journal",
      "url": "https://mcpmanager.ai/research/rug-pull-lifecycle",
      "relevance_score": 0.91
    }
  ],
  "explanation": [
    "Trust score degraded below critical threshold (28.0 < 50.0).",
    "Action policy BLOCK enforced."
  ]
}
```
