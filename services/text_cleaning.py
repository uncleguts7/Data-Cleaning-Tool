"""Text cleaning operations for paragraph/text data."""

import re
from dataclasses import dataclass

# Try to import spellchecker, if not available, spell correction will be limited
try:
    from spellchecker import SpellChecker
    SPELLCHECKER_AVAILABLE = True
except ImportError:
    SPELLCHECKER_AVAILABLE = False


@dataclass
class TextCleaningResult:
    """Result of text cleaning operation."""
    original_text: str
    cleaned_text: str
    changes_made: list
    stats: dict


# Common misspellings dictionary (fallback if spellchecker not available)
COMMON_MISSPELLINGS = {
    "teh":  "the",
    "thier": "their",
    "recieve": "receive",
    "seperate": "separate",
    "definately": "definitely",
    "occured": "occurred",
    "untill": "until",
    "begining": "beginning",
    "beleive": "believe",
    "comming": "coming",
    "completly": "completely",
    "enviroment": "environment",
    "explaination": "explanation",
    "finaly":  "finally",
    "goverment": "government",
    "happend": "happened",
    "immediatly": "immediately",
    "knowlege": "knowledge",
    "libary":  "library",
    "neccessary": "necessary",
    "ocasionally": "occasionally",
    "probaly": "probably",
    "realy": "really",
    "remeber": "remember",
    "successfull":  "successful",
    "tommorow": "tomorrow",
    "truely": "truly",
    "wierd": "weird",
    "wellcome": "welcome",
    "welcom": "welcome",
    "writting": "writing",
    "exoplain": "explain",
    "explian": "explain",
    "waht": "what",
    "becuase": "because",
    "becasue": "because",
    "freind":  "friend",
    "diffrent": "different",
    "alot": "a lot",
    "somthing": "something",
    "everthing": "everything",
    "watever": "whatever",
    "whatver": "whatever",
}

# Words to ignore during spell checking (technical terms, names, etc.)
IGNORE_WORDS = {
    "streamlit", "pandas", "numpy", "python", "javascript", "html", "css",
    "github", "stackoverflow", "api", "json", "xml", "sql", "http", "https",
    "www", "com", "org", "net", "io", "app", "config", "utils", "init",
}


def is_code_snippet(text: str) -> bool:
    """Detect if text contains code snippets."""
    code_patterns = [
        r'\$\w+\s*=',
        r'<\?php',
        r'\?>',
        r'function\s+\w+\s*\(',
        r'def\s+\w+\s*\(',
        r'class\s+\w+',
        r'import\s+\w+',
        r'const\s+\w+\s*=',
        r'let\s+\w+\s*=',
        r'var\s+\w+\s*=',
        r'=>',
        r'console\.log',
        r'#include',
    ]
    
    for pattern in code_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def extract_code_blocks(text:  str) -> tuple:
    """Extract code blocks and replace with placeholders."""
    code_blocks = {}
    counter = [0]
    
    def replace_with_placeholder(match):
        placeholder = f"__CODE_BLOCK_{counter[0]}__"
        code_blocks[placeholder] = match.group(0)
        counter[0] += 1
        return placeholder
    
    # Inline code with backticks
    text = re.sub(r'`[^`]+`', replace_with_placeholder, text)
    
    # Triple backtick code blocks
    text = re.sub(r'```[\s\S]*?```', replace_with_placeholder, text)
    
    # PHP code
    text = re.sub(r'<\?php[\s\S]*?\?>', replace_with_placeholder, text)
    
    # Variable assignments like $x = 5;
    text = re.sub(r'\$\w+\s*=\s*[^;]+;', replace_with_placeholder, text)
    
    # HTML tags
    text = re.sub(r'<[^>]+>', replace_with_placeholder, text)
    
    return text, code_blocks


def restore_code_blocks(text: str, code_blocks: dict) -> str:
    """Restore code blocks from placeholders."""
    for placeholder, code in code_blocks.items():
        text = text.replace(placeholder, code)
    return text


def clean_extra_whitespace(text:  str) -> tuple:
    """Remove extra whitespace."""
    original = text
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+\n', '\n', text)
    text = re.sub(r'\n[ \t]+', '\n', text)
    text = text.strip()
    return text, text != original


def fix_punctuation(text: str) -> tuple:
    """Fix common punctuation issues."""
    original = text
    text = re.sub(r'\s+([.,!?;:])', r'\1', text)
    text = re.sub(r'([.!?]){2,}', r'\1', text)
    text = re.sub(r',{2,}', ',', text)
    return text, text != original


