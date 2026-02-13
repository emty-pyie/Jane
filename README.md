# JANE Desktop Assistant

JANE is a **desktop-first**, production-style AI assistant built with **Python + Kivy**.

**Name:** JANE  
**Deployed By:** Visrodeck Technology  
**Track:** Stable desktop software

## Professional Feature Set

- Premium control-center style desktop UI
- Voice input (speech-to-text) with wake word: **Hey Jane**
- Voice input (speech-to-text)
- Text-to-speech responses
- Command parsing and smart intent routing
- High-risk command queue with explicit grant/deny gate
- Security popup appears for dangerous commands (approve once / deny)
- Admin-elevation compatible execution path for privileged tasks
- Quick actions panel (time, calculator, WhatsApp, note capture)
- Computer vision test capture
- Notes persistence to local file (`jane_notes.txt`)
- Console export (`jane_console_log.txt`)
- Optional Gemini chat integration through `GEMINI_API_KEY` (also accepts `GEMENI_API_KEY` / `GOOGLE_API_KEY`)
- Optional Gemini chat integration through `GEMINI_API_KEY`

## Security

Never hardcode credentials in code.

```bash
export GEMINI_API_KEY="your_key_here"
# fallback names also supported: GEMENI_API_KEY or GOOGLE_API_KEY
```

## Run (Windows - recommended)

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
python main.py
```

## Run (Linux/macOS)
```

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
python main.py
```

## Fix: `ModuleNotFoundError: No module named 'kivy'`

If you see this error, it means dependencies were not installed in the active environment.

1. Activate your project venv.
2. Upgrade pip tools.
3. Install requirements.
4. If needed, install Kivy directly:

```bash
pip install kivy
```

## Admin / Privileged Actions

JANE can request elevated rights for privileged tasks (installs, shutdown, certain system actions).
You still must explicitly approve high-risk actions from the popup before execution.

## Example Commands

- `open chrome and open whatsapp`
- `open settings and change theme`
- `open terminal and download this library requests`
- `shut down the system`
- `what time is it`
- `today date`
- `open calculator`
- `note: buy milk tomorrow`

## Structure

- `main.py` → app entrypoint
- `jane/app.py` → professional UI + orchestration
- `jane/commands.py` → intent parsing
- `jane/actions.py` → action execution layer
- `jane/speech.py` → STT/TTS
- `jane/vision.py` → camera capture


## Example Voice Usage

- Say: `Hey Jane what time is it`
- Say: `Hey Jane open calculator`
- Without wake word, voice input is ignored for safety and noise filtering.


## Fix: `IndentationError: unexpected indent`

If you see this on startup, one Python file is malformed (often from manual copy/paste).

1. Re-copy a clean version of the project files (especially `jane/commands.py`).
2. Run syntax check:

```bash
python -m py_compile main.py jane/*.py
```

3. Start again:

```bash
python main.py
```
