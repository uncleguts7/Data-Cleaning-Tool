"""
Semantic Matcher Module — Upgrades column matching from character-level
fuzzy matching (RapidFuzz) to meaning-level embedding similarity.

Why this matters:
    rapidfuzz("New York City", "NYC") → ~40% (fails)
    semantic_similarity("New York City", "NYC") → ~92% (correct)

Uses sentence-transformers (all-MiniLM-L6-v2) locally — no API calls needed.
Falls back gracefully to rapidfuzz if the model isn't installed.
"""

import pandas as pd
import numpy as np
import streamlit as st
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Try to load sentence-transformers; fall back to rapidfuzz
_model = None
_SBERT_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer, util as sbert_util
    _SBERT_AVAILABLE = True
except ImportError:
    pass

try:
    from rapidfuzz import fuzz as _fuzz
    _RAPIDFUZZ_AVAILABLE = True
except ImportError:
    _RAPIDFUZZ_AVAILABLE = False


def _load_model():
    """Lazy-load the SBERT model (cached in session for Streamlit)."""
    global _model
    if _model is None and _SBERT_AVAILABLE:
        try:
            _model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("SBERT model loaded: all-MiniLM-L6-v2")
        except Exception as e:
            logger.warning(f"Could not load SBERT model: {e}")
    return _model


def _embed(texts: list, model) -> np.ndarray:
    """Encode a list of strings to embeddings."""
    return model.encode(texts, convert_to_tensor=False, show_progress_bar=False)


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two vectors."""
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def semantic_similarity(text1: str, text2: str) -> float:
    """
    Compute semantic similarity between two strings [0.0, 1.0].

    Uses SBERT embeddings if available, otherwise falls back to
    character-level fuzzy ratio normalized to [0, 1].
    """
    if not text1 or not text2:
        return 0.0

    model = _load_model()

    if model is not None:
        try:
            embeddings = _embed([str(text1), str(text2)], model)
            score = _cosine_similarity(embeddings[0], embeddings[1])
            # Cosine can return slightly negative values; clamp to [0, 1]
            return max(0.0, min(1.0, score))
        except Exception as e:
            logger.warning(f"SBERT similarity failed, falling back: {e}")

    # Fallback: rapidfuzz
    if _RAPIDFUZZ_AVAILABLE:
        return _fuzz.ratio(str(text1), str(text2)) / 100.0

    # Last resort: exact match
    return 1.0 if str(text1).lower() == str(text2).lower() else 0.0


def find_semantic_matches(
    df: pd.DataFrame,
    col1: str,
    col2: str,
    threshold: float = 0.75,
    batch_size: int = 64,
) -> list:
    """
    Find semantically similar pairs between two columns using embeddings.

    This is a drop-in upgrade for services/matching.py's find_matching_columns().
    Returns the same schema but with real semantic scores.

    Args:
        df: Input dataframe
        col1: First column name
        col2: Second column name
        threshold: Minimum similarity [0.0, 1.0] — 0.75 ≈ 80 in old fuzz scale
        batch_size: Embedding batch size (tune for memory)

    Returns:
        List of dicts: [{index, value1, value2, score, method}, ...]
    """
    model = _load_model()
    method = "sbert" if model is not None else "fuzzy_fallback"

    vals1 = [str(df.loc[idx, col1]) if pd.notna(df.loc[idx, col1]) else "" for idx in df.index]
    vals2 = [str(df.loc[idx, col2]) if pd.notna(df.loc[idx, col2]) else "" for idx in df.index]

    matches = []

    if model is not None:
        try:
            # Batch encode both columns at once for efficiency
            all_texts = vals1 + vals2
            all_embs = _embed(all_texts, model)
            embs1 = all_embs[: len(vals1)]
            embs2 = all_embs[len(vals1) :]

            for i, idx in enumerate(df.index):
                if not vals1[i] or not vals2[i]:
                    continue
                score = _cosine_similarity(embs1[i], embs2[i])
                score = max(0.0, min(1.0, score))
                if score >= threshold:
                    matches.append({
                        "index": idx,
                        "value1": vals1[i],
                        "value2": vals2[i],
                        "score": round(score * 100, 2),  # keep same 0-100 scale as old API
                        "method": method,
                    })
            return matches
        except Exception as e:
            logger.warning(f"Batch SBERT failed, falling back row-by-row: {e}")

    # Row-by-row fallback
    for i, idx in enumerate(df.index):
        if not vals1[i] or not vals2[i]:
            continue
        score = semantic_similarity(vals1[i], vals2[i])
        if score >= threshold:
            matches.append({
                "index": idx,
                "value1": vals1[i],
                "value2": vals2[i],
                "score": round(score * 100, 2),
                "method": method,
            })

    return matches


def deduplicate_semantic(
    df: pd.DataFrame,
    columns: list,
    threshold: float = 0.88,
) -> tuple:
    """
    Find near-duplicate rows using semantic similarity on selected columns.

    Rows that are semantically near-identical (even with different wording)
    are flagged. This catches duplicates that exact-match dedup misses.

    Args:
        df: Input dataframe
        columns: Columns to use for semantic fingerprint
        threshold: Similarity threshold (0.88 = very similar, safe to flag)

    Returns:
        (deduplicated_df, list_of_duplicate_index_pairs)
    """
    model = _load_model()
    if model is None:
        st.warning("SBERT not available — semantic deduplication skipped.")
        return df, []

    # Build a text "fingerprint" per row from selected columns
    def row_text(row):
        parts = [str(row[c]) for c in columns if c in row.index and pd.notna(row[c])]
        return " | ".join(parts)

    texts = [row_text(df.iloc[i]) for i in range(len(df))]

    try:
        embeddings = _embed(texts, model)
    except Exception as e:
        st.warning(f"Semantic deduplication encoding failed: {e}")
        return df, []

    duplicate_pairs = []
    flagged_indices = set()

    # O(n²) comparison — fine for typical cleaning datasets (<10k rows)
    for i in range(len(embeddings)):
        if i in flagged_indices:
            continue
        for j in range(i + 1, len(embeddings)):
            if j in flagged_indices:
                continue
            score = _cosine_similarity(embeddings[i], embeddings[j])
            if score >= threshold:
                duplicate_pairs.append((df.index[i], df.index[j], round(score, 4)))
                flagged_indices.add(j)  # Keep first, flag later

    duplicate_actual_indices = [pair[1] for pair in duplicate_pairs]
    df_clean = df.drop(index=duplicate_actual_indices).reset_index(drop=True)

    return df_clean, duplicate_pairs


def is_sbert_available() -> bool:
    """Check whether SBERT embedding model is available."""
    return _SBERT_AVAILABLE and _load_model() is not None


def get_method_label() -> str:
    """Return a human-readable label for the current matching method."""
    if is_sbert_available():
        return "🧠 Semantic (SBERT embeddings)"
    elif _RAPIDFUZZ_AVAILABLE:
        return "📏 Fuzzy string matching (install sentence-transformers for AI matching)"
    return "🔤 Exact matching (fallback)"