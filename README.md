# JANE Web Assistant

A sleek Jarvis-like assistant named **JANE**, accessible from a browser-based control panel.

**Name:** JANE  
**Deployed By:** Visrodeck Technology  
**Track:** Stable web-enabled build

## What’s New (Web Access)

- Browser dashboard UI/UX (glassmorphism + responsive layout)
- Voice command capture in browser (Web Speech API)
- Built-in Python web server backend (no FastAPI install required)
- High-risk command queue with **explicit per-command grant/deny**
- Log viewer + pending queue panel
- Optional Gemini chat integration via environment variable

## Security Note

Never hardcode API secrets.

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

Then open:

- `http://localhost:8000`

## Example Commands

- `open chrome and open whatsapp`
- `open settings and change theme`
- `open terminal and download this library requests`
- `shut down the system`

High-risk actions are never executed immediately. They are queued and require clicking:

- ✅ Grant High Risk
- ❌ Deny High Risk

## Architecture

- `jane/commands.py` → NLP intent parsing
- `jane/actions.py` → cross-platform action execution
- `jane_web/server.py` → built-in Python HTTP backend + state/queue
- `jane_web/templates/index.html` → dashboard markup
- `jane_web/static/style.css` → modern UI styling
- `jane_web/static/app.js` → frontend logic + API calls
