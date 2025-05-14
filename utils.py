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
