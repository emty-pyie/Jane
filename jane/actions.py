from __future__ import annotations

import importlib
import importlib.util
import os
import platform
import shutil
import shlex
import subprocess
import time
import webbrowser
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable

from jane.commands import ParsedCommand


@dataclass
class ActionResult:
    ok: bool
    message: str


class ActionExecutor:
    def __init__(self, speaker: Callable[[str], None]) -> None:
        self.speaker = speaker
        self._gemini_key_loaded: str | None = None
        self.gemini_model = self._init_gemini_model()
        self.notes_file = Path("jane_notes.txt")

    def _resolve_gemini_key(self) -> str | None:
        candidates = [
            os.getenv("GEMINI_API_KEY"),
            os.getenv("GEMENI_API_KEY"),
            os.getenv("GOOGLE_API_KEY"),
        ]
        for key in candidates:
            if not key:
                continue
            cleaned = key.strip().strip("\"'").strip()
            cleaned = cleaned.strip("()")
            if cleaned:
                return cleaned
        return None

    def _init_gemini_model(self):
        key = self._resolve_gemini_key()
        if not key:
            return None
        try:
            if importlib.util.find_spec("google.generativeai") is None:
                return None
        except ModuleNotFoundError:
            return None

        try:
            genai = importlib.import_module("google.generativeai")
        except ModuleNotFoundError:
            return None
        try:
            genai.configure(api_key=key)
            self._gemini_key_loaded = key
        self.gemini_model = self._init_gemini_model()
        self.notes_file = Path("jane_notes.txt")

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

    def _ensure_gemini_ready(self) -> bool:
        key = self._resolve_gemini_key()
        if not key:
            self.gemini_model = None
            return False
        if self.gemini_model is not None and self._gemini_key_loaded == key:
            return True
        self.gemini_model = self._init_gemini_model()
        return self.gemini_model is not None

    def execute(self, cmd: ParsedCommand) -> ActionResult:
        action = cmd.action
        if action == "open_whatsapp_web":
            webbrowser.open("https://web.whatsapp.com")
            return ActionResult(True, "Opening WhatsApp Web in browser.")
        if action == "change_theme":
            return self._open_settings_for_theme()
        if action == "install_library":
            return self._install_library(cmd.params.get("library", ""))
        if action == "shutdown_system":
            return self._shutdown_with_countdown(int(cmd.params.get("countdown", 10)))
        if action == "open_app_or_site":
            return self._open_target(cmd.params.get("target", ""))
        if action == "tell_time":
            return ActionResult(True, f"Current time is {datetime.now().strftime('%I:%M %p')}.")
        if action == "tell_date":
            return ActionResult(True, f"Today is {datetime.now().strftime('%A, %d %B %Y')}.")
        if action == "save_note":
            return self._save_note(cmd.params.get("note", ""))
        if action == "open_calculator":
            return self._open_system_app(["calc", "gnome-calculator", "open -a Calculator"])
        if action == "open_notepad":
            return self._open_system_app(["notepad", "gedit", "open -a TextEdit"])
        if action == "chat":
            return self._chat(cmd.params.get("prompt", ""))
        return ActionResult(False, "I could not understand that command.")

    def _open_settings_for_theme(self) -> ActionResult:
        system = platform.system().lower()
        try:
            if "windows" in system:
                return self._run_with_admin(
                    ["start", "ms-settings:colors"],
                    "Open Windows color settings",
                    shell=True,
                )
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
            return self._run_with_admin(
                ["python", "-m", "pip", "install", library],
                f"Install library: {library}",
                wait=True,
            )
        except Exception as exc:
            return ActionResult(False, f"Failed to install {library}: {exc}")

    def _shutdown_with_countdown(self, seconds: int) -> ActionResult:
        for sec in range(seconds, 0, -1):
            self.speaker(f"Shutdown in {sec}")
            time.sleep(1)
        self.speaker("System Black Out")

        system = platform.system().lower()
        if "windows" in system:
            return self._run_with_admin(["shutdown", "/s", "/t", "0"], "Shutdown system")
        if "darwin" in system:
            return self._run_with_admin(["shutdown", "-h", "now"], "Shutdown system")
        return self._run_with_admin(["shutdown", "now"], "Shutdown system")

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

    def _save_note(self, note: str) -> ActionResult:
        if not note:
            return ActionResult(False, "Note text was empty.")
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.notes_file.open("a", encoding="utf-8") as fh:
            fh.write(f"[{stamp}] {note}\n")
        self.notes_file.write_text(
            (self.notes_file.read_text() if self.notes_file.exists() else "") + f"[{stamp}] {note}\n",
            encoding="utf-8",
        )
        return ActionResult(True, "Note saved to jane_notes.txt")

    def _open_system_app(self, candidates: list[str]) -> ActionResult:
        system = platform.system().lower()
        for cmd in candidates:
            try:
                if "windows" in system and cmd == "open -a Calculator":
                    continue
                if "windows" in system and cmd == "open -a TextEdit":
                    continue
                if "darwin" in system and cmd in {"calc", "gnome-calculator", "notepad", "gedit"}:
                    continue
                if " " in cmd:
                    subprocess.Popen(cmd, shell=True)
                else:
                    subprocess.Popen([cmd])
                return ActionResult(True, f"Launching app via: {cmd}")
            except Exception:
                continue
        return ActionResult(False, "Unable to open requested app on this system.")

    def _chat(self, prompt: str) -> ActionResult:
        if not prompt:
            return ActionResult(True, "How can I assist you?")
        if not self._ensure_gemini_ready():
            return ActionResult(
                True,
                "Gemini is not configured. Set GEMINI_API_KEY (or GEMENI_API_KEY / GOOGLE_API_KEY) and ensure google-generativeai is installed.",
            )
        if self.gemini_model is None:
            return ActionResult(True, "Gemini is not configured. Set GEMINI_API_KEY to enable AI chat.")
        try:
            response = self.gemini_model.generate_content(prompt)
            text = getattr(response, "text", None) or "I could not generate a response."
            return ActionResult(True, text)
        except Exception as exc:
            return ActionResult(False, f"AI request failed: {exc}")

    def _run_with_admin(self, command: list[str], reason: str, shell: bool = False, wait: bool = False) -> ActionResult:
        system = platform.system().lower()

        try:
            if "windows" in system:
                cmdline = " ".join(shlex.quote(part) for part in command)
                elevate = [
                    "powershell",
                    "-Command",
                    f"Start-Process cmd -Verb RunAs -ArgumentList '/c {cmdline}'",
                ]
                proc = subprocess.Popen(elevate)
                if wait:
                    proc.wait()
                return ActionResult(True, f"Admin request launched for: {reason}")

            if "darwin" in system:
                cmdline = " ".join(shlex.quote(part) for part in command)
                osa = [
                    "osascript",
                    "-e",
                    f'do shell script "{cmdline}" with administrator privileges',
                ]
                proc = subprocess.Popen(osa)
                if wait:
                    proc.wait()
                return ActionResult(True, f"Admin request launched for: {reason}")

            if shutil.which("pkexec"):
                proc = subprocess.Popen(["pkexec", *command], shell=shell)
                if wait:
                    proc.wait()
                return ActionResult(True, f"Admin request launched for: {reason}")

            if shutil.which("sudo"):
                proc = subprocess.Popen(["sudo", *command], shell=shell)
                if wait:
                    proc.wait()
                return ActionResult(True, f"Admin request launched for: {reason}")

            return ActionResult(False, f"Admin tools unavailable for: {reason}")
        except Exception as exc:
            return ActionResult(False, f"Admin execution failed for {reason}: {exc}")
