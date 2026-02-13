from __future__ import annotations

import threading
from collections import deque
from datetime import datetime
from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import BooleanProperty, NumericProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from jane.actions import ActionExecutor
from jane.commands import ParsedCommand, extract_wake_word_command, parse_command
from jane.speech import SpeechEngine
from jane.vision import capture_frame

WAKE_WORD = "hey jane"
KV_PATH = Path(__file__).with_name("ui.kv")


class AssistantRoot(BoxLayout):
    title_text = StringProperty("JANE")
    subtitle_text = StringProperty("Deployed By: Visrodeck Technology")
    status_text = StringProperty("Stable Desktop Core | Professional Mode")
    wake_word_text = StringProperty("Wake word: Hey Jane")
    log_text = StringProperty("[BOOT] JANE core is online.\n")
    has_pending_risk = BooleanProperty(False)
    pending_count = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.speech = SpeechEngine()
        self.executor = ActionExecutor(self.safe_speak)
        self.pending: deque[ParsedCommand] = deque()
        self.risk_popup: Popup | None = None
        self.safe_speak("Hello, I am JANE. Say 'Hey Jane' before voice commands.")

    def append_log(self, line: str) -> None:
        self.log_text += line + "\n"

    def safe_speak(self, text: str) -> None:
        self.append_log(f"JANE: {text}")

        def _speak() -> None:
            try:
                self.speech.speak(text)
            except Exception as exc:  # noqa: BLE001
                Clock.schedule_once(lambda *_: self.append_log(f"[WARN] TTS failed: {exc}"), 0)

        threading.Thread(target=_speak, daemon=True).start()

    def _refresh_pending_flags(self) -> None:
        self.pending_count = len(self.pending)
        self.has_pending_risk = self.pending_count > 0

    def run_quick(self, command: str) -> None:
        self.process_command(command)

    def save_note_from_ui(self) -> None:
        note = self.ids.note_input.text.strip()
        if not note:
            self.append_log("[INFO] Note box is empty.")
            return
        self.ids.note_input.text = ""
        self.process_command(f"note: {note}")

    def clear_logs(self) -> None:
        self.log_text = f"[RESET] Console cleared at {datetime.now().strftime('%H:%M:%S')}\n"

    def export_logs(self) -> None:
        path = Path("jane_console_log.txt")
        path.write_text(self.log_text, encoding="utf-8")
        self.append_log(f"[INFO] Logs exported to {path}")

    def submit_text_command(self) -> None:
        user_input = self.ids.user_input
        text = user_input.text.strip()
        user_input.text = ""
        if text:
            self.process_command(text)

    def listen_voice(self) -> None:
        self.append_log("[VOICE] Listening for wake word...")

        def _listen() -> None:
            try:
                transcript = self.speech.listen_once()
                Clock.schedule_once(lambda *_: self._handle_voice_transcript(transcript), 0)
            except Exception as exc:  # noqa: BLE001
                Clock.schedule_once(lambda *_: self.append_log(f"[WARN] STT failed: {exc}"), 0)

        threading.Thread(target=_listen, daemon=True).start()

    def _handle_voice_transcript(self, transcript: str) -> None:
        self.append_log(f"Heard: {transcript}")
        command = extract_wake_word_command(transcript, WAKE_WORD)
        if command is None:
            self.safe_speak("Wake word missing. Say Hey Jane followed by a command.")
            return
        if not command:
            self.safe_speak("I heard Hey Jane. Please say a command after the wake word.")
            return
        self.process_command(command)


    def process_command(self, text: str) -> None:
        self.append_log(f"You: {text}")
        parsed = parse_command(text)
        if parsed.action == "empty":
            return

        if parsed.high_risk:
            self.pending.append(parsed)
            self._refresh_pending_flags()
            self.safe_speak(f"High-risk command queued for approval: {parsed.raw}")
            self.show_risk_popup(parsed)
            return

        self.run_command(parsed)

    def run_command(self, parsed: ParsedCommand) -> None:
        def _run() -> None:
            result = self.executor.execute(parsed)
            Clock.schedule_once(lambda *_: self.safe_speak(result.message), 0)

        threading.Thread(target=_run, daemon=True).start()

    def approve_pending(self) -> None:
        if not self.pending:
            self._refresh_pending_flags()
            self.dismiss_risk_popup()
            return
        command = self.pending.popleft()
        self._refresh_pending_flags()
        self.append_log(f"[APPROVED] {command.raw}")
        self.dismiss_risk_popup()
        self.run_command(command)

    def deny_pending(self) -> None:
        if not self.pending:
            self._refresh_pending_flags()
            self.dismiss_risk_popup()
            return
        command = self.pending.popleft()
        self._refresh_pending_flags()
        self.dismiss_risk_popup()
        self.safe_speak(f"Denied: {command.raw}")

    def dismiss_risk_popup(self) -> None:
        if self.risk_popup is not None:
            self.risk_popup.dismiss()
            self.risk_popup = None

    def show_risk_popup(self, parsed: ParsedCommand) -> None:
        self.dismiss_risk_popup()
        content = BoxLayout(orientation="vertical", spacing=12, padding=12)
        content.add_widget(
            Label(
                text=(
                    "Dangerous command detected.\n\n"
                    f"[b]{parsed.raw}[/b]\n\n"
                    "Grant once to continue or deny to block."
                ),
                markup=True,
                halign="left",
                valign="middle",
            )
        )

        action_row = BoxLayout(size_hint_y=None, height=46, spacing=10)
        grant_btn = Button(text="✅ Grant Once")
        deny_btn = Button(text="❌ Deny")
        grant_btn.bind(on_release=lambda *_: self.approve_pending())
        deny_btn.bind(on_release=lambda *_: self.deny_pending())
        action_row.add_widget(grant_btn)
        action_row.add_widget(deny_btn)
        content.add_widget(action_row)

        self.risk_popup = Popup(
            title="JANE Security Approval",
            content=content,
            size_hint=(0.66, 0.42),
            auto_dismiss=False,
        )
        self.risk_popup.open()

    def capture_vision(self) -> None:
        def _capture() -> None:
            try:
                path = capture_frame()
                Clock.schedule_once(lambda *_: self.safe_speak(f"Vision frame saved: {path}"), 0)
            except Exception as exc:  # noqa: BLE001
                Clock.schedule_once(lambda *_: self.append_log(f"[WARN] Vision capture failed: {exc}"), 0)

        threading.Thread(target=_capture, daemon=True).start()


class JaneApp(App):
    def build(self):
        Builder.load_file(str(KV_PATH))
        return AssistantRoot()
