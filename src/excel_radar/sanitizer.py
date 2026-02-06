"""HTML sanitization and text cleaning utilities."""

import html
import re
from typing import Optional

import bleach

# Allowed HTML tags for descriptions
ALLOWED_TAGS = [
    "p",
    "a",
    "strong",
    "em",
    "ul",
    "ol",
    "li",
    "code",
    "pre",
    "br",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
]

# Allowed attributes for tags
ALLOWED_ATTRIBUTES = {
    "a": ["href", "title"],
}


def clean_text(text: str) -> str:
    """
    Clean and normalize text.
    
    - Trim whitespace
    - Convert smart quotes to regular quotes
    - Collapse multiple spaces
    - Remove zero-width characters
    
    Args:
        text: Input text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Trim whitespace
    text = text.strip()
    
    # Convert smart quotes
    text = text.replace(""", '"').replace(""", '"')
    text = text.replace("'", "'").replace("'", "'")
    text = text.replace("–", "-").replace("—", "-")
    
    # Remove zero-width characters
    text = text.replace("\u200b", "").replace("\ufeff", "")
    
    # Collapse multiple spaces
    text = re.sub(r"\s+", " ", text)
    
    return text.strip()


def is_html_escaped(text: str) -> bool:
    """
    Check if text contains HTML-escaped entities.
    
    Args:
        text: Text to check
        
    Returns:
        True if text appears to be HTML-escaped
    """
    return bool(re.search(r"&[a-z]+;|&#\d+;", text, re.IGNORECASE))


def sanitize_html(html_content: str) -> str:
    """
    Sanitize HTML content using bleach.
    
    - Unescape HTML entities if needed
    - Remove dangerous tags and attributes
    - Add rel="noopener noreferrer" to links
    - Clean and normalize text
    
    Args:
        html_content: HTML content to sanitize
        
    Returns:
        Sanitized HTML
    """
    if not html_content:
        return ""
    
    # Clean text first
    content = clean_text(html_content)
    
    # Check if content is HTML-escaped and unescape if needed
    if is_html_escaped(content):
        content = html.unescape(content)
    
    # Sanitize with bleach
    sanitized = bleach.clean(
        content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True,
    )
    
    # Add security attributes to links
    sanitized = add_link_security(sanitized)
    
    return sanitized


def add_link_security(html_content: str) -> str:
    """
    Add rel="noopener noreferrer" and target="_blank" to all links.
    
    Args:
        html_content: HTML content with links
        
    Returns:
        HTML with secured links
    """
    # Replace <a href="..."> with <a href="..." target="_blank" rel="noopener noreferrer">
    pattern = r'<a\s+href="([^"]+)"([^>]*)>'
    
    def replace_link(match: re.Match[str]) -> str:
        href = match.group(1)
        rest = match.group(2)
        
        # Check if target and rel already exist
        has_target = "target=" in rest
        has_rel = "rel=" in rest
        
        if not has_target:
            rest += ' target="_blank"'
        if not has_rel:
            rest += ' rel="noopener noreferrer"'
        
        return f'<a href="{href}"{rest}>'
    
    return re.sub(pattern, replace_link, html_content)


def sanitize_description(description: Optional[str]) -> str:
    """
    Sanitize a description field from Excel.
    
    This is the main entry point for cleaning description fields.
    
    Args:
        description: Raw description from Excel
        
    Returns:
        Sanitized HTML description
    """
    if not description:
        return ""
    
    return sanitize_html(str(description))

# Made with Bob
