# System Limitations & Future Work

## 1. Known Limitations

1. **Synthetic Attack Dataset Size**: While baseline tool schemas are authentic, temporal rug-pull attack sequences are synthetically generated under controlled parameters due to the current rarity of public MCP malware repositories.
2. **Computational Overhead of Transformers**: Embedding generation using Transformer models adds ~45ms per metadata update compared to static string matching (~2.5ms).
3. **Cold-Start Behavioral Baseline**: The Isolation Forest anomaly detector requires an initial sequence of clean operational calls to establish a reliable baseline.
4. **Offline RAG Knowledge Scope**: The local FAISS vector store is restricted to indexed threat documents; unknown zero-day attack patterns outside the CTI corpus rely primarily on ML drift heuristics.

---

## 2. Future Research Directions

* **Graph Neural Network (GNN) Tool Relationships**: Modeling multi-tool dependency graphs and inter-server call chains.
* **Cryptographic Schema Pinning**: Integrating PKI and digital signatures for MCP tool publishing verification.
* **Federated Trust Sharing**: Sharing anonymized tool trust degradation scores across enterprise MCP host networks.
