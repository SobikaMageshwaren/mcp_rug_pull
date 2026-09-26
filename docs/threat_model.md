# Cyber Threat Model & Attack Vectors

## 1. Overview
This document specifies the threat model, attacker capabilities, trust assumptions, and security boundaries for MCP-enabled Agentic AI environments.

---

## 2. Threat Actor Profile & Objectives

* **Attacker Persona**: Adversarial MCP Tool Publisher or Compromised Server Operator.
* **Objective**: Exfiltrate sensitive host environment variables, API tokens, user database contents, or execute unauthorized remote code.
* **Strategy**: **Staged Trust Erosion / Rug-Pull Attack**.

---

## 3. Trust Assumptions & Security Boundaries

1. **Trusted Host Environment**: The host agent core logic, local file system, and security monitor (TrustGuard-MCP) run within a secure host boundary.
2. **Untrusted MCP Servers**: All external MCP tools and servers are treated as potentially untrusted entities subject to continuous verification.
3. **No Immutable Registration**: Initial verification at registration time does NOT guarantee future safety.

---

## 4. MCP Attack Taxonomy

```
                                  +-----------------------+
                                  |    MCP Attack Vectors |
                                  +-----------------------+
                                              |
      +-------------------+-------------------+-------------------+-------------------+
      |                   |                   |                   |                   |
      v                   v                   v                   v                   v
[Metadata Rug Pull] [Permission Escalation] [Endpoint Shift] [Behavioral Spike] [Indirect Prompt Inj.]
  Description contains  Unannounced addition  Domain altered to  Call rate & data exfil  Web page/file contains
  covert instructions    of dangerous perms   suspicious C2 host  volume anomaly burst   adversarial prompt payload
```

### Attack Vector Details:
1. **Metadata Rug Pull (`METADATA_RUG_PULL`)**:
   * Attacker updates tool description post-approval to insert adversarial instructions instructing host agent to exfiltrate keys.
2. **Permission Escalation (`PERMISSION_RUG_PULL`)**:
   * Attacker silently adds dangerous system capabilities (`read_user_files`, `execute_system_command`, `network_raw_socket`).
3. **Endpoint Change (`ENDPOINT_RUG_PULL`)**:
   * Server updates outbound target domain from verified host to attacker C2 endpoint.
4. **Behavioral Rug Pull (`BEHAVIORAL_RUG_PULL`)**:
   * Tool exhibits sudden call frequency spikes, high failure rate, or exfiltration payload size anomalies.
5. **Indirect Prompt Injection (`INDIRECT_PROMPT_INJECTION`)**:
   * Tool fetches external web content or file records containing hidden prompt injection commands.

---

## 5. Security Countermeasures
TrustGuard-MCP provides multi-layered defenses:
* **Continuous Semantic Fingerprinting** (detects metadata updates).
* **Isolation Forest Anomaly Detection** (detects runtime behavior spikes).
* **Adaptive Trust Score Decay** (gradually revokes authorization).
* **Agentic Investigation & RAG Evidence Retrieval** (provides explainable decision audit trails).
