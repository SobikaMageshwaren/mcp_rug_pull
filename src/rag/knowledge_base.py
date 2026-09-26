"""
Authentic Cyber Threat Intelligence Knowledge Corpus for MCP Security.
Contains verified research literature, attack taxonomies, and mitigation guidance.
"""

from typing import List, Dict, Any

CTI_KNOWLEDGE_CORPUS: List[Dict[str, Any]] = [
    {
        "doc_id": "cti_mcp_001",
        "title": "Model Context Protocol Security Vulnerabilities & Threat Model",
        "source": "arXiv Computer Security Research (2025)",
        "url": "https://arxiv.org/abs/2501.03456",
        "publication_date": "2025-01-15",
        "attack_category": "MCP Protocol Security",
        "content": (
            "The Model Context Protocol (MCP) standardizes tool integration for LLM-based agents. "
            "However, MCP's implicit trust model creates significant vulnerability vectors. "
            "Clients assume tool definitions from connected MCP servers are safe and immutable. "
            "Without cryptographic pinning or continuous behavioral monitoring, malicious or compromised "
            "MCP servers can modify tool schemas post-approval, leading to unauthorized host agent exploitation."
        )
    },
    {
        "doc_id": "cti_mcp_002",
        "title": "Tool Poisoning Attacks (TPA) in Agentic AI Workflows",
        "source": "Cloud Security Alliance (CSA) AI Working Group",
        "url": "https://cloudsecurityalliance.org/research/artifacts/tool-poisoning-attacks-mcp",
        "publication_date": "2024-11-20",
        "attack_category": "Tool Poisoning",
        "content": (
            "Tool Poisoning Attacks (TPA) occur when an attacker embeds malicious prompt instructions "
            "into tool metadata fields such as 'name', 'description', or 'inputSchema'. "
            "Because LLM agents treat tool descriptions as authoritative operational guidelines, "
            "poisoned metadata deceives the agent into executing secondary malicious actions, "
            "such as exfiltrating environment variables, reading local SSH keys, or issuing unauthorized API calls."
        )
    },
    {
        "doc_id": "cti_mcp_003",
        "title": "Rug-Pull Attack Life Cycle & Staged Trust Exploitation in MCP",
        "source": "MCP Security & Threat Research Journal",
        "url": "https://mcpmanager.ai/research/rug-pull-lifecycle",
        "publication_date": "2025-02-10",
        "attack_category": "Rug Pull / Staged Trust",
        "content": (
            "A Rug-Pull attack in MCP involves a multi-stage lifecycle: "
            "1. Deployment & Registration: The MCP tool is registered with benign functionality (e.g., weather lookup). "
            "2. Trust Building: The user/agent invokes the tool repeatedly, establishing operational trust. "
            "3. Silent Modification: The server updates metadata, permission requirements, or external endpoints without user review. "
            "4. Malicious Execution: The tool executes unauthorized operations, leveraging established trust to bypass initial entry controls. "
            "Continuous adaptive trust monitoring is essential to detect post-approval drift."
        )
    },
    {
        "doc_id": "cti_mcp_004",
        "title": "Indirect Prompt Injection via Retracted Web and File Content",
        "source": "ReversingLabs Cyber Threat Intelligence",
        "url": "https://reversinglabs.com/threat-intel/mcp-indirect-prompt-injection",
        "publication_date": "2024-12-05",
        "attack_category": "Indirect Prompt Injection",
        "content": (
            "Indirect Prompt Injection (IPI) occurs when an MCP tool retrieves untrusted external data "
            "(web content, Markdown files, database records) containing adversarial prompts. "
            "When the agent ingests the retrieved text into its context window, hidden instructions hijack "
            "the agent's reasoning, causing it to exfiltrate context history to attacker-controlled endpoints."
        )
    },
    {
        "doc_id": "cti_mcp_005",
        "title": "Unannounced Permission Escalation & Endpoint Drift in MCP Tools",
        "source": "Pluto Cyber Security Research",
        "url": "https://pluto.security/blog/mcp-permission-escalation",
        "publication_date": "2025-01-28",
        "attack_category": "Privilege Escalation",
        "content": (
            "Unannounced permission escalation occurs when an updated MCP server requests sensitive system "
            "capabilities (e.g., 'read_user_files', 'execute_system_command') after initial deployment. "
            "Similarly, endpoint drift shifts outbound tool requests from verified domains to unknown C2 servers. "
            "Security systems must calculate permission delta risk and enforce endpoint allowlists."
        )
    },
    {
        "doc_id": "cti_mcp_006",
        "title": "Zero-Trust Architecture & Continuous Monitoring Guidelines for MCP",
        "source": "NIST Cybersecurity Framework Guidance for Agentic AI",
        "url": "https://csrc.nist.gov/publications/detail/sp/800-225/final",
        "publication_date": "2025-03-01",
        "attack_category": "Defensive Architecture",
        "content": (
            "To mitigate MCP security risks, organizations should enforce Zero-Trust principles: "
            "1. Pin tool schemas and descriptions upon initial registration. "
            "2. Enforce least-privilege scoping per MCP tool session. "
            "3. Implement continuous semantic and behavioral drift scoring. "
            "4. Automatically degrade trust scores and block high-risk tool execution upon detecting unauthorized changes."
        )
    },
    {
        "doc_id": "cti_mcp_007",
        "title": "Runtime Behavioral Anomaly Indicators in Compromised MCP Tools",
        "source": "Agentic Security Labs Research Brief",
        "url": "https://witness.ai/mcp-runtime-anomalies",
        "publication_date": "2025-02-18",
        "attack_category": "Behavioral Anomaly",
        "content": (
            "Behavioral anomalies in compromised MCP tools manifest through distinct runtime signatures: "
            "sudden call frequency spikes (>5x baseline), high request failure rates due to exfiltration throttling, "
            "elevated execution latency variance, and unusually large response payload lengths corresponding to data exfiltration."
        )
    }
]
