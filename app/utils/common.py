import re


def extract_post_code(url: str) -> str:
    """
    Extracts the post code from an Instagram post URL.
    """
    match = re.search(r"/(p|tv|reel)/([^/]+)", url)
    if match:
        return match.group(2)
    return None
