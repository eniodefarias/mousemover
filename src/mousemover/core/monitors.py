from screeninfo import get_monitors


def monitors():
    return get_monitors()


def monitor_description(index: int, m) -> str:
    orientation = "Landscape" if m.width >= m.height else "Portrait"
    primary = " | Principal" if getattr(m, "is_primary", False) else ""
    return (
        f"{index} | {getattr(m, 'name', None) or 'Monitor'} | "
        f"{m.width}x{m.height} | X={m.x} Y={m.y} | {orientation}{primary}"
    )


def point_on_any_monitor(x: int, y: int) -> bool:
    for m in get_monitors():
        if m.x <= x < m.x + m.width and m.y <= y < m.y + m.height:
            return True
    return False


def clamp_to_monitor(x: int, y: int, m) -> tuple[int, int]:
    return (
        max(m.x, min(x, m.x + m.width - 1)),
        max(m.y, min(y, m.y + m.height - 1)),
    )
