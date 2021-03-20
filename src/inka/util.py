def create_anki_search_query(text: str) -> str:
    """Create Anki search query from the supplied text"""
    special_chars = ['\\', '"', '*', '_', ':']

    search_query = text
    for char in special_chars:
        escaped_char = '\\' + char
        search_query = search_query.replace(char, escaped_char)

    return '"' + search_query + '"'
