"""
Post-processing utilities for AI-generated content
"""
import re
import html
from typing import List, Dict

def clean_summary_text(text: str) -> str:
    """Clean and format summary text"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove HTML entities
    text = html.unescape(text)
    
    # Remove markdown formatting that might interfere with Telegram
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Remove bold
    text = re.sub(r'\*(.*?)\*', r'\1', text)      # Remove italic
    
    # Ensure proper sentence ending
    if text and not text.endswith(('.', '!', '?')):
        text += '.'
    
    return text

def format_for_telegram(text: str, max_length: int = 4096) -> str:
    """Format text for Telegram message (respecting length limits)"""
    text = clean_summary_text(text)
    
    if len(text) <= max_length:
        return text
    
    # Truncate at sentence boundary if possible
    truncated = text[:max_length-3]
    last_sentence_end = max(
        truncated.rfind('.'),
        truncated.rfind('!'),
        truncated.rfind('?')
    )
    
    if last_sentence_end > max_length * 0.7:  # If we can keep at least 70% and end at sentence
        return text[:last_sentence_end + 1]
    else:
        return truncated + "..."

def extract_keywords_from_summary(text: str) -> List[str]:
    """Extract potential keywords from summary text"""
    if not text:
        return []
    
    # Simple keyword extraction - can be enhanced with NLP
    words = re.findall(r'\b[A-Za-zА-Яа-я]{3,}\b', text)
    
    # Filter out common words (basic stopwords)
    stopwords = {
        'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        'это', 'что', 'как', 'для', 'или', 'они', 'его', 'её', 'их', 'она', 'оно'
    }
    
    keywords = [word.lower() for word in words if word.lower() not in stopwords]
    
    # Return unique keywords, limited to reasonable number
    return list(dict.fromkeys(keywords))[:10]

def validate_summary_quality(original_text: str, summary: str) -> bool:
    """Basic validation of summary quality"""
    if not summary or not original_text:
        return False
    
    # Check if summary is not just truncated original
    if summary == original_text[:len(summary)]:
        return False
    
    # Check minimum length
    if len(summary) < 20:
        return False
    
    # Check if summary is not too long compared to original
    if len(summary) > len(original_text) * 0.8:
        return False
    
    return True

def format_news_item_for_display(news_item: Dict) -> str:
    """Format a news item for display in Telegram"""
    title = news_item.get('title', 'No title')
    description = news_item.get('description', '')
    summary = news_item.get('summary', '')
    url = news_item.get('url', '')
    category = news_item.get('category', 'Без категории')
    published_at = news_item.get('published_at', '')
    
    # Use summary if available, otherwise description
    content = summary if summary else description
    content = format_for_telegram(content, 500)  # Limit content length
    
    msg = f"<b>{html.escape(title)}</b>\n"
    if content:
        msg += f"{html.escape(content)}\n"
    if url:
        msg += f"<a href=\"{url}\">Читать подробнее</a>\n"
    msg += f"Категория: {html.escape(category)}\n"
    if published_at:
        msg += f"Дата: {html.escape(str(published_at))}\n"
    
    return msg