"""
Utility functions for code detector.
"""

def batch_process(texts, max_batch_size=100):
    """
    Process a batch of texts and determine which ones are code.
    
    Args:
        texts (list): List of text strings to analyze
        max_batch_size (int, optional): Maximum batch size. Defaults to 100.
        
    Returns:
        list: List of booleans indicating whether each text is code
    """
    from .detector import is_code
    
    results = []
    for i in range(0, len(texts), max_batch_size):
        batch = texts[i:i + max_batch_size]
        batch_results = [is_code(text) for text in batch]
        results.extend(batch_results)
    
    return results

def get_statistics(texts):
    """
    Get statistics about code detection in a corpus of texts.
    
    Args:
        texts (list): List of text strings to analyze
        
    Returns:
        dict: Statistics about code detection
    """
    from .detector import is_code
    
    results = [is_code(text) for text in texts]
    code_count = sum(results)
    non_code_count = len(results) - code_count
    
    return {
        'total': len(results),
        'code_count': code_count,
        'non_code_count': non_code_count,
        'code_percentage': (code_count / len(results)) * 100 if results else 0
    }