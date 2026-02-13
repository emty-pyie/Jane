from __future__ import annotations

import importlib
import importlib.util
import os
import platform
import subprocess
import time
import webbrowser
from dataclasses import dataclass
from typing import Callable

import google.generativeai as genai

from jane.commands import ParsedCommand


@dataclass
class ActionResult:
    ok: bool
    message: str


class ActionExecutor:
    def __init__(self, speaker: Callable[[str], None]) -> None:
        self.speaker = speaker
        self.gemini_model = self._init_gemini_model()

    def _init_gemini_model(self):
        key = os.getenv("GEMINI_API_KEY")
        if not key:
            return None
        if importlib.util.find_spec("google.generativeai") is None:
            return None

        genai = importlib.import_module("google.generativeai")
        try:
            genai.configure(api_key=key)
            return genai.GenerativeModel("gemini-1.5-flash")
        except Exception:
            return None

    def execute(self, cmd: ParsedCommand) -> ActionResult:
        action = cmd.action
        if action == "open_whatsapp_web":
            webbrowser.open("https://web.whatsapp.com")
            return ActionResult(True, "Opening WhatsApp Web in browser.")

        if action == "change_theme":
            return self._open_settings_for_theme()

        if action == "install_library":
            library = cmd.params.get("library", "")
            return self._install_library(library)

        if action == "shutdown_system":
            countdown = int(cmd.params.get("countdown", 10))
            return self._shutdown_with_countdown(countdown)

        if action == "open_app_or_site":
            return self._open_target(cmd.params.get("target", ""))

        if action == "chat":
            return self._chat(cmd.params.get("prompt", ""))

        return ActionResult(False, "I could not understand that command.")

    def _open_settings_for_theme(self) -> ActionResult:
        system = platform.system().lower()
        try:
            if "windows" in system:
                subprocess.Popen(["start", "ms-settings:colors"], shell=True)
            elif "darwin" in system:
                subprocess.Popen(["open", "x-apple.systempreferences:"])
            else:
                subprocess.Popen(["gnome-control-center", "appearance"])
            return ActionResult(True, "Opened settings. Please apply your theme preference.")
        except Exception as exc:
            return ActionResult(False, f"Unable to open settings: {exc}")

    def _install_library(self, library: str) -> ActionResult:
        if not library:
            return ActionResult(False, "No library name was provided.")
        try:
            subprocess.check_call(["python", "-m", "pip", "install", library])
            return ActionResult(True, f"Installed library: {library}")
        except Exception as exc:
            return ActionResult(False, f"Failed to install {library}: {exc}")

    def _shutdown_with_countdown(self, seconds: int) -> ActionResult:
        for sec in range(seconds, 0, -1):
            self.speaker(f"Shutdown in {sec}")
            time.sleep(1)
        self.speaker("System Black Out")

        system = platform.system().lower()
        try:
            if "windows" in system:
                subprocess.Popen(["shutdown", "/s", "/t", "0"])
            elif "darwin" in system:
                subprocess.Popen(["sudo", "shutdown", "-h", "now"])
            else:
                subprocess.Popen(["shutdown", "now"])
            return ActionResult(True, "Shutdown command issued.")
        except Exception as exc:
            return ActionResult(False, f"Could not shutdown system: {exc}")

    def _open_target(self, target: str) -> ActionResult:
        if not target:
            return ActionResult(False, "Nothing to open.")
        known_sites = {
            "whatsapp": "https://web.whatsapp.com",
            "youtube": "https://youtube.com",
            "gmail": "https://mail.google.com",
            "chrome": "https://www.google.com",
        }
        key = target.strip().lower()
        if key in known_sites:
            webbrowser.open(known_sites[key])
            return ActionResult(True, f"Opening {key}.")

        try:
            webbrowser.open(target)
            return ActionResult(True, f"Attempting to open {target}.")
        except Exception as exc:
            return ActionResult(False, f"Open failed: {exc}")

    def _chat(self, prompt: str) -> ActionResult:
        if not prompt:
            return ActionResult(True, "How can I assist you?")
        if self.gemini_model is None:
            return ActionResult(True, "Gemini is not configured. Set GEMINI_API_KEY to enable AI chat.")

        try:
            response = self.gemini_model.generate_content(prompt)
            text = getattr(response, "text", None) or "I could not generate a response."
            return ActionResult(True, text)
        except Exception as exc:
            return ActionResult(False, f"AI request failed: {exc}")
