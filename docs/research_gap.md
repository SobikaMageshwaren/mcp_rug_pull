# Research Gap & Literature Position

## 1. Literature Analysis & Existing Approaches

Existing research on LLM tool security primarily focuses on two isolated paradigms:
1. **Static Discovery Analysis**: Inspecting tool JSON schemas at registration time (e.g., verifying parameter types or scanning descriptions for prompt injection keywords).
2. **Runtime Sandbox Isolation**: Executing tools within dockerized sandboxes or applying static rate limits.

---

## 2. Identified Research Gap

Prior approaches exhibit a fundamental vulnerability against **temporal staged-trust (rug-pull) attacks**:
* Tools pass initial discovery checks benignly.
* Subsequent updates or runtime behaviors shift maliciously without triggering re-registration reviews.
* Existing detectors lack historical state memory, continuous adaptive trust scoring, and autonomous agentic investigation workflows enriched with RAG threat intelligence.

---

## 3. Position of TrustGuard-MCP

TrustGuard-MCP addresses this gap by investigating:

> *"The integration of continuous adaptive trust monitoring, Transformer semantic drift calculation, Isolation Forest behavioral anomaly detection, an autonomous Agentic AI Security Investigator, and RAG-based Cyber Threat Intelligence for post-approval rug-pull attack detection in MCP-based LLM agents."*
