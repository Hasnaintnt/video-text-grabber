#!/usr/bin/env python3
"""
install_free.py — setup for Video Text Grabber (Free / Tesseract edition)
"""
import sys, os, subprocess, json, shutil
from pathlib import Path

DEPS       = ["pillow", "pytesseract", "pyperclip", "pystray", "keyboard"]
CONFIG_PATH = Path.home() / ".video_text_grabber" / "config.json"
SCRIPT_DIR  = Path(__file__).parent.resolve()
MAIN_SCRIPT = SCRIPT_DIR / "grabber_free.py"

BANNER = """
╔══════════════════════════════════════════════╗
║   Video Text Grabber — Free Edition Setup    ║
║   Powered by Tesseract OCR (100% offline)    ║
╚══════════════════════════════════════════════╝
"""

def run(cmd, **kw):
    return subprocess.run(cmd, **kw)

def check_tesseract():
    if shutil.which("tesseract"):
        print("✓ Tesseract found.")
        return True
    print("\n⚠  Tesseract OCR engine not found.")
    if sys.platform == "win32":
        print("   Download and install it from:")
        print("   https://github.com/UB-Mannheim/tesseract/wiki")
        print("   Then re-run this installer.\n")
    elif sys.platform == "darwin":
        print("   Install with:  brew install tesseract\n")
    else:
        print("   Install with:  sudo apt install tesseract-ocr\n")
    return False

def install_deps():
    print("Installing Python packages…")
    run([sys.executable, "-m", "pip", "install", "--upgrade", *DEPS], check=True)
    if sys.platform == "win32":
        run([sys.executable, "-m", "pip", "install", "win10toast"])

def setup_config():
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if CONFIG_PATH.exists():
        print(f"Config already exists at {CONFIG_PATH}")
        return

    hotkey = input("\nHotkey [default: ctrl+shift+g]: ").strip() or "ctrl+shift+g"
    lang   = input("Language code [default: eng]: ").strip() or "eng"
    print("  (other examples: ara=Arabic, fra=French, deu=German)")
    print("  Install extra languages: sudo apt install tesseract-ocr-ara")

    config = {
        "hotkey": hotkey,
        "auto_copy": True,
        "save_log": True,
        "notify": True,
        "lang": lang,
        "tesseract_cmd": "",
    }
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)
    print(f"\nConfig saved → {CONFIG_PATH}")

def create_launcher():
    if sys.platform == "win32":
        vbs = SCRIPT_DIR / "VideoTextGrabber.vbs"
        bat = SCRIPT_DIR / "VideoTextGrabber.bat"
        bat.write_text(f'@echo off\n"{sys.executable}" "{MAIN_SCRIPT}"\n')
        vbs.write_text(
            f'Set WshShell = CreateObject("WScript.Shell")\n'
            f'WshShell.Run chr(34) & "{bat}" & chr(34), 0\n'
            f'Set WshShell = Nothing\n'
        )
        ans = input("\nCreate desktop shortcut? [Y/n]: ").strip().lower()
        if ans != "n":
            desktop = Path.home() / "Desktop"
            if desktop.exists():
                import shutil as sh
                sh.copy(vbs, desktop / "VideoTextGrabber.vbs")
                print("Shortcut created on Desktop.")
        print(f"\nTo start: double-click VideoTextGrabber.vbs")

    elif sys.platform == "darwin":
        plist_dir  = Path.home() / "Library" / "LaunchAgents"
        plist_path = plist_dir / "com.videotextgrabber.plist"
        plist_dir.mkdir(parents=True, exist_ok=True)
        plist_path.write_text(f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
    <key>Label</key><string>com.videotextgrabber</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable}</string>
        <string>{MAIN_SCRIPT}</string>
    </array>
    <key>RunAtLoad</key><true/>
</dict></plist>""")
        run(["launchctl", "load", str(plist_path)])
        print(f"\nLaunchAgent installed — starts on login.")

    else:
        autostart = Path.home() / ".config" / "autostart"
        autostart.mkdir(parents=True, exist_ok=True)
        (autostart / "video-text-grabber.desktop").write_text(
            f"[Desktop Entry]\nType=Application\nName=Video Text Grabber\n"
            f"Exec={sys.executable} {MAIN_SCRIPT}\nX-GNOME-Autostart-enabled=true\n"
        )
        print(f"\nAutostart entry created.")
        print(f"Start now with:  python3 {MAIN_SCRIPT} &")

def main():
    print(BANNER)
    tess_ok = check_tesseract()
    install_deps()
    setup_config()
    if tess_ok:
        create_launcher()
    print("\n✓ Done!")
    print("─────────────────────────────────────────")
    print("1. Pause any video on your screen")
    print("2. Press your hotkey (default: Ctrl+Shift+G)")
    print("3. Text is copied to clipboard — paste anywhere")
    print("─────────────────────────────────────────\n")

if __name__ == "__main__":
    main()
