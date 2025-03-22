"""
SaraikiNLP - normalization
by Muhammad Muzamil (MMuzamilAI)
"""

import re
import unicodedata
from typing import Dict, List

# Mapping of character variants to Saraiki standard forms.
_SARAIKI_CHARACTERS_MAPPING: Dict[str, List[str]] = {
    'آ': ['ﺁ', 'ﺂ'],
    'أ': ['ﺃ'],
    'ا': ['ﺍ', 'ﺎ', 'ٱ'],
    'ب': ['ﺏ', 'ﺐ', 'ﺑ', 'ﺒ'],
    'ٻ': [],
    'پ': ['ﭖ', 'ﭘ', 'ﭙ'],
    'ت': ['ﺕ', 'ﺖ', 'ﺗ', 'ﺘ'],
    'ٹ': ['ﭦ', 'ﭧ', 'ﭨ', 'ﭩ'],
    'ث': ['ﺛ', 'ﺜ', 'ﺚ'],
    'ج': ['ﺝ', 'ﺞ', 'ﺟ', 'ﺠ'],
    'ڄ': [],
    'ح': ['ﺡ', 'ﺣ', 'ﺤ', 'ﺢ'],
    'خ': ['ﺧ', 'ﺨ', 'ﺦ'],
    'د': ['ﺩ', 'ﺪ'],
    'ذ': ['ﺬ', 'ﺫ'],
    'ر': ['ﺭ', 'ﺮ'],
    'ز': ['ﺯ', 'ﺰ'],
    'س': ['ﺱ', 'ﺲ', 'ﺳ', 'ﺴ'],
    'ش': ['ﺵ', 'ﺶ', 'ﺷ', 'ﺸ'],
    'ص': ['ﺹ', 'ﺺ', 'ﺻ', 'ﺼ'],
    'ض': ['ﺽ', 'ﺾ', 'ﺿ', 'ﻀ'],
    'ط': ['ﻃ', 'ﻄ'],
    'ظ': ['ﻅ', 'ﻇ', 'ﻈ'],
    'ع': ['ﻉ', 'ﻊ', 'ﻋ', 'ﻌ'],
    'غ': ['ﻍ', 'ﻏ', 'ﻐ'],
    'ف': ['ﻑ', 'ﻒ', 'ﻓ', 'ﻔ'],
    'ق': ['ﻕ', 'ﻖ', 'ﻗ', 'ﻘ'],
    'ل': ['ﻝ', 'ﻞ', 'ﻟ', 'ﻠ'],
    'م': ['ﻡ', 'ﻢ', 'ﻣ', 'ﻤ'],
    'ن': ['ﻥ', 'ﻦ', 'ﻧ', 'ﻨ'],
    'ݨ': [],
    'چ': ['ﭺ', 'ﭻ', 'ﭼ', 'ﭽ'],
    'ڈ': ['ﮈ', 'ﮉ'],
    'ݙ': [],
    'ڑ': ['ﮍ', 'ﮌ'],
    'ژ': ['ﮋ'],
    'ک': ['ﮎ', 'ﮏ', 'ﮐ', 'ﮑ', 'ﻛ', 'ك'],
    'گ': ['ﮒ', 'ﮓ', 'ﮔ', 'ﮕ'],
    'ڳ': [],
    'ں': ['ﮞ', 'ﮟ'],
    'و': ['ﻮ', 'ﻭ', 'ﻮ'],
    'ؤ': ['ﺅ'],
    'ھ': ['ﮪ', 'ﮬ', 'ﮭ', 'ﻬ', 'ﻫ', 'ﮫ'],
    'ہ': ['ﻩ', 'ﮦ', 'ﻪ', 'ﮧ', 'ﮩ', 'ﮨ', 'ه'],
    'ۃ': ['ة'],
    'ء': ['ﺀ'],
    'ی': ['ﯼ', 'ى', 'ﯽ', 'ﻰ', 'ﻱ', 'ﻲ', 'ﯾ', 'ﯿ', 'ي'],
    'ئ': ['ﺋ', 'ﺌ', 'یٔ'],
    'ے': ['ﮮ', 'ﮯ', 'ﻳ', 'ﻴ'],
    'لا': ['ﻻ', 'ﻼ'],
    'ۂ': [],
    'ۓ': [],
}

# Mapping for converting Saraiki/Arabic numeral variants to Western numerals.
_TO_WESTERN_NUMBERS: Dict[str, str] = {
    '٠': '0', '۰': '0',
    '١': '1', '۱': '1',
    '٢': '2', '۲': '2',
    '٣': '3', '۳': '3',
    '٤': '4', '۴': '4',
    '٥': '5', '۵': '5',
    '٦': '6', '۶': '6',
    '٧': '7', '۷': '7',
    '٨': '8', '۸': '8',
    '٩': '9', '۹': '9'
}

