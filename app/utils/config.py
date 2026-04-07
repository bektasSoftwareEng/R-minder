from app.core import repository


def get(key: str, default: str = "") -> str:
    value = repository.get_setting(key)
    return value if value is not None else default


def set(key: str, value: str) -> None:
    repository.set_setting(key, value)


def get_int(key: str, default: int = 0) -> int:
    try:
        return int(get(key, str(default)))
    except ValueError:
        return default


def get_widget_geometry() -> tuple[int, int, int, int]:
    """(x, y, width, height) döner."""
    return (
        get_int("widget_x", 40),
        get_int("widget_y", 40),
        get_int("widget_width", 320),
        get_int("widget_height", 520),
    )


def save_widget_geometry(x: int, y: int, width: int, height: int) -> None:
    set("widget_x", str(x))
    set("widget_y", str(y))
    set("widget_width", str(width))
    set("widget_height", str(height))


def get_notification_lead_minutes() -> int:
    return get_int("notification_lead_minutes", 15)
