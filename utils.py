import re
import unicodedata

def slugify(text):
    # Normalize Unicode characters
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("utf-8")
    # Remove punctuation, replace spaces with hyphens, lowercase
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "-", text)


def strip_html(text):
    return re.sub(r'<[^>]*?>', '', text)

def category_to_url(category):
    """Convert a category name to URL-friendly format"""
    return category.strip().lower().replace(" ", "-")

def url_to_category(category_url):
    """Convert a URL-friendly category back to database format"""
    return category_url.replace("-", " ")

def generate_meta_description(text, max_length=160, min_sentence_len=40):
    # Strip HTML tags
    clean = re.sub(r'<[^>]+>', '', text).strip()

    # If already short, return as-is
    if len(clean) <= max_length:
        return clean

    # Try to extract the longest sequence of complete sentences under max_length
    sentences = re.split(r'(?<=[.!?]) +', clean)
    result = ""
    for sentence in sentences:
        if len(result) + len(sentence) <= max_length:
            result += sentence + " "
        else:
            break

    result = result.strip()

    # If we managed to form a full sentence chunk, return it
    if len(result) >= min_sentence_len:
        return result

    # Fallback: cut at word boundary and add ellipsis
    fallback = clean[:max_length - 3]  # Reserve space for "..."
    last_space = fallback.rfind(" ")
    return fallback[:last_space].strip() + "..."