_TO_SARAIKI_NUMBERS: Dict[str, str] = {
    '0': '٠', '٠': '٠', '۰': '٠',
    '1': '١', '١': '١', '۱': '١',
    '2': '٢', '٢': '٢', '۲': '٢',
    '3': '٣', '٣': '٣', '۳': '٣',
    '4': '٤', '٤': '٤', '۴': '٤',
    '5': '٥', '٥': '٥', '۵': '٥',
    '6': '٦', '٦': '٦', '۶': '٦',
    '7': '٧', '٧': '٧', '۷': '٧',
    '8': '٨', '٨': '٨', '۸': '٨',
    '9': '٩', '٩': '٩', '۹': '٩'
}


def normalize_characters(text: str) -> str:
    """
    Replace variant Saraiki characters with their standard forms.

    Parameters:
        text (str): The input text.

    Returns:
        str: The text with all variant characters replaced.
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string")

    for standard_char, variants in _SARAIKI_CHARACTERS_MAPPING.items():
        for variant in variants:
            if variant:
                text = text.replace(variant, standard_char)
    return text


def normalize_numbers(text: str, convert_native: bool = True) -> str:
    """
    Convert numeral representations in the text to either Western or Saraiki numerals.

    Parameters:
        text (str): The input text.
        convert_native (bool): If True, converts native numeral variants to Western numerals.
                               If False, converts to Saraiki numeral forms.

    Returns:
        str: The text with numerals normalized.
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string")

    mapping = _TO_WESTERN_NUMBERS if convert_native else _TO_SARAIKI_NUMBERS
    for wrong_num, correct_num in mapping.items():
        text = text.replace(wrong_num, correct_num)
    return text


def remove_diacritics(text: str, allowed_diacritics: set = None) -> str:
    """
    Remove diacritics (combining marks) from the text while preserving specified allowed diacritics.

    Parameters:
        text (str): The input text.
        allowed_diacritics (set, optional): A set of allowed combining diacritical marks.
            Defaults to preserving only HAMZA ABOVE (U+0654) and HAMZA BELOW (U+0655).

    Returns:
        str: The text with non-essential diacritics removed.
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string")

    if allowed_diacritics is None:
        allowed_diacritics = {'\u0654', '\u0655'}  # Preserve only combining hamza marks.

    text = normalize_characters(text)
    normalized_text = unicodedata.normalize('NFD', text)
    return ''.join(ch for ch in normalized_text if not unicodedata.combining(ch) or ch in allowed_diacritics)


def normalize_punctuation(text: str, convert_native: bool = False) -> str:
    """
    Standardize punctuation in the text:
      1. Apply an explicit mapping for known punctuation variants.
      2. Normalize remaining punctuation using Unicode normalization.
      3. Optionally convert native Arabic/Urdu punctuation to Western equivalents.
      4. Insert spaces after punctuation if needed.

    Parameters:
        text (str): The input text.
        convert_native (bool): If True, convert native punctuation to Western equivalents.
                               If False, preserve native punctuation except for minor removals.

    Returns:
        str: The punctuation-normalized text.
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string")

    if convert_native:
        punctuation_mapping: Dict[str, str] = {
            '“': '"', '”': '"',
            '‘': "'", '’': "'",
            '–': '-', '—': '-',
            '…': '...',
            '،': ',',  # Arabic comma to Western comma.
            '۔': '.',  # Urdu full stop to period.
            '؟': '?',  # Arabic/Urdu question mark.
            '؛': ';',  # Arabic/Urdu semicolon.
            'ـ': '',   # Remove tatweel.
            '٪': '%', '؉': '%', '؊': '%',
        }
    else:
        punctuation_mapping = {
            '“': '"', '”': '"',
            '‘': "'", '’': "'",
            '–': '-', '—': '-',
            '…': '...',
            'ـ': '',   # Remove tatweel for consistency.
            '٪': '%', '؉': '%', '؊': '%',
        }

    for orig, repl in punctuation_mapping.items():
        text = text.replace(orig, repl)

    normalized_chars = [
        unicodedata.normalize('NFKC', ch) if unicodedata.category(ch).startswith("P") else ch
        for ch in text
    ]
    normalized_text = ''.join(normalized_chars)



    return normalized_text

def insert_space_after_punctuation(text: str) -> str:
    """
    Inserts a space after punctuation marks (if not already present) for both English and Urdu.
    Considered punctuation:
      - English: . , ? ! ; :
      - Urdu: ، ؛ ؟
    """
    # Pattern matches any of the specified punctuation characters followed immediately by a non-space character.
    if not isinstance(text, str):
      raise TypeError("Text must be of string type")

    pattern = r'([.,?!;:،؛؟۔])(?=\S)'
    return re.sub(pattern, r'\1 ', text)



def normalize_text(text: str, remove_diacritic: bool = False) -> str:
    """
    Normalize Saraiki text by performing character normalization, numeral conversion, punctuation standardization,
    and optionally removing diacritics.

    Parameters:
        text (str): The input Saraiki text.
        remove_diacritic (bool): If True, remove diacritics from the text.

    Returns:
        str: The fully normalized text.

    Raises:
        TypeError: If the input is not a string.
    """
    if not isinstance(text, str):
        raise TypeError("Text must be of string type")

    text = normalize_characters(text)
    text = normalize_numbers(text)
    text = normalize_punctuation(text)
    if remove_diacritic:
        text = remove_diacritics(text)

    return text
