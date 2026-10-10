# config/learned_patterns.py  ← NEW, auto-updated by llm_advisor
import json, os

PATTERNS_FILE = os.path.join(os.path.dirname(__file__), "learned_patterns.json")

def load_patterns() -> dict:
    if os.path.exists(PATTERNS_FILE):
        with open(PATTERNS_FILE) as f:
            return json.load(f)
    return {"integer_cols": [], "monetary_cols": [], "id_cols": []}

def save_pattern(category: str, column_name: str):
    """Called by llm_advisor when it identifies a column type confidently."""
    patterns = load_patterns()
    if column_name not in patterns.get(category, []):
        patterns.setdefault(category, []).append(column_name)
        with open(PATTERNS_FILE, "w") as f:
            json.dump(patterns, f, indent=2)