def remove_special_chars_and_fix_words(text: str, preserve_code: bool = True) -> tuple:
    """Remove special characters from words and attempt to fix the resulting word."""
    original = text
    code_blocks = {}
    
    if preserve_code:
        text, code_blocks = extract_code_blocks(text)
    
    # Protect emails
    emails = {}
    email_counter = [0]
    
    def save_email(match):
        placeholder = f"__EMAIL_{email_counter[0]}__"
        emails[placeholder] = match. group(0)
        email_counter[0] += 1
        return placeholder
    
    text = re. sub(r'[\w\.-]+@[\w\.-]+\.\w+', save_email, text)
    
    # Protect URLs
    urls = {}
    url_counter = [0]
    
    def save_url(match):
        placeholder = f"__URL_{url_counter[0]}__"
        urls[placeholder] = match.group(0)
        url_counter[0] += 1
        return placeholder
    
    text = re. sub(r'https?://[^\s]+|www\.[^\s]+', save_url, text)
    
    # Initialize spell checker if available
    spell = None
    if SPELLCHECKER_AVAILABLE:
        spell = SpellChecker()
    
    def fix_word_with_special_chars(match):
        """Fix a word that contains special characters."""
        word = match.group(0)
        
        # Remove special characters from the word
        cleaned_word = re.sub(r'[%$#@! ^&*]+', '', word)
        
        # If spell checker is available, try to correct the word
        if spell and cleaned_word. isalpha() and len(cleaned_word) > 2:
            # Check if the cleaned word is misspelled
            if cleaned_word. lower() not in spell and cleaned_word. lower() not in IGNORE_WORDS:
                # Get the best correction
                correction = spell.correction(cleaned_word. lower())
                if correction and correction != cleaned_word. lower():
                    # Preserve original capitalization
                    if word[0].isupper():
                        return correction. capitalize()
                    return correction
        
        return cleaned_word
    
    # Find words with special characters in the middle and fix them
    # Pattern matches words that have letters, then special chars, then more letters
    text = re.sub(r'\b\w*[%$#@!^&*]+\w*\b', fix_word_with_special_chars, text)
    
    # Restore emails and URLs
    for placeholder, email in emails.items():
        text = text.replace(placeholder, email)
    for placeholder, url in urls.items():
        text = text.replace(placeholder, url)
    
    if preserve_code:
        text = restore_code_blocks(text, code_blocks)
    
    return text, text != original


def fix_spelling(text: str, preserve_code: bool = True) -> tuple:
    """Fix spelling mistakes using spell checker."""
    original = text
    code_blocks = {}
    corrections = []
    
    if preserve_code:
        text, code_blocks = extract_code_blocks(text)
    
    # Protect emails
    emails = {}
    email_counter = [0]
    
    def save_email(match):
        placeholder = f"__EMAIL_{email_counter[0]}__"
        emails[placeholder] = match.group(0)
        email_counter[0] += 1
        return placeholder
    
    text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', save_email, text)
    
    # Protect URLs
    urls = {}
    url_counter = [0]
    
    def save_url(match):
        placeholder = f"__URL_{url_counter[0]}__"
        urls[placeholder] = match.group(0)
        url_counter[0] += 1
        return placeholder
    
    text = re.sub(r'https?://[^\s]+|www\.[^\s]+', save_url, text)
    
    # First, apply common misspellings dictionary
    for wrong, correct in COMMON_MISSPELLINGS.items():
        pattern = r'\b' + wrong + r'\b'
        if re.search(pattern, text, re.IGNORECASE):
            def replace_preserve_case(match):
                matched = match.group(0)
                if matched[0].isupper():
                    return correct.capitalize()
                return correct
            
            text = re.sub(pattern, replace_preserve_case, text, flags=re.IGNORECASE)
            corrections.append(f"'{wrong}' -> '{correct}'")
    
    # Then use spell checker for remaining words
    if SPELLCHECKER_AVAILABLE:
        spell = SpellChecker()
        
        # Find all words
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        
        for word in words:
            # Skip short words, placeholders, and ignored words
            if len(word) <= 2:
                continue
            if word. startswith('__') and word.endswith('__'):
                continue
            if word. lower() in IGNORE_WORDS:
                continue
            
            # Check if word is misspelled
            if word.lower() not in spell:
                correction = spell.correction(word.lower())
                
                # Only apply if we got a good correction
                if correction and correction != word.lower():
                    # Create pattern for this specific word
                    pattern = r'\b' + re.escape(word) + r'\b'
                    
                    # Preserve capitalization
                    if word[0].isupper():
                        replacement = correction.capitalize()
                    else:
                        replacement = correction
                    
                    # Only replace if not already in corrections
                    if f"'{word. lower()}'" not in str(corrections):
                        text = re.sub(pattern, replacement, text)
                        corrections.append(f"'{word}' -> '{replacement}'")
    
    # Restore emails and URLs
    for placeholder, email in emails.items():
        text = text.replace(placeholder, email)
    for placeholder, url in urls. items():
        text = text. replace(placeholder, url)
    
    if preserve_code: 
        text = restore_code_blocks(text, code_blocks)
    
    return text, text != original, corrections


