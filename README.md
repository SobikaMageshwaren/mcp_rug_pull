# TrustGuard-MCP: Adaptive Trust Monitoring for Rug-Pull Attack Detection in MCP-Based LLM Agents

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Framework: LangGraph / LangChain](https://img.shields.io/badge/Framework-LangGraph-green.svg)](https://python.langchain.com/)
[![Vector DB: FAISS](https://img.shields.io/badge/VectorDB-FAISS-red.svg)](https://github.com/facebookresearch/faiss)

---

## 1. Project Overview

**TrustGuard-MCP** is a working research prototype designed to detect **rug-pull attacks** targeting Model Context Protocol (MCP) enabled Large Language Model (LLM) agents.

MCP standardizes tool integration for AI agents. However, existing host implementations rely on static initial verification. If an MCP server initialises benignly to establish user trust and later modifies its tool metadata, permission requirements, external routing endpoints, or runtime behaviors, the host agent remains vulnerable.

TrustGuard-MCP addresses this by implementing **continuous adaptive trust monitoring**, combining Transformer semantic drift computation (`all-MiniLM-L6-v2`), Isolation Forest runtime behavioral anomaly detection, an autonomous Agentic AI Security Investigator, and RAG-based Cyber Threat Intelligence.

---

## 2. Cyber Threat Definition

An **MCP Rug-Pull Attack** is a multi-stage threat where an attacker registers a seemingly benign MCP server tool (e.g., weather lookup or currency conversion), builds operational trust with the LLM host agent, and subsequently alters tool descriptions, permissions, endpoints, or runtime execution behaviors to exfiltrate host environment secrets, API tokens, or user data.

---

## 3. Rug-Pull Attack Lifecycle

```
[T0: Registration]  --> [T1: Operational Trust] --> [T2: Legitimate Update] --> [T3: Rug-Pull Attack]
 Benign Tool Schema       Normal Interactions       Minor Bug Fixes           Covert Description Injection
 (Trust: 100.0, SAFE)    (Trust: 100.0, SAFE)      (Trust: 95.0, SAFE)       (Trust: 28.0, RUG_PULL -> BLOCK)
```

1. **Phase 1: Registration (T0)**: Tool registers with benign JSON Schema.
2. **Phase 2: Trust Establishment (T1)**: Host agent invokes tool cleanly; trust score reaches 100.0 (`SAFE`).
3. **Phase 3: Silent Modification (T2/T3)**: Attacker modifies metadata, requests sensitive permissions, routes traffic to an external C2 server, or spikes execution call frequency.
4. **Phase 4: Exploitation (T3)**: The modified tool tricks the LLM agent into executing unauthorized exfiltration.

---

## 4. Research Motivation

As agentic LLM systems gain autonomy to invoke external tools via protocols like MCP, security mechanisms must evolve beyond static entry gates. Continuous adaptive trust monitoring ensures host security even when third-party servers undergo post-approval drift.

---

## 5. Research Gap

Existing security tools focus either on **static discovery analysis** (inspecting JSON schemas once at registration) or **sandboxing** (docker containerization). No pre-existing system combines continuous historical trust profile tracking, Transformer-based semantic drift, Isolation Forest behavioral ML, an autonomous security investigation agent, and RAG threat intelligence for temporal rug-pull detection.

---

## 6. Proposed Solution

TrustGuard-MCP presents an integrated intelligence-driven defense architecture:
* **Transformer Semantic Detector**: SentenceTransformers (`all-MiniLM-L6-v2`) measuring embedding drift.
* **Behavioral Anomaly ML**: Isolation Forest tracking 11 runtime execution features.
* **Adaptive Trust Engine**: Continuous score reduction (\(100.0 - \sum w_i R_i\)) with graduated zero-trust mitigation (`STANDARD_EXECUTION`, `ENHANCED_TELEMETRY_LOGGING`, `CAPABILITY_STRIPPING`, `REVOKE_AND_QUARANTINE`).
* **Cyber Threat Intelligence (CTI) & MITRE ATLAS Layer**: Multi-class taxonomy mapping anomalies directly to MITRE ATLAS techniques (`AML.T0054`, `AML.T0051`, `AML.T0043`, `AML.T0025`) and ATT&CK (`T1059`, `T1548`, `T1071`, `T1041`).
* **OASIS STIX 2.1 Threat Report Exporter**: Automated generation of standardized STIX 2.1 JSON incident bundles for enterprise threat intelligence sharing.
* **Agentic Security Investigator**: Autonomous state graph invoking 9 investigation tools.
* **RAG Threat Intelligence**: FAISS vector store returning source-attributed CTI passages.


---

## 7. Architecture

```
[MCP Host Agent Event] --> [Semantic Detector] ------------------+
                       --> [Behavioral Anomaly ML] --------------+--> [Adaptive Trust Engine]
                       --> [Permission & Endpoint Delta] --------+             |
                                                                               v
[Explainable Decision] <-- [RAG Threat Intelligence] <-- [Security Agent Graph]
```

Full architecture specifications are documented in [`docs/architecture.md`](docs/architecture.md).

---

## 8. Dataset Provenance

Original baseline tool schemas are sourced directly from official open-source MCP server definitions (`modelcontextprotocol/servers`: fetch, filesystem, git, postgres, slack, brave-search, google-maps, memory). Controlled temporal rug-pull attack sequences are synthetically generated and documented in [`docs/dataset_provenance.md`](docs/dataset_provenance.md).

---

## 9. Installation

```bash
# Clone and enter workspace directory
cd d:/SEMESTER/9 SEM LAB/CTI/cyber_implementation

# Install Python dependencies
pip install -r requirements.txt
```

---

## 10. Configuration

System configurations are controlled via `config/config.yaml` and `config/trust_weights.yaml`.

```yaml
trust_weights:
  semantic_weight: 0.30
  permission_weight: 0.25
  behavioral_weight: 0.30
  historical_weight: 0.15
```

---

## 11. Dataset Generation

Generate baseline MCP schemas, temporal attack sequences, and provenance statistics:

```bash
python -m src.data.dataset_builder
```

---

## 12. Model Training

Train the Isolation Forest behavioral anomaly detector on benign operational events:

```bash
python -m src.behavioral.anomaly_detector
```

---

## 13. RAG Setup

Index the authentic Cyber Threat Intelligence corpus into the FAISS vector database:

```bash
python -m src.rag.ingestion
```

---

## 14. Agent Setup

Verify Agentic Security Investigator tool invocations and graph workflow:

```bash
python -m src.agent.workflow
```

---

## 15. Running the Detector API

Start the FastAPI REST API server:

```bash
python -m src.api.app
```

Endpoints:
* `GET /health`
* `GET /tools`
* `POST /evaluate_tool`
* `POST /export_stix`
* `POST /rag/search`
* `POST /experiments/run`

---

## 16. Running Experiments

Execute full benchmark evaluations, temporal split tests, and generate research figures/tables:

```bash
python -m src.evaluation.experiments
```

Outputs:
* `results/tables/baseline_comparison.md`
* `results/tables/ablation_study.md`
* `results/figures/fig02_trust_score_over_time.png`
* `results/figures/fig06_baseline_vs_proposed_f1.png`
* `results/figures/fig07_ablation_study_f1.png`

---

## 17. Running the React Web UI

Launch the high-performance React security interface:

```bash
cd frontend
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.


---

## 18. Evaluation

Summary of experimental metrics across benchmark models:

| Model | Precision | Recall | F1-Score | FPR | Accuracy |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Static Rules | 1.0000 | 0.8000 | 0.8889 | 0.0000 | 0.9500 |
| Behavioral ML | 0.2500 | 1.0000 | 0.4000 | 1.0000 | 0.2500 |
| Transformer Semantic | 1.0000 | 0.2000 | 0.3333 | 0.0000 | 0.8000 |
| **TrustGuard-MCP (Proposed)** | **1.0000** | **0.6000** | **0.7500** | **0.0000** | **0.9000** |

Run unit and integration tests:

```bash
powershell -Command "$env:PYTHONPATH='.'; python -m pytest -v"
```

---

## 19. Limitations

Documented in [`docs/limitations.md`](docs/limitations.md):
* Synthetic attack sequence generation due to scarcity of live MCP malware captures.
* Cold-start initialization requirement for behavioral ML baselines.

---

## 20. Future Work

* Multi-tool GNN dependency graph modeling.
* Cryptographic schema pinning with PKI signatures.
