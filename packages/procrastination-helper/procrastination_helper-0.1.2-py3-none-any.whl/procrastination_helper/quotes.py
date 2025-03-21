"""
This module provides a function to retrieve random motivational quotes about procrastination.
Source of quotes: https://www.goodreads.com/quotes/tag/procrastination
"""

import random
from procrastination_helper.data.quotesData import quotes as quotes_collection

def get(num_quotes=1):
    """
    Returns random motivational quotes about procrastination. 
    Accepts number of quotes to return, or defaults to 1 if no argument.
    
    Parameters:
        num_quotes (int): Number of quotes to return (default: 1)
        
    Returns:
        str: A string containing the requested number of quotes
    """
    num_quotes = min(num_quotes, len(quotes_collection))
    
    if num_quotes < len(quotes_collection):
        ret_quotes = random.sample(quotes_collection, num_quotes)
    else:
        ret_quotes = quotes_collection.copy()
        random.shuffle(ret_quotes)
    
    formatted_quotes = [f"{q['text']} - {q['author']}" for q in ret_quotes]
    
    if num_quotes == 1:
        return formatted_quotes[0]
    else:
        return "\n".join(formatted_quotes)

quotes = quotes_collection
