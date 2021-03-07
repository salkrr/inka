def escape_special_chars(text: str) -> str:
    """Escape special chars from Anki search query"""
    special_chars = ['\\', '"', '*', '_', '(', ')', '-', ':']
    # We use two backward slashes because JSON requires backward slash to be escaped
    escape_chars = r'\\'
    for char in special_chars:
        escaped = escape_chars + char
        if char == '\\':
            # Because otherwise '\' will be replaced with '\\\' instead of '\\'
            escaped = escape_chars

        text = text.replace(char, escaped)

    return text
