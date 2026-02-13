from __future__ import annotations

import threading
from collections import deque

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout

from jane.actions import ActionExecutor
from jane.commands import ParsedCommand, parse_command
from jane.speech import SpeechEngine
from jane.vision import capture_frame

KV = '''
<AssistantRoot>:
    orientation: 'vertical'
    spacing: dp(10)
    padding: dp(12)
    canvas.before:
        Color:
            rgba: 0.07, 0.08, 0.1, 1
        Rectangle:
            pos: self.pos
            size: self.size

    Label:
        text: root.title_text
        font_size: '26sp'
        bold: True
        color: 0.3, 0.85, 1, 1
        size_hint_y: None
        height: dp(44)

    Label:
        text: root.subtitle_text
        color: 0.75, 0.78, 0.82, 1
        size_hint_y: None
        height: dp(28)

    TextInput:
        id: log_view
        text: root.log_text
        readonly: True
        background_color: 0.12, 0.13, 0.16, 1
        foreground_color: 0.9, 0.92, 0.97, 1

    BoxLayout:
        size_hint_y: None
        height: dp(46)
        spacing: dp(8)
        TextInput:
            id: user_input
            multiline: False
            hint_text: 'Type a command for JANE...'
            background_color: 0.14, 0.15, 0.2, 1
            foreground_color: 1, 1, 1, 1
            on_text_validate: root.submit_text_command()
        Button:
            text: 'Send'
            on_release: root.submit_text_command()

    BoxLayout:
        size_hint_y: None
        height: dp(46)
        spacing: dp(8)
        Button:
            text: '🎤 Listen'
            on_release: root.listen_voice()
        Button:
            text: '📷 Capture Vision Frame'
            on_release: root.capture_vision()

    BoxLayout:
        size_hint_y: None
        height: dp(46)
        spacing: dp(8)
        opacity: 1 if root.has_pending_risk else 0.2
        Button:
            text: '✅ Grant Selected'
            disabled: not root.has_pending_risk
            on_release: root.approve_pending()
        Button:
            text: '❌ Deny Selected'
            disabled: not root.has_pending_risk
            on_release: root.deny_pending()
'''


class AssistantRoot(BoxLayout):
    title_text = StringProperty("JANE")
    subtitle_text = StringProperty("Deployed By: Visrodeck Technology")
    log_text = StringProperty("[BOOT] JANE is online.\n")
    has_pending_risk = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.speech = SpeechEngine()
        self.executor = ActionExecutor(self.safe_speak)
        self.pending: deque[ParsedCommand] = deque()
        self.safe_speak("Hello, I am JANE. How can I assist you today?")

    def append_log(self, line: str) -> None:
        self.log_text += line + "\n"

    def safe_speak(self, text: str) -> None:
        self.append_log(f"JANE: {text}")

        def _speak():
            try:
                self.speech.speak(text)
            except Exception as exc:
                Clock.schedule_once(lambda *_: self.append_log(f"[WARN] TTS failed: {exc}"), 0)

        threading.Thread(target=_speak, daemon=True).start()

    def submit_text_command(self) -> None:
        user_input = self.ids.user_input
        text = user_input.text.strip()
        user_input.text = ""
        if text:
            self.process_command(text)

    def listen_voice(self) -> None:
        self.append_log("[VOICE] Listening...")

        def _listen():
            try:
                recognized = self.speech.listen_once()
                Clock.schedule_once(lambda *_: self.process_command(recognized), 0)
            except Exception as exc:
                Clock.schedule_once(lambda *_: self.append_log(f"[WARN] STT failed: {exc}"), 0)

        threading.Thread(target=_listen, daemon=True).start()

    def process_command(self, text: str) -> None:
        self.append_log(f"You: {text}")
        parsed = parse_command(text)
        if parsed.action == "empty":
            return

        if parsed.high_risk:
            self.pending.append(parsed)
            self.has_pending_risk = True
            self.safe_speak(f"High-risk command queued for approval: {parsed.raw}")
            return

        self.run_command(parsed)

    def run_command(self, parsed: ParsedCommand) -> None:
        def _run():
            result = self.executor.execute(parsed)
            Clock.schedule_once(lambda *_: self.safe_speak(result.message), 0)

        threading.Thread(target=_run, daemon=True).start()

    def approve_pending(self) -> None:
        if not self.pending:
            self.has_pending_risk = False
            return
        command = self.pending.popleft()
        self.has_pending_risk = bool(self.pending)
        self.append_log(f"[APPROVED] {command.raw}")
        self.run_command(command)

    def deny_pending(self) -> None:
        if not self.pending:
            self.has_pending_risk = False
            return
        command = self.pending.popleft()
        self.has_pending_risk = bool(self.pending)
        self.safe_speak(f"Denied: {command.raw}")

    def capture_vision(self) -> None:
        def _capture():
            try:
                path = capture_frame()
                Clock.schedule_once(lambda *_: self.safe_speak(f"Vision frame saved: {path}"), 0)
            except Exception as exc:
                Clock.schedule_once(lambda *_: self.append_log(f"[WARN] Vision capture failed: {exc}"), 0)

        threading.Thread(target=_capture, daemon=True).start()


class JaneApp(App):
    def build(self):
        Builder.load_string(KV)
        return AssistantRoot()
