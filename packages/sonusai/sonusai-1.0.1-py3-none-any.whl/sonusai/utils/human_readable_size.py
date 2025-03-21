def human_readable_size(num: float, decimal_places: int = 3, suffix: str = "B") -> str:
    """Convert number into string with units"""
    for unit in ("", "k", "M", "G", "T", "P", "E", "Z"):
        if abs(num) < 1024.0:
            return f"{num:.{decimal_places}f} {unit}{suffix}"
        num /= 1024.0
    return f"{num:.{decimal_places}f} Y{suffix}"
