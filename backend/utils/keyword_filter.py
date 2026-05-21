import re

def quick_filter(query: str, text: str) -> bool:
    """
    Lightweight keyword overlap gate to check if the retrieved abstract
    is loosely related to the research query.
    Extracts terms and ensures at least one key term (excluding common stop words) matches.
    """
    if not text or not query:
        return False
        
    # Standard English stop words
    stops = {
        "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "arent", "as", "at", 
        "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can", "cant", "cannot", 
        "could", "did", "do", "does", "doing", "don", "down", "during", "each", "few", "for", "from", "further", "had", 
        "has", "have", "having", "he", "her", "here", "hers", "herself", "him", "himself", "his", "how", "i", "if", "in", 
        "into", "is", "it", "its", "itself", "me", "more", "most", "my", "myself", "no", "nor", "not", "of", "off", "on", 
        "once", "only", "or", "other", "our", "ours", "ourselves", "out", "over", "own", "same", "she", "should", "so", 
        "some", "such", "than", "that", "the", "their", "theirs", "them", "themselves", "then", "there", "these", "they", 
        "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "we", "were", "what", "when", 
        "where", "which", "while", "who", "whom", "why", "with", "would", "you", "your", "yours", "yourself", "yourselves"
    }
    
    # Tokenize and lowercase
    query_words = set(re.findall(r'\b\w{3,}\b', query.lower())) - stops
    text_words = set(re.findall(r'\b\w{3,}\b', text.lower()))
    
    if not query_words:
        # If the query only had stopwords, allow everything at this gate
        return True
        
    # Check for intersection of stems or full words
    overlap = query_words.intersection(text_words)
    return len(overlap) > 0
