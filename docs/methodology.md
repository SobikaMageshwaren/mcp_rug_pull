# Mathematical Methodology & Scoring Models

## 1. Overview
This document details the mathematical formulations and risk algorithms governing **TrustGuard-MCP**.

---

## 2. Transformer Semantic Drift Computation

Given a baseline tool description text \(D_{\text{base}}\) and a newly observed version text \(D_{\text{curr}}\), we compute 384-dimensional dense vector embeddings using SentenceTransformers (`all-MiniLM-L6-v2`):

\[
\mathbf{v}_{\text{base}} = \text{Encoder}(D_{\text{base}}), \quad \mathbf{v}_{\text{curr}} = \text{Encoder}(D_{\text{curr}})
\]

Cosine similarity between baseline and current tool embeddings is defined as:

\[
\text{Sim}(D_{\text{base}}, D_{\text{curr}}) = \frac{\mathbf{v}_{\text{base}} \cdot \mathbf{v}_{\text{curr}}}{\|\mathbf{v}_{\text{base}}\| \|\mathbf{v}_{\text{curr}}\|}
\]

The **semantic drift** \(S_{\text{drift}} \in [0, 1]\) is computed as:

\[
S_{\text{drift}} = 1.0 - \max\left(0, \text{Sim}(D_{\text{base}}, D_{\text{curr}})\right)
\]

Input JSON schemas are similarly serialized and evaluated to yield schema drift \(S_{\text{schema}}\). The overall **semantic risk score** \(R_{\text{sem}} \in [0, 100]\) combines drift magnitude with keyword threat indicators:

\[
R_{\text{sem}} = \min\left(100, 100 \times \left(0.70 S_{\text{drift}} + 0.30 S_{\text{schema}} + 0.35 N_{\text{keywords}}\right)\right)
\]

---

## 3. Isolation Forest Behavioral Anomaly Scoring

Each tool execution event is mapped to an 11-dimensional feature vector \(\mathbf{x} \in \mathbb{R}^{11}\):

\[
\mathbf{x} = \begin{bmatrix}
f_{\text{calls\_per\_min}} & f_{\text{failure\_rate}} & f_{\text{avg\_latency}} & f_{\text{latency\_std}} & f_{\text{unique\_domains}} & f_{\text{new\_domains}} & f_{\text{param\_count}} & f_{\text{perm\_count}} & f_{\text{sensitive\_count}} & f_{\text{out\_mean}} & f_{\text{out\_std}}
\end{bmatrix}^T
\]

Vectors are normalized via `StandardScaler`:

\[
\mathbf{z} = \frac{\mathbf{x} - \boldsymbol{\mu}}{\boldsymbol{\sigma}}
\]

An ensemble of 100 isolation trees calculates path length \(h(\mathbf{z})\). The raw anomaly decision function output \(s(\mathbf{z})\) is calibrated via a sigmoid transformation into a continuous behavioral risk score \(R_{\text{beh}} \in [0, 100]\):

\[
R_{\text{beh}} = \frac{100}{1 + e^{4.0 \cdot s(\mathbf{z})}}
\]

---

## 4. Adaptive Trust Score Formula

The current trust score \(T_t \in [0, 100]\) for tool \(i\) at timestamp \(t\) is dynamically computed by penalizing the initial baseline score (\(T_0 = 100.0\)) with the weighted sum of composite risk vectors:

\[
T_t = \max\left(0, \min\left(100, 100.0 - \left(w_{\text{sem}} R_{\text{sem}} + w_{\text{perm}} R_{\text{perm}} + w_{\text{beh}} R_{\text{beh}} + w_{\text{hist}} R_{\text{hist}}\right)\right)\right)
\]

Where:
* \(w_{\text{sem}} = 0.30\) (Semantic Risk Weight)
* \(w_{\text{perm}} = 0.25\) (Permission Escalation Weight)
* \(w_{\text{beh}} = 0.30\) (Behavioral Anomaly Weight)
* \(w_{\text{hist}} = 0.15\) (Historical Penalty Weight)

---

## 5. Security Policy Mapping Matrix

The continuous trust score \(T_t\) maps directly to a discrete security classification and enforcement action:

| Trust Score Range | Classification | Enforcement Action | Operator Requirement |
| :--- | :--- | :--- | :--- |
| \(80.0 \le T_t \le 100.0\) | **`SAFE`** | **`ALLOW`** | Unrestricted tool execution |
| \(65.0 \le T_t < 80.0\) | **`SUSPICIOUS`** | **`MONITOR`** | Log telemetry & flag minor alerts |
| \(50.0 \le T_t < 65.0\) | **`SUSPICIOUS`** | **`REQUIRE HUMAN APPROVAL`** | Halt execution pending admin review |
| \(0.0 \le T_t < 50.0\) | **`RUG_PULL`** | **`BLOCK`** | Immediate tool revocation & session termination |
