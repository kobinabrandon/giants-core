def remove_new_line_marker(text: str) -> str:
    """
    Remove the commonly used new line marker "\n" from the raw text 

    Args:
        text: the raw text 

    Returns:
        str: the text with the new line marker removed
    """
    return text.replace("\n", " ").strip()

