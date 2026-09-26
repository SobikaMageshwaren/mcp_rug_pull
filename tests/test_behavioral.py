"""
Unit tests for behavioral feature extraction and anomaly detection.
"""

import pytest
import numpy as np
from src.data.mcp_sources import AUTHENTIC_MCP_TOOLS
from src.data.rugpull_generator import RugPullDatasetGenerator
from src.behavioral import BehavioralFeatureExtractor, BehavioralAnomalyDetector


def test_feature_extractor():
    extractor = BehavioralFeatureExtractor()
    tool = AUTHENTIC_MCP_TOOLS[0]
    vec = extractor.extract_features(tool)
    assert isinstance(vec, np.ndarray)
    assert len(vec) == 11


def test_anomaly_detector_fit_and_predict():
    detector = BehavioralAnomalyDetector()
    gen = RugPullDatasetGenerator()
    events = gen.build_full_dataset()

    benign_events = [e for e in events if e["label"] == "BENIGN"]
    detector.fit(benign_events)

    tool = AUTHENTIC_MCP_TOOLS[0]
    _, beh_attack = gen.generate_behavioral_rugpull(tool)

    benign_score = detector.predict_anomaly_score(tool)
    attack_score = detector.predict_anomaly_score(beh_attack)

    assert 0.0 <= benign_score <= 1.0
    assert 0.0 <= attack_score <= 1.0
    assert attack_score > benign_score
