"""
Natural Language Processing & Normalization Utility.
Implements text cleaning, normalization, contraction expansion,
tokenization, keyword matching, and regex entity extraction.
"""

import re
import string
from typing import List, Dict, Any, Tuple, Optional

# Contraction mapping for text normalization
CONTRACTIONS = {
    "i'm": "i am",
    "i've": "i have",
    "i'll": "i will",
    "i'd": "i would",
    "you're": "you are",
    "you've": "you have",
    "you'll": "you will",
    "he's": "he is",
    "she's": "she is",
    "it's": "it is",
    "we're": "we are",
    "they're": "they are",
    "can't": "cannot",
    "won't": "will not",
    "don't": "do not",
    "doesn't": "does not",
    "didn't": "did not",
    "hasn't": "has not",
    "haven't": "have not",
    "hadn't": "had not",
    "isn't": "is not",
    "aren't": "are not",
    "wasn't": "was not",
    "weren't": "were not",
    "what's": "what is",
    "how's": "how is",
    "where's": "where is",
    "who's": "who is",
    "that's": "that is",
    "there's": "there is",
    "let's": "let us",
}


class NLPNormalizer:
    """Handles text normalization, tokenization, entity extraction, and fuzzy matching."""

    @staticmethod
    def expand_contractions(text: str) -> str:
        """Expands common English contractions in the text."""
        lower_text = text.lower()
        for contraction, expanded in CONTRACTIONS.items():
            pattern = re.compile(r'\b' + re.escape(contraction) + r'\b', re.IGNORECASE)
            text = pattern.sub(expanded, text)
        return text

    @classmethod
    def clean_text(cls, text: str, preserve_punctuation: bool = False) -> str:
        """
        Normalizes raw text:
        1. Strips leading/trailing whitespaces.
        2. Converts to lowercase.
        3. Expands contractions.
        4. Removes non-alphanumeric punctuation.
        5. Normalizes internal whitespace.
        """
        if not text:
            return ""

        # Step 1: Expand contractions
        cleaned = cls.expand_contractions(text)

        # Step 2: Convert to lowercase
        cleaned = cleaned.lower()

        # Step 3: Remove unwanted special characters if preserve_punctuation is False
        if not preserve_punctuation:
            # Replace punctuation with spaces
            cleaned = re.sub(r'[^a-z0-9\s#\$\-]', ' ', cleaned)

        # Step 4: Normalize multiple spaces to a single space
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()

        return cleaned

    @classmethod
    def tokenize(cls, text: str) -> List[str]:
        """Tokenizes cleaned text into a list of word tokens."""
        cleaned = cls.clean_text(text)
        if not cleaned:
            return []
        return cleaned.split()

    @staticmethod
    def extract_entities(raw_text: str) -> Dict[str, Any]:
        """
        Extracts structured entities using regular expressions:
        - Order IDs (e.g., #ORD-1234, ORD12345)
        - Email addresses
        - Phone numbers
        - Monetary amounts ($50, 50 USD, 50 dollars)
        - Numbers / Quantities
        """
        entities: Dict[str, Any] = {
            "order_id": None,
            "email": None,
            "phone": None,
            "amount": None,
            "number": None
        }

        # Order ID pattern (e.g., #ORD-9821 or ORD-1234 or #12345)
        order_match = re.search(r'#?ORD-?[a-z0-9]{3,10}\b|#\d{4,8}\b', raw_text, re.I)
        if order_match:
            entities["order_id"] = order_match.group(0).upper().strip()

        # Email pattern
        email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', raw_text)
        if email_match:
            entities["email"] = email_match.group(0).lower()

        # Phone pattern
        phone_match = re.search(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', raw_text)
        if phone_match:
            entities["phone"] = phone_match.group(0).strip()

        # Monetary amount pattern
        amount_match = re.search(r'(?:\$|\bUSD\s*|\beur\s*|\bgbp\s*)?(\d+(?:\.\d{1,2})?)\s*(?:dollars?|usd|\$|euros?|€)?\b', raw_text, re.I)
        if amount_match and amount_match.group(1):
            try:
                entities["amount"] = float(amount_match.group(1))
            except ValueError:
                pass

        # Standalone numbers (e.g. menu option 1, 2, 3)
        num_match = re.search(r'\b(\d+)\b', raw_text)
        if num_match:
            entities["number"] = int(num_match.group(1))

        return entities

    @staticmethod
    def compute_jaccard_similarity(set1: set, set2: set) -> float:
        """Computes Jaccard word token overlap similarity."""
        if not set1 or not set2:
            return 0.0
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / float(union) if union > 0 else 0.0

    @classmethod
    def match_intent_keywords(cls, text: str, keyword_map: Dict[str, List[str]]) -> Tuple[Optional[str], float]:
        """
        Matches cleaned text against a dictionary of intent keyword lists using whole word boundaries.
        Returns the best matching intent name and confidence score (0.0 to 1.0).
        """
        cleaned = cls.clean_text(text)
        tokens = set(cls.tokenize(cleaned))
        
        if not tokens:
            return None, 0.0

        best_intent = None
        best_score = 0.0

        for intent, keywords in keyword_map.items():
            matches = 0
            for kw in keywords:
                kw_clean = cls.clean_text(kw)
                # Word boundary match pattern
                pattern = r'\b' + re.escape(kw_clean) + r'\b'
                if re.search(pattern, cleaned):
                    # Multi-word phrase match gives higher weight
                    matches += 3.0 if " " in kw_clean else 1.5
                else:
                    kw_tokens = set(kw_clean.split())
                    overlap = len(tokens.intersection(kw_tokens))
                    if overlap > 0:
                        matches += overlap / max(len(kw_tokens), 1)

            if matches > 0:
                score = min(round(matches / (len(keywords) * 0.4 + 1.0), 2), 1.0)
                if score > best_score:
                    best_score = score
                    best_intent = intent

        return best_intent, best_score
