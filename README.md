# JANE Desktop Assistant

JANE is a **desktop-first**, production-style AI assistant built with **Python + Kivy**.

**Name:** JANE  
**Deployed By:** Visrodeck Technology  
**Track:** Stable desktop software

## Professional Feature Set

- Premium control-center style desktop UI
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
- Optional Gemini chat integration through `GEMINI_API_KEY`

## Security

Never hardcode credentials in code.

```bash
export GEMINI_API_KEY="your_key_here"
```

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
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
