import re

def compress_abstract(abstract: str) -> str:
    """
    Strips academic boilerplate from abstracts (e.g. copyright notices, funding warnings, 
    publisher signatures) to save context window tokens.
    """
    if not abstract:
        return ""
    # Strip common copyright boilerplate
    abstract = re.sub(r'©\s*\d{4}\s+.*$', '', abstract, flags=re.IGNORECASE)
    abstract = re.sub(r'copyright\s+.*$', '', abstract, flags=re.IGNORECASE)
    abstract = re.sub(r'all\s+rights\s+reserved\.?', '', abstract, flags=re.IGNORECASE)
    # Remove excessive double whitespace
    abstract = re.sub(r'\s+', ' ', abstract).strip()
    return abstract

def extract_claims(text: str) -> list[str]:
    """
    Splits review draft text into fine-grained claim sentences.
    Carefully ignores standard abbreviations such as 'e.g.', 'i.e.', 'et al.', and 'fig.'
    to avoid false splitting.
    """
    if not text:
        return []
    
    # Simple regex based sentence splitter with abbreviation protection
    # Replace period in abbreviations temporarily
    abbrevs = ["e.g.", "i.e.", "et al.", "vs.", "fig.", "dr.", "prof.", "mr.", "mrs.", "ms.", "al."]
    
    temp_text = text
    for abbrev in abbrevs:
        # e.g. "et al." -> "et_al_"
        protected = abbrev.replace(".", "_")
        temp_text = re.sub(r'\b' + re.escape(abbrev), protected, temp_text, flags=re.IGNORECASE)
        
    # Split by sentence ending punctuation followed by whitespace and uppercase letter
    splits = re.split(r'(?<=[.!?])\s+(?=[A-Z])', temp_text)
    
    claims = []
    for split in splits:
        # Revert abbreviations
        for abbrev in abbrevs:
            protected = abbrev.replace(".", "_")
            split = split.replace(protected, abbrev)
        
        cleaned = split.strip()
        # Filter out headers (lines starting with #) and extremely short texts
        if cleaned and not cleaned.startswith('#') and len(cleaned) > 15:
            claims.append(cleaned)
            
    return claims
