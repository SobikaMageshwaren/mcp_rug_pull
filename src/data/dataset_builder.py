"""
Dataset Builder Script.
Saves baseline MCP tools, temporal sequences, and dataset provenance metadata.
"""

import json
import os
from typing import Dict, Any
from src.data.mcp_sources import AUTHENTIC_MCP_TOOLS
from src.data.rugpull_generator import RugPullDatasetGenerator


def build_and_save_datasets(
    raw_dir: str = "data/raw",
    processed_dir: str = "data/processed",
    synthetic_dir: str = "data/synthetic"
) -> Dict[str, Any]:
    """Generates and saves raw, processed, and synthetic dataset files."""
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)
    os.makedirs(synthetic_dir, exist_ok=True)

    # 1. Save Raw Baseline MCP Tools
    raw_path = os.path.join(raw_dir, "mcp_baseline_tools.json")
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(AUTHENTIC_MCP_TOOLS, f, indent=2)

    # 2. Generate Temporal Rug-Pull Sequences
    generator = RugPullDatasetGenerator(random_seed=42)
    temporal_events = generator.build_full_dataset()

    processed_path = os.path.join(processed_dir, "rugpull_dataset.json")
    with open(processed_path, "w", encoding="utf-8") as f:
        json.dump(temporal_events, f, indent=2)

    synthetic_path = os.path.join(synthetic_dir, "temporal_sequences.json")
    with open(synthetic_path, "w", encoding="utf-8") as f:
        json.dump(temporal_events, f, indent=2)

    # Summary Statistics
    total_events = len(temporal_events)
    benign_count = sum(1 for e in temporal_events if e["label"] == "BENIGN")
    rugpull_count = sum(1 for e in temporal_events if e["label"] == "RUG_PULL")

    change_type_dist = {}
    for e in temporal_events:
        ct = e.get("change_type", "UNKNOWN")
        change_type_dist[ct] = change_type_dist.get(ct, 0) + 1

    summary = {
        "total_events": total_events,
        "benign_events": benign_count,
        "rugpull_events": rugpull_count,
        "change_type_distribution": change_type_dist,
        "baseline_tool_count": len(AUTHENTIC_MCP_TOOLS)
    }

    summary_path = os.path.join(processed_dir, "dataset_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"Dataset successfully built and saved:")
    print(f"  - Baseline tools: {len(AUTHENTIC_MCP_TOOLS)} -> {raw_path}")
    print(f"  - Total events: {total_events} (Benign: {benign_count}, Rug-Pull: {rugpull_count})")
    print(f"  - Summary saved to {summary_path}")

    return summary


if __name__ == "__main__":
    build_and_save_datasets()
