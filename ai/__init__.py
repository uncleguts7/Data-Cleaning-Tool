"""
AI Module — Core AI/ML components for the Data Cleaning Tool.

Modules:
    llm_advisor      — Claude API: explains decisions, generates reports, suggests strategies
    anomaly_detector — IsolationForest + LOF ensemble with explainability
    semantic_matcher — SBERT embeddings for meaning-level column matching & dedup
"""

from ai.llm_advisor import (
    suggest_cleaning_strategy,
    explain_anomalies,
    generate_quality_report,
    render_strategy_card,
    render_anomaly_explanation,
    render_quality_report,
)

from ai.anomaly_detector import (
    detect_anomalies_ensemble,
    remove_anomalies,
    render_anomaly_results,
)

from ai.semantic_matcher import (
    find_semantic_matches,
    deduplicate_semantic,
    semantic_similarity,
    is_sbert_available,
    get_method_label,
)

__all__ = [
    # LLM Advisor
    "suggest_cleaning_strategy",
    "explain_anomalies",
    "generate_quality_report",
    "render_strategy_card",
    "render_anomaly_explanation",
    "render_quality_report",
    # Anomaly Detection
    "detect_anomalies_ensemble",
    "remove_anomalies",
    "render_anomaly_results",
    # Semantic Matching
    "find_semantic_matches",
    "deduplicate_semantic",
    "semantic_similarity",
    "is_sbert_available",
    "get_method_label",
]