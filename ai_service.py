import os
import logging
from openai import OpenAI
from typing import Optional

# Initialize OpenAI client with timeout configuration
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(
    api_key=OPENAI_API_KEY,
    timeout=10.0  # 10 second timeout to prevent hanging
) if OPENAI_API_KEY else None

def generate_proposal_summary(title: str, description: str) -> str:
    """
    Generate a plain-English summary of a DAO proposal using OpenAI
    
    Args:
        title: The proposal title
        description: The proposal description/body
        
    Returns:
        A 2-3 sentence summary in plain English
    """
    
    if not openai_client:
        logging.warning("OpenAI API key not configured, returning fallback summary")
        return "AI summary unavailable - OpenAI API key not configured. Please check the original proposal for details."
    
    try:
        # Prepare a concise prompt
        prompt = f"""Summarize this DAO proposal in 2-3 simple sentences:

Title: {title}

Description: {description[:800]}

Make it easy to understand for non-technical users."""
        
        # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
        # do not change this unless explicitly requested by the user
        response = openai_client.chat.completions.create(
            model="gpt-5",
            messages=[
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            max_completion_tokens=100
        )
        
        summary = response.choices[0].message.content.strip() if response.choices[0].message.content else "Summary not available"
        logging.info(f"Generated AI summary for proposal: {title[:30]}...")
        
        return summary
        
    except Exception as e:
        logging.warning(f"AI summary failed, using fallback: {str(e)[:100]}")
        # Return a simple fallback summary based on the title and first part of description
        if description and len(description) > 50:
            return f"This proposal '{title}' involves: {description[:150]}..."
        else:
            return f"Governance proposal: {title}. Please check the full proposal details for more information."

def test_openai_connection() -> bool:
    """Test if OpenAI API is properly configured and accessible"""
    if not openai_client:
        return False
    
    try:
        # Simple test call
        response = openai_client.chat.completions.create(
            model="gpt-5",
            messages=[{"role": "user", "content": "Hello"}],
            max_completion_tokens=5
        )
        return True
    except Exception as e:
        logging.error(f"OpenAI connection test failed: {e}")
        return False
