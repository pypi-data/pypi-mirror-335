"""
SaraikiNLP - preprocessing
by Muhammad Muzamil (MMuzamilAI)
"""

import re
import string
import unicodedata
from typing import Dict

def remove_links(text: str) -> str:
    """Remove web links (http, https, www) from the text."""
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    return remove_multiple_spaces(re.sub(r'http\S+|www\.\S+', ' ', text))

def remove_hashtags(text: str) -> str:
    """Remove hashtags from the text."""
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    return remove_multiple_spaces(re.sub(r'#\w+', ' ', text))

def remove_usernames(text: str) -> str:
    """Remove usernames (e.g., @username) from the text."""
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    return remove_multiple_spaces(re.sub(r'@\w+', ' ', text))

def remove_phone_numbers(text: str) -> str:
    """Remove phone numbers (international and local formats) from the text."""
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    return remove_multiple_spaces(re.sub(r'\+?\d[\d\s\-]{8,}\d', ' ', text))

def remove_numbers(text: str) -> str:
    """Remove all digits from the text."""
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    return remove_multiple_spaces(re.sub(r'\d+', ' ', text))

def remove_punctuation(text: str) -> str:
    """
    Remove punctuation from the text, replacing it with spaces.
    Keeps dots if they are part of a complete decimal.
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string")

    chars = list(text)
    result_chars = []
    length = len(chars)
    for i, ch in enumerate(chars):
        if ch == '.':
            if i > 0 and i < length - 1 and chars[i - 1].isdigit() and chars[i + 1].isdigit():
                result_chars.append(ch)
            else:
                result_chars.append(' ')
        elif unicodedata.category(ch).startswith('P'):
            result_chars.append(' ')
        else:
            result_chars.append(ch)
    return remove_multiple_spaces(''.join(result_chars))

def remove_whitespace(text: str) -> str:
    """Collapse multiple whitespace characters into a single space and trim."""
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    return re.sub(r'\s+', ' ', text).strip()

def remove_multiple_spaces(text: str) -> str:
    """Replace multiple consecutive spaces with a single space."""
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    return re.sub(r' {2,}', ' ', text)

def remove_linebreaks(text: str) -> str:
    """Replace line breaks with a space and normalize whitespace."""
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    text = text.replace('\n', ' ')
    return remove_whitespace(text)

def separate_numbers_from_text(text: str) -> str:
    """
    Insert spaces between numbers and letters while preserving complete decimals.

    Examples:
        "11لاکھ" becomes "11 لاکھ"
        "اج10بندے" becomes "اج 10 بندے"
        "110810.22پوائنٹس" becomes "110810.22 پوائنٹس"
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    text = re.sub(r'(?<=\d)(?=[^\d\s\.])', ' ', text)
    text = re.sub(r'(?<=[^\d\s\.])(?=\d)', ' ', text)
    return text

def remove_emojis(text: str) -> str:
    """
    Remove emojis and other non-textual symbols from the text.

    This regex pattern covers many common emoji ranges.
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

def to_lowercase(text: str) -> str:
    """Convert text to lowercase."""
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    return text.lower()

def remove_english(text: str) -> str:
    """
    Remove English alphabets, digits, and punctuation (ASCII range) from the text.

    This function removes:
      - English letters (A-Za-z)
      - English digits (0-9)
      - ASCII punctuation defined in string.punctuation

    Whitespace is preserved.
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    # Build a regex character class that includes English letters, digits, and punctuation.
    pattern = r'[A-Za-z0-9' + re.escape(string.punctuation) + r']+'
    return re.sub(pattern, '', text)

def preprocess_text(text: str) -> str:
    """
    Apply a full preprocessing pipeline to the text.
    Pipeline steps include:
      - Removing links, hashtags, usernames, and phone numbers.
      - Removing punctuation and emojis.
      - Collapsing extra spaces and line breaks.
      - Converting text to lowercase.

    Note: You can uncomment additional functions like remove_numbers() if needed.
    """

    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    text = remove_links(text)
    text = remove_hashtags(text)
    text = remove_usernames(text)
    text = remove_phone_numbers(text)
    text = separate_numbers_from_text(text)
    # text = remove_numbers(text)  # Uncomment if digit removal is desired.
    text = remove_punctuation(text)
    text = remove_emojis(text)
    text = remove_whitespace(text)
    text = to_lowercase(text)
    return text

def retain_clean_saraiki(text: str) -> str:
    """
    Retains only allowed Urdu, Arabic, and Saraiki characters, digits, punctuation, and whitespace.
    Removes all other symbols and non-allowed characters.
    
    Allowed character ranges:
      - Basic Arabic block (\u0600-\u06FF), which includes Urdu punctuation (e.g. '،', '؛', '؟')
      - Arabic Supplement (\u0750-\u077F)
      - Combining diacritical marks (\u0300-\u036F)
      - Whitespace (\s)
      - Western digits (0-9) and Arabic-Indic digits (\u06F0-\u06F9)
      - Additional Saraiki characters: ݨ, ݙ, ڳ, ڄ, ٻ
      - English punctuation: all characters defined in string.punctuation
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    
    # Build the allowed character set:
    allowed_chars = (
        r"\u0600-\u06FF"       # Basic Arabic block (includes Urdu punctuation)
        r"\u0750-\u077F"       # Arabic Supplement
        r"\u0300-\u036F"       # Combining diacritical marks
        r"\s"                  # Whitespace
        r"0-9"                 # Western digits
        r"\u06F0-\u06F9"       # Arabic-Indic digits
        r"ݨݙڳڄٻ"              # Additional Saraiki characters
    )
    
    # Pattern to match characters that are NOT allowed
    pattern = rf"[^{allowed_chars}]"
    
    # Normalize text, remove unwanted characters, and clean up extra spaces
    cleaned_text = re.sub(pattern, " ", normalize_text(text))
    cleaned_text = remove_multiple_spaces(cleaned_text)
    return separate_numbers_from_text(cleaned_text)
