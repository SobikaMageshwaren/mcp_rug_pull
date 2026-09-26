"""
Ablation Study Evaluator.
Evaluates the incremental contribution of each component across 6 configuration levels (A to F).
"""

from typing import List, Dict, Any
from src.behavioral.baseline import StaticRuleDetector, SemanticOnlyDetector
from src.behavioral.anomaly_detector import BehavioralAnomalyDetector
from src.trust.trust_engine import AdaptiveTrustEngine
from src.agent.security_agent import SecurityInvestigationAgent
from src.semantic.metadata_analyzer import MetadataAnalyzer
from src.evaluation.metrics import compute_classification_metrics


class AblationStudyEvaluator:
    """Runs ablation experiments across configuration levels A through F."""

    def __init__(self):
        self.rule_detector = StaticRuleDetector()
        self.semantic_detector = SemanticOnlyDetector(drift_threshold=0.20)
        self.behavioral_detector = BehavioralAnomalyDetector()
        self.metadata_analyzer = MetadataAnalyzer()
        self.trust_engine = AdaptiveTrustEngine()
        self.agent = SecurityInvestigationAgent()

    def run_ablation(self, train_events: List[Dict[str, Any]], test_events: List[Dict[str, Any]], baseline_map: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
        """Executes full ablation suite on temporal test dataset."""

        # Fit behavioral detector on benign training samples
        benign_train = [e for e in train_events if e["label"] == "BENIGN"]
        if benign_train:
            self.behavioral_detector.fit(benign_train, baseline_map)

        y_true = [1 if e["label"] == "RUG_PULL" else 0 for e in test_events]

        # Config A: Rules Only
        pred_a = []
        for e in test_events:
            base = baseline_map.get(e["tool_id"], e)
            res = self.rule_detector.predict(base, e)
            pred_a.append(1 if res["classification"] == "RUG_PULL" else 0)

        # Config B: Transformer Only
        pred_b = []
        for e in test_events:
            base = baseline_map.get(e["tool_id"], e)
            res = self.semantic_detector.predict(base, e)
            pred_b.append(1 if res["classification"] == "RUG_PULL" else 0)

        # Config C: Behavioral ML Only
        pred_c = []
        for e in test_events:
            base = baseline_map.get(e["tool_id"], e)
            score = self.behavioral_detector.predict_anomaly_score(e, base)
            pred_c.append(1 if score >= 0.40 else 0)

        # Config D: Transformer + Behavioral ML (Simple Average)
        pred_d = []
        for e in test_events:
            base = baseline_map.get(e["tool_id"], e)
            drift = self.semantic_detector.predict(base, e)["semantic_drift"]
            beh_score = self.behavioral_detector.predict_anomaly_score(e, base)
            comb_score = 0.5 * drift + 0.5 * beh_score
            pred_d.append(1 if comb_score >= 0.30 else 0)

        # Config E: D + Adaptive Trust Engine
        pred_e = []
        for e in test_events:
            base = baseline_map.get(e["tool_id"], e)
            meta_res = self.metadata_analyzer.analyze(base, e)
            sem_risk = meta_res["metadata_risk_score"]
            perm_risk = meta_res["permission_risk_score"]
            beh_score = self.behavioral_detector.predict_anomaly_score(e, base)
            trust_eval = self.trust_engine.evaluate_event(e, sem_risk, perm_risk, beh_score)
            pred_e.append(1 if trust_eval["classification"] in ["SUSPICIOUS", "RUG_PULL"] else 0)

        # Config F: Full System (Transformer + Behavioral + Adaptive Trust + RAG + Agentic AI)
        pred_f = []
        for e in test_events:
            base = baseline_map.get(e["tool_id"], e)
            agent_res = self.agent.investigate(base, e)
            pred_f.append(1 if agent_res["classification"] == "RUG_PULL" or (agent_res["classification"] == "SUSPICIOUS" and agent_res["recommended_action"] == "BLOCK") else 0)

        return {
            "Config_A_Rules_Only": compute_classification_metrics(y_true, pred_a),
            "Config_B_Transformer_Only": compute_classification_metrics(y_true, pred_b),
            "Config_C_Behavioral_ML_Only": compute_classification_metrics(y_true, pred_c),
            "Config_D_Transformer_Plus_Behavioral": compute_classification_metrics(y_true, pred_d),
            "Config_E_D_Plus_Adaptive_Trust": compute_classification_metrics(y_true, pred_e),
            "Config_F_Full_System": compute_classification_metrics(y_true, pred_f)
        }
