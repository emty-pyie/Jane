from __future__ import annotations

import sys


def _print_kivy_install_help() -> None:
    print("[JANE] Missing dependency: kivy")
    print("Install dependencies first, then run again.")
    print("\nWindows (PowerShell):")
    print("  py -3.11 -m venv .venv")
    print("  .venv\\Scripts\\Activate.ps1")
    print("  python -m pip install --upgrade pip setuptools wheel")
    print("  pip install -r requirements.txt")
    print("  python main.py")
    print("\nIf Kivy still fails, install it directly:")
    print("  pip install kivy")


if __name__ == "__main__":
    try:
        from jane.app import JaneApp
    except ModuleNotFoundError as exc:
        if exc.name == "kivy" or str(exc).startswith("No module named 'kivy'"):
            _print_kivy_install_help()
            sys.exit(1)
        raise

    JaneApp().run()
from jane.app import JaneApp


if __name__ == "__main__":
    JaneApp().run()
from jane_web.server import run_server


if __name__ == "__main__":
    run_server(host="0.0.0.0", port=8000)
