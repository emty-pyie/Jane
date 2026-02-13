from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ParsedCommand:
    raw: str
    action: str
    params: dict[str, Any] = field(default_factory=dict)
    high_risk: bool = False


def parse_command(text: str) -> ParsedCommand:
    normalized = text.strip().lower()

    if not normalized:
        return ParsedCommand(raw=text, action="empty")

    if "open chrome" in normalized and "whatsapp" in normalized:
        return ParsedCommand(
            raw=text,
            action="open_whatsapp_web",
            params={"browser": "chrome"},
            high_risk=False,
        )

    if normalized.startswith("open ") and "settings" in normalized and "theme" in normalized:
        return ParsedCommand(raw=text, action="change_theme", params={}, high_risk=True)

    download_match = re.search(r"download\s+(?:this\s+library\s+)?([a-z0-9_\-.]+)", normalized)
    if "open terminal" in normalized and download_match:
        return ParsedCommand(
            raw=text,
            action="install_library",
            params={"library": download_match.group(1)},
            high_risk=True,
        )

    if "shut down" in normalized or "shutdown" in normalized:
        return ParsedCommand(raw=text, action="shutdown_system", params={"countdown": 10}, high_risk=True)

    if "what time" in normalized or "current time" in normalized:
        return ParsedCommand(raw=text, action="tell_time")

    if "what date" in normalized or "today date" in normalized:
        return ParsedCommand(raw=text, action="tell_date")

    note_match = re.search(r"note\s*[:\-]?\s*(.+)$", text.strip(), re.IGNORECASE)
    if note_match:
        return ParsedCommand(raw=text, action="save_note", params={"note": note_match.group(1).strip()})

    if "open calculator" in normalized:
        return ParsedCommand(raw=text, action="open_calculator")

    if "open notepad" in normalized or "open editor" in normalized:
        return ParsedCommand(raw=text, action="open_notepad")

    open_match = re.match(r"open\s+(.+)", normalized)
    if open_match:
        return ParsedCommand(raw=text, action="open_app_or_site", params={"target": open_match.group(1).strip()})

    return ParsedCommand(raw=text, action="chat", params={"prompt": text}, high_risk=False)
