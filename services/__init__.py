"""Text cleaning operations for paragraph/text data."""

import re
from dataclasses import dataclass


@dataclass
class TextCleaningResult:
    """Result of text cleaning operation."""
    original_text: str
    cleaned_text: str
    changes_made: list
    stats: dict


def is_code_snippet(text: str) -> bool:
    """Detect if text contains code snippets. 
    
    Args:
        text: Text to analyze
        
    Returns:
        True if text appears to contain code
    """
    code_patterns = [
        r'\$\w+\s*=',  # PHP/Perl variables:  $x = 5
        r'<\?php',  # PHP opening tag
        r'\?>',  # PHP closing tag
        r'function\s+\w+\s*\(',  # Function declarations
        r'def\s+\w+\s*\(',  # Python function
        r'class\s+\w+',  # Class declarations
        r'import\s+\w+',  # Import statements
        r'from\s+\w+\s+import',  # Python imports
        r'const\s+\w+\s*=',  # JavaScript const
        r'let\s+\w+\s*=',  # JavaScript let
        r'var\s+\w+\s*=',  # JavaScript var
        r'=>',  # Arrow functions
        r'console\.log',  # JavaScript console
        r'print\s*\(',  # Print statements
        r'return\s+',  # Return statements
        r'if\s*\(. +\)\s*{',  # If statements with braces
        r'for\s*\(.+\)\s*{',  # For loops
        r'while\s*\(.+\)\s*{',  # While loops
        r'\w+\.\w+\(',  # Method calls
        r'#include',  # C/C++ includes
        r'using\s+namespace',  # C++ namespace
        r'public\s+static',  # Java/C# modifiers
        r'private\s+\w+',  # Access modifiers
        r'<\w+>.*</\w+>',  # HTML/XML tags
        r'\{\{.*\}\}',  # Template syntax
        r'SELECT\s+. +\s+FROM',  # SQL queries
        r'INSERT\s+INTO',  # SQL insert
        r'UPDATE\s+\w+\s+SET',  # SQL update
    ]
    
    for pattern in code_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def extract_code_blocks(text: str) -> tuple[str, dict]:
    """Extract code blocks and replace with placeholders.
    
    Args:
        text: Input text
        
    Returns:
        Tuple of (text with placeholders, dict of placeholder->code)
    """
    code_blocks = {}
    placeholder_counter = [0]
    
    def replace_with_placeholder(match):
        placeholder = f"__CODE_BLOCK_{placeholder_counter[0]}__"
        code_blocks[placeholder] = match. group(0)
        placeholder_counter[0] += 1
        return placeholder
    
    # Pattern for inline code with backticks
    text = re.sub(r'`[^`]+`', replace_with_placeholder, text)
    
    # Pattern for code blocks with triple backticks
    text = re.sub(r'```[\s\S]*?```', replace_with_placeholder, text)
    
    # Pattern for PHP code
    text = re.sub(r'<\?php[\s\S]*?\?>', replace_with_placeholder, text)
    
    # Pattern for variable assignments (like $x = 5;)
    text = re.sub(r'\$\w+\s*=\s*[^;]+;', replace_with_placeholder, text)
    
    # Pattern for HTML/XML tags
    text = re.sub(r'<[^>]+>', replace_with_placeholder, text)
    
    return text, code_blocks


def restore_code_blocks(text: str, code_blocks: dict) -> str:
    """Restore code blocks from placeholders.
    
    Args:
        text: Text with placeholders
        code_blocks: Dict of placeholder->code
        
    Returns:
        Text with code blocks restored
    """
    for placeholder, code in code_blocks. items():
        text = text. replace(placeholder, code)
    return text


