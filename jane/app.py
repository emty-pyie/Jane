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
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout

from jane.actions import ActionExecutor
from jane.commands import ParsedCommand, parse_command
from jane.speech import SpeechEngine
from jane.vision import capture_frame

KV = '''
#:import dp kivy.metrics.dp

<AssistantRoot>:
    orientation: 'vertical'
    padding: dp(16)
    spacing: dp(12)
    canvas.before:
        Color:
            rgba: 0.03, 0.04, 0.09, 1
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

    BoxLayout:
        size_hint_y: None
        height: dp(92)
        spacing: dp(12)
        padding: dp(14)
        canvas.before:
            Color:
                rgba: 0.08, 0.12, 0.22, 1
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [18, 18, 18, 18]

        BoxLayout:
            orientation: 'vertical'
            Label:
                text: root.title_text
                color: 0.34, 0.90, 1, 1
                font_size: '31sp'
                bold: True
                halign: 'left'
                text_size: self.size
            Label:
                text: root.subtitle_text
                color: 0.76, 0.83, 0.97, 1
                font_size: '14sp'
                halign: 'left'
                text_size: self.size

        BoxLayout:
            orientation: 'vertical'
            size_hint_x: None
            width: dp(310)
            Label:
                text: 'Operational Status'
                color: 0.66, 0.79, 1, 1
                font_size: '13sp'
                halign: 'right'
                text_size: self.size
            Label:
                text: root.status_text
                color: 0.97, 0.98, 1, 1
                bold: True
                font_size: '15sp'
                halign: 'right'
                text_size: self.size

    BoxLayout:
        spacing: dp(12)

        BoxLayout:
            orientation: 'vertical'
            spacing: dp(10)

            BoxLayout:
                size_hint_y: None
                height: dp(52)
                spacing: dp(8)
                TextInput:
                    id: user_input
                    multiline: False
                    hint_text: 'Type command for JANE...'
                    background_color: 0.1, 0.13, 0.21, 1
                    foreground_color: 0.94, 0.98, 1, 1
                    cursor_color: 0.33, 0.93, 1, 1
                    padding: dp(12), dp(14)
                    on_text_validate: root.submit_text_command()
                Button:
                    text: 'Execute'
                    size_hint_x: None
                    width: dp(120)
                    background_normal: ''
                    background_color: 0.26, 0.87, 1, 1
                    color: 0.03, 0.08, 0.13, 1
                    bold: True
                    on_release: root.submit_text_command()

            BoxLayout:
                size_hint_y: None
                height: dp(40)
                spacing: dp(8)
                Button:
                    text: 'What Time'
                    background_normal: ''
                    background_color: 0.18, 0.65, 1, 1
                    on_release: root.run_quick('what time is it')
                Button:
                    text: 'Open WhatsApp'
                    background_normal: ''
                    background_color: 0.27, 0.77, 0.62, 1
                    on_release: root.run_quick('open chrome and open whatsapp')
                Button:
                    text: 'Open Calculator'
                    background_normal: ''
                    background_color: 0.60, 0.67, 1, 1
                    on_release: root.run_quick('open calculator')

            TextInput:
                id: log_view
                text: root.log_text
                readonly: True
                background_color: 0.06, 0.08, 0.14, 1
                foreground_color: 0.89, 0.94, 1, 1

            BoxLayout:
                size_hint_y: None
                height: dp(40)
                spacing: dp(8)
                Button:
                    text: 'Export Logs'
                    background_normal: ''
                    background_color: 0.83, 0.74, 0.34, 1
                    color: 0.14, 0.10, 0.02, 1
                    on_release: root.export_logs()
                Button:
                    text: 'Clear Console'
                    background_normal: ''
                    background_color: 0.94, 0.45, 0.50, 1
                    color: 0.14, 0.03, 0.05, 1
                    on_release: root.clear_logs()

        BoxLayout:
            orientation: 'vertical'
            size_hint_x: None
            width: dp(292)
            spacing: dp(10)

            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: dp(178)
                padding: dp(12)
                spacing: dp(8)
                canvas.before:
                    Color:
                        rgba: 0.09, 0.13, 0.21, 1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [16, 16, 16, 16]
                Label:
                    text: 'Core Controls'
                    color: 0.65, 0.84, 1, 1
                    bold: True
                Button:
                    text: '🎤 Voice Listen'
                    background_normal: ''
                    background_color: 0.35, 0.86, 0.72, 1
                    color: 0.03, 0.10, 0.08, 1
                    on_release: root.listen_voice()
                Button:
                    text: '📷 Vision Capture'
                    background_normal: ''
                    background_color: 0.57, 0.75, 1, 1
                    color: 0.03, 0.07, 0.12, 1
                    on_release: root.capture_vision()
                Label:
                    text: 'Queued High-Risk: ' + str(root.pending_count)
                    color: 0.95, 0.83, 0.50, 1

            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: dp(170)
                padding: dp(12)
                spacing: dp(8)
                canvas.before:
                    Color:
                        rgba: 0.16, 0.12, 0.12, 1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [16, 16, 16, 16]

                Label:
                    text: 'High Risk Command Gate'
                    color: 1, 0.86, 0.75, 1
                    bold: True
                Button:
                    text: '✅ Grant Approval'
                    disabled: not root.has_pending_risk
                    background_normal: ''
                    background_color: 0.97, 0.80, 0.36, 1
                    color: 0.16, 0.10, 0.02, 1
                    on_release: root.approve_pending()
                Button:
                    text: '❌ Deny Approval'
                    disabled: not root.has_pending_risk
                    background_normal: ''
                    background_color: 0.97, 0.48, 0.56, 1
                    color: 0.17, 0.03, 0.06, 1
                    on_release: root.deny_pending()

            BoxLayout:
                orientation: 'vertical'
                padding: dp(12)
                spacing: dp(6)
                canvas.before:
                    Color:
                        rgba: 0.08, 0.10, 0.17, 1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [16, 16, 16, 16]
                Label:
                    text: 'Quick Notes'
                    color: 0.72, 0.86, 1, 1
                    bold: True
                TextInput:
                    id: note_input
                    hint_text: 'Type note and click Save Note'
                    multiline: True
                    background_color: 0.1, 0.13, 0.2, 1
                    foreground_color: 0.95, 0.98, 1, 1
                Button:
                    text: 'Save Note'
                    background_normal: ''
                    background_color: 0.40, 0.78, 1, 1
                    color: 0.03, 0.08, 0.12, 1
                    on_release: root.save_note_from_ui()
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
    status_text = StringProperty("Stable Desktop Core | Professional Mode")
    wake_word_text = StringProperty("Wake word: Hey Jane")
    log_text = StringProperty("[BOOT] JANE core is online.\n")
    has_pending_risk = BooleanProperty(False)
    pending_count = NumericProperty(0)
    log_text = StringProperty("[BOOT] JANE core is online.\n")
    has_pending_risk = BooleanProperty(False)
    pending_count = NumericProperty(0)
    log_text = StringProperty("[BOOT] JANE is online.\n")
    has_pending_risk = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.speech = SpeechEngine()
        self.executor = ActionExecutor(self.safe_speak)
        self.pending: deque[ParsedCommand] = deque()
        self.risk_popup: Popup | None = None
        self.safe_speak("Hello, I am JANE. Say 'Hey Jane' before voice commands.")
        self.safe_speak("Hello, I am JANE. Premium desktop interface initialized.")
        self.safe_speak("Hello, I am JANE. How can I assist you today?")

    def append_log(self, line: str) -> None:
        self.log_text += line + "\n"

    def safe_speak(self, text: str) -> None:
        self.append_log(f"JANE: {text}")

        def _speak() -> None:
            try:
                self.speech.speak(text)
            except Exception as exc:  # noqa: BLE001
        def _speak():
            try:
                self.speech.speak(text)
            except Exception as exc:
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
        self.append_log("[VOICE] Listening...")

        def _listen():
            try:
                recognized = self.speech.listen_once()
                Clock.schedule_once(lambda *_: self.process_command(recognized), 0)
            except Exception as exc:
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
            self.has_pending_risk = True
            self.safe_speak(f"High-risk command queued for approval: {parsed.raw}")
            return

        self.run_command(parsed)

    def run_command(self, parsed: ParsedCommand) -> None:
        def _run() -> None:
        def _run():
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
            self.has_pending_risk = False
            return
        command = self.pending.popleft()
        self.has_pending_risk = bool(self.pending)
        self.append_log(f"[APPROVED] {command.raw}")
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
        grant_btn = Button(
            text="✅ Grant Once",
            background_normal="",
            background_color=(0.97, 0.80, 0.36, 1),
            color=(0.16, 0.10, 0.02, 1),
        )
        deny_btn = Button(
            text="❌ Deny",
            background_normal="",
            background_color=(0.97, 0.48, 0.56, 1),
            color=(0.17, 0.03, 0.06, 1),
        )
        grant_btn.bind(on_release=lambda *_: self.approve_pending())
        deny_btn.bind(on_release=lambda *_: self.deny_pending())
        action_row.add_widget(grant_btn)
        action_row.add_widget(deny_btn)
        content.add_widget(action_row)

        self.risk_popup = Popup(
            title="JANE Security Approval",
            content=content,
            size_hint=(0.66, 0.42),
            size_hint=(0.65, 0.42),
            auto_dismiss=False,
        )
        self.risk_popup.open()

    def capture_vision(self) -> None:
        def _capture() -> None:
            try:
                path = capture_frame()
                Clock.schedule_once(lambda *_: self.safe_speak(f"Vision frame saved: {path}"), 0)
            except Exception as exc:  # noqa: BLE001
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
        Builder.load_file(str(KV_PATH))
        Builder.load_string(KV)
        return AssistantRoot()
