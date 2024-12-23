from functools import reduce


def clean_field_name(v: str) -> str:
    """Normalize a field name by removing specific substrings (case-insensitive) and converting it to lowercase.

    Args:
        v (str): The original field name.

    Returns:
        str: The cleaned field name.

    """
    to_remove = ("_h_c", "_h_f", "_i_c", "_i_f")
    return reduce(lambda name, substr: name.replace(substr, ""), to_remove, v.lower())
