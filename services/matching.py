"""
Column Matching — Upgraded to use semantic embeddings (SBERT).

Changes from original:
- find_matching_columns() now uses ai.semantic_matcher under the hood
- Falls back to rapidfuzz automatically if sentence-transformers not installed
- Returns same dict schema as before, plus a 'method' key showing what was used
- New: find_semantic_duplicates() for near-duplicate row detection
"""

import pandas as pd

# ── NEW: AI semantic matcher ──────────────────────────────────────────────────
try:
    from ai.semantic_matcher import (
        find_semantic_matches,
        deduplicate_semantic,
        get_method_label,
        is_sbert_available,
    )
    _AI_AVAILABLE = True
except ImportError:
    _AI_AVAILABLE = False

# ── Fallback: original rapidfuzz ─────────────────────────────────────────────
try:
    from rapidfuzz import fuzz
    _RAPIDFUZZ_AVAILABLE = True
except ImportError:
    _RAPIDFUZZ_AVAILABLE = False
# ─────────────────────────────────────────────────────────────────────────────


def find_matching_columns(
    df: pd.DataFrame,
    col1: str,
    col2: str,
    threshold: int = 80,
) -> list:
    """
    Find matching values between two columns.

    Drop-in replacement for the original function.
    Threshold is still 0–100 for API compatibility.

    If SBERT is available → uses semantic embeddings (meaning-level match).
    Otherwise → falls back to rapidfuzz character similarity.

    Returns:
        List of dicts: [{index, value1, value2, score, method}, ...]
    """
    float_threshold = threshold / 100.0

    if _AI_AVAILABLE:
        return find_semantic_matches(df, col1, col2, threshold=float_threshold)

    # Original rapidfuzz fallback
    if _RAPIDFUZZ_AVAILABLE:
        matches = []
        for idx in df.index:
            val1 = str(df.loc[idx, col1]) if pd.notna(df.loc[idx, col1]) else ""
            val2 = str(df.loc[idx, col2]) if pd.notna(df.loc[idx, col2]) else ""
            if val1 and val2:
                score = fuzz.ratio(val1, val2)
                if score >= threshold:
                    matches.append({
                        "index": idx,
                        "value1": val1,
                        "value2": val2,
                        "score": score,
                        "method": "fuzzy_fallback",
                    })
        return matches

    return []


def find_semantic_duplicates(
    df: pd.DataFrame,
    columns: list,
    threshold: float = 0.88,
) -> tuple:
    """
    Find near-duplicate rows using semantic similarity.

    This catches duplicates that exact-match dedup misses, e.g.:
        "New York City" vs "NYC, USA"
        "Mohamed Ali" vs "Mohammed Aly"

    Args:
        df: Input dataframe
        columns: Columns to use for semantic fingerprint
        threshold: Similarity threshold (0.88 = very similar, safe default)

    Returns:
        (deduplicated_df, list_of_duplicate_index_pairs)
    """
    if _AI_AVAILABLE:
        return deduplicate_semantic(df, columns, threshold=threshold)

    # No AI available — return unchanged
    return df, []


def get_active_method() -> str:
    """Return a description of the current matching method."""
    if _AI_AVAILABLE:
        return get_method_label()
    elif _RAPIDFUZZ_AVAILABLE:
        return "📏 Fuzzy string matching (install sentence-transformers for AI)"
    return "⚠️ No matching library available"
