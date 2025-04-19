from typing import List, Any
import enum
import shutil
import os


class Color(enum.Enum):
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"


terminal_width = shutil.get_terminal_size(fallback=(80, 24)).columns
terminal_height = shutil.get_terminal_size(fallback=(80, 24)).lines - 2


def clear():
    if "GIT_ANCHOR_INTERACTIVE" not in os.environ:
        return

    global terminal_height
    terminal_height = shutil.get_terminal_size(fallback=(80, 24)).lines - 2
    print("\033[2J\033[H", end="")
    clog(Color.RED, "#" * terminal_width)


def log(color: Color, obj: Any):
    if "GIT_ANCHOR_INTERACTIVE" not in os.environ:
        return

    global terminal_height
    lines = []

    if terminal_height <= 0:
        clear()

    if isinstance(obj, str):
        lines = repr_str(
            obj, max_width=terminal_width, max_lines=min(20, terminal_height)
        )
    elif isinstance(obj, list):
        lines = repr_arr(obj, max_lines=terminal_height)
    else:
        lines = repr(obj, max_lines=terminal_height)

    terminal_height -= len(lines)
    clog_arr(color, lines)


def clog(color: Color, text: str):
    """Print text in color."""
    print(f"{color.value}{text}\033[0m")


def clog_arr(color: Color, arr: List[str]):
    for text in arr:
        clog(color, text)


def repr(obj: Any, max_width: int = 80, max_lines: int = 20) -> List[str]:
    """pretty print object based on its type"""
    if isinstance(obj, list):
        return repr_arr(obj, max_width=max_width, max_lines=min(20, max_lines))
    else:
        return repr_str(obj, max_width=max_width, max_lines=min(20, max_lines))


def repr_str(
    obj: str, prefix: str = "", max_width: int = 80, max_lines: int = 4
) -> List[str]:
    lines = str(obj).strip().splitlines()
    compact_lines = [
        [
            " " * len(prefix) + line[i : i + max_width - len(prefix)]
            for i in range(0, len(line), max_width - len(prefix))
        ]
        for line in lines
    ]
    line_array = sum(compact_lines, [])
    line_array[0] = prefix + line_array[0][len(prefix) :]

    result = line_array[0:max_lines]
    if len(line_array) > max_lines:
        result[-1] = " " * len(prefix) + "..."

    return result


def repr_arr(arr: List[Any], max_width: int = 80, max_lines: int = 40) -> List[str]:
    items_show: List[str] = []
    for index, item in enumerate(arr):
        item_repr = repr_str(
            item, prefix=f"{index + 1:02d}. ", max_width=max_width, max_lines=5
        )

        items_show.extend(item_repr)
        if len(item_repr) > 1 and item_repr[-1] != "\n":
            items_show.append("")

    result = items_show[0:max_lines]
    if len(items_show) > max_lines:
        result[-1] = f"... and {len(items_show) - max_lines} more"

    return result
