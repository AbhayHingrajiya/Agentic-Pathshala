def validate_menu_choice(choice: str, minimum: int = 1, maximum: int = 6) -> bool:
    if not isinstance(choice, str) or not choice.strip().isdigit():
        return False

    numeric_choice = int(choice.strip())
    return minimum <= numeric_choice <= maximum


def is_non_empty_string(value: str) -> bool:
    return bool(value and value.strip())
