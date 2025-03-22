from typing import List, Dict
import re

def reverse_string(text: str) -> str:
    """Reverse a string using slicing."""
    return text[::-1]

def is_palindrome(text: str) -> bool:
    """Check if a string is a palindrome (case-insensitive)."""
    cleaned_text = ''.join(c.lower() for c in text if c.isalnum())
    return cleaned_text == cleaned_text[::-1]

def word_frequency(text: str) -> Dict[str, int]:
    """Count frequency of each word in a text."""
    words = re.findall(r'\w+', text.lower())
    frequency = {}
    for word in words:
        frequency[word] = frequency.get(word, 0) + 1
    return frequency

def camel_to_snake(text: str) -> str:
    """Convert camelCase to snake_case."""
    pattern = re.compile(r'(?<!^)(?=[A-Z])')
    return pattern.sub('_', text).lower()

def snake_to_camel(text: str) -> str:
    """Convert snake_case to camelCase."""
    components = text.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

def find_longest_word(text: str) -> str:
    """Find the longest word in a text."""
    words = text.split()
    if not words:
        return ""
    return max(words, key=len)

def extract_emails(text: str) -> List[str]:
    """Extract all email addresses from text."""
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.findall(pattern, text)

def truncate_string(text: str, max_length: int, suffix: str = '...') -> str:
    """Truncate string to max_length and add suffix if truncated."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def capitalize_sentences(text: str) -> str:
    """Capitalize the first letter of each sentence."""
    sentences = re.split(r'([.!?]+)', text)
    result = []
    for i in range(0, len(sentences) - 1, 2):
        sentence = sentences[i].strip()
        if sentence:
            result.append(sentence[0].upper() + sentence[1:])
        if i + 1 < len(sentences):
            result.append(sentences[i + 1])
    if len(sentences) % 2:
        last = sentences[-1].strip()
        if last:
            result.append(last[0].upper() + last[1:])
    return ''.join(result)

def remove_duplicate_words(text: str) -> str:
    """Remove duplicate words while maintaining order."""
    words = text.split()
    seen = set()
    unique_words = []
    for word in words:
        if word.lower() not in seen:
            seen.add(word.lower())
            unique_words.append(word)
    return ' '.join(unique_words)
