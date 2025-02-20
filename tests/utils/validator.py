import re


def is_valid_time_format(time_str: str) -> bool:
    """Check if the given time string matches the 'YYYY-MM-DDTHH:MM:SS' format."""
    pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$"
    return bool(re.match(pattern, time_str))
