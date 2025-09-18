"""
Prompt templates and generation for OpenAI interactions
"""

def get_news_summary_prompt(text: str, max_length: int = 150) -> str:
    """Generate a prompt for news summarization"""
    return f"""You are a helpful assistant that summarizes news articles concisely and accurately.

Please summarize the following news article in {max_length} characters or less. 
Focus on the most important facts and main points.

Article text:
{text}

Summary:"""

def get_news_categorization_prompt(title: str, description: str) -> str:
    """Generate a prompt for news categorization"""
    return f"""You are a news categorization assistant. 
    
Please categorize the following news article into one of these categories:
- Politics
- Economy
- Technology
- Sports
- Entertainment
- Health
- Science
- World News
- Other

News title: {title}
News description: {description}

Category:"""

def get_keyword_extraction_prompt(text: str) -> str:
    """Generate a prompt for keyword extraction"""
    return f"""Extract the most important keywords from the following news article. 
Return 3-5 keywords separated by commas.

Article:
{text}

Keywords:"""

def get_translation_prompt(text: str, target_language: str) -> str:
    """Generate a prompt for text translation"""
    return f"""Translate the following text to {target_language}. 
Maintain the original meaning and tone.

Text to translate:
{text}

Translation:"""