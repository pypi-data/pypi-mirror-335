def hide_value(value, default="Not defined"):
    if not value:
        return default
    value_to_hide = "***"
    if len(value) > 4:
        value_to_hide = f"{value[0]}****{value[-1:]}"
    return value_to_hide
