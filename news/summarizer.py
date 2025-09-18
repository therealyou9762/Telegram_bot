"""
OpenAI summarization functionality
"""
import os
import openai
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def create_summary(text: str, max_length: int = 150) -> str:
    """Create a summary of the given text using OpenAI"""
    if not OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY not set, returning truncated text")
        return text[:max_length] + "..." if len(text) > max_length else text
    
    # TODO: Implement OpenAI summarization
    # This is a placeholder for future implementation
    try:
        # client = openai.OpenAI(api_key=OPENAI_API_KEY)
        # response = client.chat.completions.create(
        #     model="gpt-3.5-turbo",
        #     messages=[
        #         {"role": "system", "content": "You are a helpful assistant that summarizes news articles."},
        #         {"role": "user", "content": f"Summarize this text in {max_length} characters or less: {text}"}
        #     ],
        #     max_tokens=max_length
        # )
        # return response.choices[0].message.content
        return text[:max_length] + "..." if len(text) > max_length else text
    except Exception as e:
        logger.error(f"Error creating summary: {e}")
        return text[:max_length] + "..." if len(text) > max_length else text

def summarize_news_batch(news_items: List[Dict]) -> List[Dict]:
    """Summarize a batch of news items"""
    summarized_items = []
    for item in news_items:
        summarized_item = item.copy()
        if 'description' in item and item['description']:
            summarized_item['summary'] = create_summary(item['description'])
        summarized_items.append(summarized_item)
    return summarized_items