def capitalize_sentences(text: str) -> tuple:
    """Capitalize the first letter of each sentence."""
    original = text
    
    text = re.sub(
        r'([. !?]\s+)([a-z])',
        lambda m: m.group(1) + m.group(2).upper(),
        text
    )
    
    if text and text[0].islower():
        text = text[0].upper() + text[1:]
    
    text = re.sub(
        r'(\n\s*)([a-z])',
        lambda m: m.group(1) + m.group(2).upper(),
        text
    )
    
    return text, text != original


def fix_common_typos(text: str) -> tuple:
    """Fix common typing mistakes (contractions)."""
    original = text
    
    typo_fixes = [
        (r'\bi\b', 'I'),
        (r'\bdont\b', "don't"),
        (r'\bcant\b', "can't"),
        (r'\bwont\b', "won't"),
        (r'\bisnt\b', "isn't"),
        (r'\barent\b', "aren't"),
        (r'\bwasnt\b', "wasn't"),
        (r'\bwerent\b', "weren't"),
        (r'\bdidnt\b', "didn't"),
        (r'\bdoesnt\b', "doesn't"),
        (r'\bhasnt\b', "hasn't"),
        (r'\bhavent\b', "haven't"),
        (r'\bhadnt\b', "hadn't"),
        (r'\bshouldnt\b', "shouldn't"),
        (r'\bwouldnt\b', "wouldn't"),
        (r'\bcouldnt\b', "couldn't"),
        (r'\bIm\b', "I'm"),
        (r'\byoure\b', "you're"),
        (r'\btheyre\b', "they're"),
        (r'\btheres\b', "there's"),
        (r'\bheres\b', "here's"),
        (r'\bwheres\b', "where's"),
        (r'\blets\b', "let's"),
    ]
    
    for pattern, replacement in typo_fixes: 
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text, text != original


def remove_duplicate_words(text: str) -> tuple:
    """Remove accidentally repeated words."""
    original = text
    text = re.sub(r'\b(\w+)(\s+\1\b)+', r'\1', text, flags=re.IGNORECASE)
    return text, text != original


def clean_text(
    text: str,
    fix_whitespace: bool = True,
    fix_punctuation_errors: bool = True,
    remove_special_chars: bool = True,
    capitalize:  bool = True,
    fix_typos: bool = True,
    remove_duplicates: bool = True,
    fix_spelling_errors: bool = True,
    preserve_code: bool = True
) -> TextCleaningResult:
    """Main text cleaning function."""
    
    if not text or not text.strip():
        return TextCleaningResult(
            original_text=text,
            cleaned_text=text,
            changes_made=[],
            stats={
                "total_changes": 0,
                "original_length": 0,
                "cleaned_length": 0,
                "characters_removed": 0,
                "is_code":  False,
                "spelling_corrections": [],
                "spellchecker_available":  SPELLCHECKER_AVAILABLE
            }
        )
    
    changes_made = []
    cleaned = text
    spelling_corrections = []
    
    if fix_whitespace:
        cleaned, changed = clean_extra_whitespace(cleaned)
        if changed:
            changes_made. append("Fixed extra whitespace")
    
    # Remove special characters AND fix the resulting words
    if remove_special_chars:
        cleaned, changed = remove_special_chars_and_fix_words(cleaned, preserve_code)
        if changed:
            changes_made.append("Removed special characters and fixed words")
    
    if fix_punctuation_errors: 
        cleaned, changed = fix_punctuation(cleaned)
        if changed:
            changes_made.append("Fixed punctuation")
    
    if remove_duplicates:
        cleaned, changed = remove_duplicate_words(cleaned)
        if changed: 
            changes_made.append("Removed duplicate words")
    
    if fix_typos:
        cleaned, changed = fix_common_typos(cleaned)
        if changed:
            changes_made.append("Fixed common typos")
    
    if fix_spelling_errors:
        cleaned, changed, corrections = fix_spelling(cleaned, preserve_code)
        if changed:
            changes_made.append(f"Fixed spelling ({len(corrections)} corrections)")
            spelling_corrections = corrections
    
    if capitalize:
        cleaned, changed = capitalize_sentences(cleaned)
        if changed:
            changes_made.append("Capitalized sentences")
    
    stats = {
        "total_changes": len(changes_made),
        "original_length": len(text),
        "cleaned_length": len(cleaned),
        "characters_removed": len(text) - len(cleaned),
        "is_code": False,
        "spelling_corrections":  spelling_corrections,
        "spellchecker_available": SPELLCHECKER_AVAILABLE
    }
    
    return TextCleaningResult(
        original_text=text,
        cleaned_text=cleaned,
        changes_made=changes_made,
        stats=stats
    )