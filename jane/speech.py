from __future__ import annotations

import threading

import pyttsx3
import speech_recognition as sr


class SpeechEngine:
    def __init__(self) -> None:
        self.recognizer = sr.Recognizer()
        self.tts = pyttsx3.init()
        self._speak_lock = threading.Lock()

    def listen_once(self, timeout: int = 5, phrase_time_limit: int = 8) -> str:
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.4)
            audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        return self.recognizer.recognize_google(audio)

    def speak(self, text: str) -> None:
        with self._speak_lock:
            self.tts.say(text)
            self.tts.runAndWait()
