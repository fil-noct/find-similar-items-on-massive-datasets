import re

def normalize_whitespace(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()

def keep_letters_lowercase(text: str) -> str:
    cleaned = re.sub(r'[^a-zA-Z]+', ' ', text)    
    return cleaned.lower().strip()
