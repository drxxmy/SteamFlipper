import re

_PRICE_RE = re.compile(r"[0-9]+(?:[.,][0-9]+)?")


def parse_price(price_str: str) -> float:
    """
    Converts Steam price string to float.
    Example: '1 234,56 руб.' → 1234.56
    """
    if not price_str:
        return 0.0

    # Replace comma with dot, remove spaces
    cleaned = price_str.replace(",", ".").replace(" ", "")
    match = _PRICE_RE.search(cleaned)

    return float(match.group()) if match else 0.0
