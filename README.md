# JANE Desktop Assistant

JANE is a desktop assistant built with **Python 3.11 + Kivy**.
It supports:

- Voice input (speech-to-text)
- Text-to-speech responses
- Command NLP parsing
- High-risk command approval workflow
- Basic computer-vision capture utility
- App/web opening automation

**Name:** JANE  
**Deployed By:** Visrodeck Technology

## Security Notice

For API keys (for example Gemini), **do not hardcode secrets in source code**.
Set them using environment variables:

```bash
export GEMINI_API_KEY="your_key_here"
```

JANE reads `GEMINI_API_KEY` at runtime.

## Quick Start

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Features

### Voice + NLP
- Click **🎤 Listen** to capture a voice command.
- Type commands manually in the input bar.

### High-Risk Command Grant
Commands that can change system state are queued for explicit approval every time:
- Shutdown/restart
- Arbitrary terminal command execution
- Theme changes / settings edits (mapped as high-risk action)

Use:
- **✅ Grant Selected** to approve
- **❌ Deny Selected** to reject

### Example Commands
- "open chrome and open whatsapp"
- "open settings and change theme"
- "open terminal and download this library requests"
- "shut down the system"

### Computer Vision
Use **📷 Capture Vision Frame** to test webcam integration.

## Project Structure

- `main.py` - app entry point
- `jane/app.py` - Kivy UI and orchestration
- `jane/commands.py` - command intent parsing
- `jane/actions.py` - action execution layer
- `jane/speech.py` - STT/TTS abstraction
- `jane/vision.py` - OpenCV helper

## Notes
- Some actions are platform dependent.
- On Linux, open-settings/theme change may vary by desktop environment.
- Shutdown command includes a countdown + spoken warning:
  **"System Black Out"**.