def clean_extra_whitespace(text: str) -> tuple[str, bool]:
    """Remove extra whitespace while preserving paragraph structure.
    
    Args:
        text: Input text
        
    Returns:
        Tuple of (cleaned text, whether changes were made)
    """
    original = text
    
    # Replace multiple spaces with single space
    text = re.sub(r'[ \t]+', ' ', text)
    
    # Replace more than 2 consecutive newlines with 2
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remove spaces at the beginning/end of lines
    text = re.sub(r'[ \t]+\n', '\n', text)
    text = re.sub(r'\n[ \t]+', '\n', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text, text != original


def fix_punctuation(text: str) -> tuple[str, bool]:
    """Fix common punctuation issues.
    
    Args:
        text: Input text
        
    Returns:
        Tuple of (cleaned text, whether changes were made)
    """
    original = text
    
    # Remove space before punctuation
    text = re.sub(r'\s+([.,!?;:])', r'\1', text)
    
    # Add space after punctuation if missing (but not for decimals or URLs)
    text = re.sub(r'([.,!?;: ])([A-Za-z\u0600-\u06FF])', r'\1 \2', text)
    
    # Fix multiple punctuation marks
    text = re. sub(r'([. !?]){2,}', r'\1', text)
    
    # Fix comma spacing
    text = re.sub(r',{2,}', ',', text)
    
    return text, text != original


def remove_special_characters(text: str, preserve_code: bool = True) -> tuple[str, bool]:
    """Remove unwanted special characters from text.
    
    Args:
        text: Input text
        preserve_code: Whether to preserve code snippets
        
    Returns: 
        Tuple of (cleaned text, whether changes were made)
    """
    original = text
    code_blocks = {}
    
    if preserve_code:
        text, code_blocks = extract_code_blocks(text)
    
    # Characters to remove (excluding those in emails, URLs, and basic punctuation)
    # Keep: letters, numbers, basic punctuation, Arabic chars, spaces
    
    # First, protect emails
    email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
    emails = {}
    email_counter = [0]
    
    def save_email(match):
        placeholder = f"__EMAIL_{email_counter[0]}__"
        emails[placeholder] = match.group(0)
        email_counter[0] += 1
        return placeholder
    
    text = re.sub(email_pattern, save_email, text)
    
    # Protect URLs
    url_pattern = r'https?://[^\s]+|www\.[^\s]+'
    urls = {}
    url_counter = [0]
    
    def save_url(match):
        placeholder = f"__URL_{url_counter[0]}__"
        urls[placeholder] = match.group(0)
        url_counter[0] += 1
        return placeholder
    
    text = re.sub(url_pattern, save_url, text)
    
    # Remove unwanted special characters
    # Keep: word chars, whitespace, basic punctuation, Arabic
    text = re.sub(r'[^\w\s\u0600-\u06FF.,!?;:\'"()\-\n@#]', '', text)
    
    # Remove standalone special chars that aren't part of meaningful content
    text = re.sub(r'(? <!\w)[@#$%^&*]+(?!\w)', '', text)
    
    # Restore emails
    for placeholder, email in emails.items():
        text = text.replace(placeholder, email)
    
    # Restore URLs
    for placeholder, url in urls.items():
        text = text.replace(placeholder, url)
    
    if preserve_code:
        text = restore_code_blocks(text, code_blocks)
    
    return text, text != original


def capitalize_sentences(text: str) -> tuple[str, bool]:
    """Capitalize the first letter of each sentence.
    
    Args:
        text: Input text
        
    Returns:
        Tuple of (cleaned text, whether changes were made)
    """
    original = text
    
    # Capitalize after period, exclamation, question mark
    text = re.sub(
        r'([.!?]\s+)([a-z])',
        lambda m: m.group(1) + m.group(2).upper(),
        text
    )
    
    # Capitalize first character of text
    if text and text[0].islower():
        text = text[0].upper() + text[1:]
    
    # Capitalize after newlines
    text = re.sub(
        r'(\n\s*)([a-z])',
        lambda m: m.group(1) + m.group(2).upper(),
        text
    )
    
    return text, text != original


def fix_common_typos(text: str) -> tuple[str, bool]:
    """Fix common typing mistakes.
    
    Args:
        text: Input text
        
    Returns:
        Tuple of (cleaned text, whether changes were made)
    """
    original = text
    
    # Common typo patterns
    typo_fixes = [
        (r'\bi\b', 'I'),  # Lowercase 'i' standing alone
        (r"dont", "don't"),
        (r"cant", "can't"),
        (r"wont", "won't"),
        (r"isnt", "isn't"),
        (r"arent", "aren't"),
        (r"wasnt", "wasn't"),
        (r"werent", "weren't"),
        (r"didnt", "didn't"),
        (r"doesnt", "doesn't"),
        (r"hasnt", "hasn't"),
        (r"havent", "haven't"),
        (r"hadnt", "hadn't"),
        (r"shouldnt", "shouldn't"),
        (r"wouldnt", "wouldn't"),
        (r"couldnt", "couldn't"),
        (r"Im\b", "I'm"),
        (r"youre\b", "you're"),
        (r"theyre\b", "they're"),
        (r"theres\b", "there's"),
        (r"heres\b", "here's"),
        (r"wheres\b", "where's"),
        (r"lets\b(? !\s+\w+\s+go)", "let's"),  # "lets" -> "let's" but not "lets X go"
    ]
    
    for pattern, replacement in typo_fixes: 
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text, text != original


def remove_duplicate_words(text: str) -> tuple[str, bool]:
    """Remove accidentally repeated words.
    
    Args:
        text: Input text
        
    Returns:
        Tuple of (cleaned text, whether changes were made)
    """
    original = text
    
    # Remove duplicate consecutive words (case-insensitive)
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
    preserve_code: bool = True
) -> TextCleaningResult:
    """Main text cleaning function.
    
    Args:
        text: Input text to clean
        fix_whitespace:  Whether to fix whitespace issues
        fix_punctuation_errors: Whether to fix punctuation
        remove_special_chars: Whether to remove special characters
        capitalize:  Whether to capitalize sentences
        fix_typos: Whether to fix common typos
        remove_duplicates:  Whether to remove duplicate words
        preserve_code: Whether to preserve code snippets
        
    Returns:
        TextCleaningResult with original, cleaned text, and stats
    """
    if not text or not text.strip():
        return TextCleaningResult(
            original_text=text,
            cleaned_text=text,
            changes_made=[],
            stats={"total_changes": 0}
        )
    
    changes_made = []
    cleaned = text
    
    # Detect if entire text is code
    if is_code_snippet(text) and preserve_code:
        # Be more conservative with code-heavy text
        if fix_whitespace:
            cleaned, changed = clean_extra_whitespace(cleaned)
            if changed:
                changes_made. append("Fixed whitespace")
        
        return TextCleaningResult(
            original_text=text,
            cleaned_text=cleaned,
            changes_made=changes_made,
            stats={
                "total_changes": len(changes_made),
                "is_code":  True
            }
        )
    
    # Apply cleaning operations
    if fix_whitespace:
        cleaned, changed = clean_extra_whitespace(cleaned)
        if changed:
            changes_made.append("Fixed extra whitespace")
    
    if remove_special_chars:
        cleaned, changed = remove_special_characters(cleaned, preserve_code)
        if changed:
            changes_made.append("Removed special characters")
    
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
    
    if capitalize:
        cleaned, changed = capitalize_sentences(cleaned)
        if changed:
            changes_made.append("Capitalized sentences")
    
    # Calculate stats
    stats = {
        "total_changes": len(changes_made),
        "original_length": len(text),
        "cleaned_length": len(cleaned),
        "characters_removed": len(text) - len(cleaned),
        "is_code": False
    }
    
    return TextCleaningResult(
        original_text=text,
        cleaned_text=cleaned,
        changes_made=changes_made,
        stats=stats
    )