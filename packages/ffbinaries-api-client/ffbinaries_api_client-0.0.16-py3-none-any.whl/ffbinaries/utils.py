"""Utils Module."""


def is_float(value: str) -> bool:
    """Check if value is a float."""
    try:
        float(value)
    except ValueError:
        return False
    return True
