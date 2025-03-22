import re
import json
from typing import List, Dict, Any, Optional, Tuple

def preprocess_prompt(prompt: str) -> str:
    """
    Preprocess a prompt for generation.
    
    Args:
        prompt: The text prompt to preprocess
        
    Returns:
        Preprocessed prompt
    """
    # Remove excessive whitespace
    prompt = re.sub(r'\s+', ' ', prompt.strip())
    return prompt

def extract_entities(text: str) -> List[Dict[str, Any]]:
    """
    Simple entity extraction using regex.
    This is a basic implementation for demonstration purposes.
    In production, use NER models from spaCy, NLTK, or similar libraries.
    
    Args:
        text: Text to extract entities from
        
    Returns:
        List of extracted entities with type and value
    """
    entities = []
    
    # Extract emails
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    for email in emails:
        entities.append({
            "type": "EMAIL",
            "value": email,
            "start": text.find(email),
            "end": text.find(email) + len(email)
        })
    
    # Extract URLs
    urls = re.findall(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/\w\.-]*(?:\?\S+)?', text)
    for url in urls:
        entities.append({
            "type": "URL",
            "value": url,
            "start": text.find(url),
            "end": text.find(url) + len(url)
        })
    
    # Extract dates (simple format)
    dates = re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', text)
    for date in dates:
        entities.append({
            "type": "DATE",
            "value": date,
            "start": text.find(date),
            "end": text.find(date) + len(date)
        })
    
    return entities

def analyze_sentiment(text: str) -> Dict[str, Any]:
    """
    Simple rule-based sentiment analysis.
    This is a basic implementation for demonstration purposes.
    In production, use proper sentiment analysis models.
    
    Args:
        text: Text to analyze sentiment
        
    Returns:
        Dictionary with sentiment scores
    """
    text = text.lower()
    
    # Simple positive and negative word lists
    positive_words = [
        "good", "great", "excellent", "amazing", "wonderful", "fantastic",
        "happy", "love", "best", "awesome", "positive", "joy", "brilliant"
    ]
    
    negative_words = [
        "bad", "awful", "terrible", "horrible", "worst", "sad", "hate",
        "negative", "poor", "disappointing", "disaster", "failure", "wrong"
    ]
    
    # Count occurrences
    positive_count = sum(1 for word in positive_words if word in text.split())
    negative_count = sum(1 for word in negative_words if word in text.split())
    
    # Calculate sentiment score (-1 to 1)
    total = positive_count + negative_count
    if total == 0:
        score = 0
    else:
        score = (positive_count - negative_count) / total
    
    # Determine sentiment label
    if score > 0.25:
        label = "positive"
    elif score < -0.25:
        label = "negative"
    else:
        label = "neutral"
    
    return {
        "score": score,
        "label": label,
        "positive_count": positive_count,
        "negative_count": negative_count
    }

def truncate_text(text: str, max_length: int, add_ellipsis: bool = True) -> str:
    """
    Truncate text to a maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        add_ellipsis: Whether to add ellipsis at the end
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    truncated = text[:max_length]
    
    if add_ellipsis:
        truncated = truncated.rstrip() + "..."
    
    return truncated

def format_as_json(data: Any, pretty: bool = False) -> str:
    """
    Format data as JSON string.
    
    Args:
        data: Data to format
        pretty: Whether to pretty-print the JSON
        
    Returns:
        JSON string
    """
    if pretty:
        return json.dumps(data, indent=2, ensure_ascii=False)
    return json.dumps(data, ensure_ascii=False)

def parse_json_safely(text: str) -> Tuple[Optional[Any], Optional[str]]:
    """
    Parse JSON string safely.
    
    Args:
        text: JSON string to parse
        
    Returns:
        Tuple of (parsed data, error message)
    """
    try:
        return json.loads(text), None
    except json.JSONDecodeError as e:
        return None, str(e) 