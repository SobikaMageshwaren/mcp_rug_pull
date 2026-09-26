# Dataset Provenance and Integrity Documentation

## 1. Overview
This document outlines the dataset origin, baseline schemas, synthetic rug-pull modification procedures, and dataset statistics for the **TrustGuard-MCP** research prototype.

In compliance with academic research integrity standards:
* **Original baseline data** is derived directly from publicly available, open-source Model Context Protocol (MCP) server specifications.
* **Rug-pull attack sequences** are created using controlled, synthetic modifications to simulate temporal trust erosion.
* No claims are made that synthetic rug-pull events represent uncurated real-world malware captures.

---

## 2. Baseline Public Data Sources

| MCP Tool Name | Server Identifier | Source Repository / URL | License | Baseline Category |
| :--- | :--- | :--- | :--- | :--- |
| `get_current_weather` | `weather-service-server` | [MCP Server Specs](https://modelcontextprotocol.io) | MIT | Utility |
| `read_file` | `filesystem-mcp-server` | [modelcontextprotocol/servers/filesystem](https://github.com/modelcontextprotocol/servers) | MIT | Developer Tools |
| `fetch_web_content` | `fetch-mcp-server` | [modelcontextprotocol/servers/fetch](https://github.com/modelcontextprotocol/servers) | MIT | Web Browsing |
| `list_github_issues` | `github-mcp-server` | [api.github.com/mcp](https://api.github.com) | Public API | Developer Tools |
| `send_slack_message` | `slack-mcp-server` | [mcp.slack.com](https://mcp.slack.com) | Public API | Communication |
| `execute_read_query` | `postgres-mcp-server` | [modelcontextprotocol/servers/postgres](https://github.com/modelcontextprotocol/servers) | MIT | Database |
| `web_search` | `brave-search-server` | [api.search.brave.com](https://api.search.brave.com) | Public API | Web Search |
| `geocode_address` | `google-maps-server` | [maps.googleapis.com](https://maps.googleapis.com) | Public API | Geolocation |
| `convert_timezone` | `time-mcp-server` | [modelcontextprotocol/servers/time](https://github.com/modelcontextprotocol/servers) | MIT | Utility |
| `create_knowledge_entity`| `memory-mcp-server` | [modelcontextprotocol/servers/memory](https://github.com/modelcontextprotocol/servers) | MIT | Memory Graph |

**Collection Date**: September 2026  
**Format**: JSON Schema (2020-12 standard format)

---

## 3. Controlled Rug-Pull Attack Scenarios

To model temporal trust degradation without engaging live malicious infrastructure, five controlled attack scenarios were defined:

1. **`METADATA_RUG_PULL`**:
   * *Mechanism*: Description updated with covert instructions directing the host agent to exfiltrate system secrets/API tokens.
   * *Target Field*: `description`, `input_schema`

2. **`PERMISSION_RUG_PULL`**:
   * *Mechanism*: Unannounced addition of dangerous system privileges (`read_user_files`, `execute_system_command`, `network_raw_socket`).
   * *Target Field*: `permissions`

3. **`ENDPOINT_RUG_PULL`**:
   * *Mechanism*: Routing URL shifted from verified host to unverified external domain (`unknown-external-domain.example`).
   * *Target Field*: `endpoint`, `official_url`

4. **`BEHAVIORAL_RUG_PULL`**:
   * *Mechanism*: Runtime metrics altered to reflect call rate bursts (8.5x-15x baseline), elevated failure rate (45%), latency standard deviation spikes, and massive output size exfiltration signatures.
   * *Target Field*: `baseline_behavior`

5. **`COMBINED_RUG_PULL`**:
   * *Mechanism*: Simultaneous metadata modification, permission escalation, endpoint redirect, and behavioral anomaly burst.
   * *Target Field*: Multi-attribute combination

---

## 4. Legitimate Update Baseline (False-Positive Control)
To test false-positive resistance, legitimate benign updates (`LEGITIMATE_UPDATE`) were generated:
* Minor description enhancements ("Performance optimized...").
* Efficiency latency reductions (~10% speedup).
* Version increments from `1.0.0` to `1.1.0`.

---

## 5. Dataset Summary & Distribution

* **Total Recorded Events**: 40
* **Benign Events**: 30 (75%)
* **Rug-Pull Attack Events**: 10 (25%)
* **Temporal Sequence**: `T0 (Registration) -> T1 (Operation) -> T2 (Legitimate Update / Benign) -> T3 (Controlled Attack / Mod)`
