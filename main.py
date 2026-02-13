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


def _print_syntax_help(exc: SyntaxError) -> None:
    print("[JANE] Python syntax error while loading project files.")
    print(f"{exc.__class__.__name__}: {exc.msg}")
    if exc.filename and exc.lineno:
        print(f"File: {exc.filename}:{exc.lineno}")
    print("This usually means one source file was edited with broken indentation.")
    print("Please restore/update the project files and run again.")

if __name__ == "__main__":
    try:
        from jane.app import JaneApp
    except ModuleNotFoundError as exc:
        if exc.name == "kivy" or str(exc).startswith("No module named 'kivy'"):
            _print_kivy_install_help()
            sys.exit(1)
        raise
    except SyntaxError as exc:
        _print_syntax_help(exc)
        sys.exit(1)

    JaneApp().run()
