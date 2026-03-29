"""
Video Text Grabber — Free Edition
----------------------------------
Author  : Hasnain  (https://github.com/Hasnaintnt)
License : MIT

Press Ctrl+Shift+G while any video is paused.
Takes a screenshot, runs Tesseract OCR locally, copies text to clipboard.

100% free. No API. No internet needed. Runs offline.

Requirements:
  pip install pillow pytesseract pyperclip pystray keyboard

Also install Tesseract engine:
  Windows : https://github.com/UB-Mannheim/tesseract/wiki  (download installer)
  macOS   : brew install tesseract
  Linux   : sudo apt install tesseract-ocr
"""

import os
import sys
import time
import threading
import signal
import json
import io
from pathlib import Path
from datetime import datetime

try:
    import keyboard
    HAS_KEYBOARD = True
except ImportError:
    HAS_KEYBOARD = False

try:
    import pyperclip
    HAS_CLIPBOARD = True
except ImportError:
    HAS_CLIPBOARD = False

try:
    from PIL import Image, ImageGrab, ImageFilter, ImageEnhance
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import pytesseract
    HAS_TESSERACT = True
except ImportError:
    HAS_TESSERACT = False

try:
    import pystray
    from pystray import MenuItem as Item
    HAS_TRAY = True
except ImportError:
    HAS_TRAY = False

# ── config ──────────────────────────────────────────────────────────────────
CONFIG_PATH = Path.home() / ".video_text_grabber" / "config.json"
LOG_PATH    = Path.home() / ".video_text_grabber" / "history.log"

DEFAULT_CONFIG = {
    "hotkey": "ctrl+shift+g",
    "auto_copy": True,
    "save_log": True,
    "notify": True,
    "lang": "eng",           # tesseract language, e.g. "eng", "ara", "fra"
    "tesseract_cmd": "",     # leave blank for auto-detect, or set full path
}

def load_config():
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH) as f:
                return {**DEFAULT_CONFIG, **json.load(f)}
        except Exception:
            pass
    save_config(DEFAULT_CONFIG)
    return dict(DEFAULT_CONFIG)

def save_config(cfg):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)

# ── notification ─────────────────────────────────────────────────────────────
def notify(title, message):
    if sys.platform == "darwin":
        os.system(f'osascript -e \'display notification "{message}" with title "{title}"\'')
    elif sys.platform == "win32":
        try:
            from win10toast import ToastNotifier
            ToastNotifier().show_toast(title, message, duration=3, threaded=True)
        except Exception:
            pass
    else:
        os.system(f'notify-send "{title}" "{message}" 2>/dev/null || true')

# ── screenshot ────────────────────────────────────────────────────────────────
def take_screenshot() -> Image.Image:
    if sys.platform == "linux":
        tmp = Path("/tmp/_vtg_shot.png")
        ret = os.system(f"scrot {tmp} 2>/dev/null")
        if ret == 0 and tmp.exists():
            return Image.open(tmp).copy()
    return ImageGrab.grab()

# ── image pre-processing (helps Tesseract accuracy) ──────────────────────────
def preprocess(img: Image.Image) -> Image.Image:
    # Convert to grayscale
    img = img.convert("L")
    # Sharpen
    img = img.filter(ImageFilter.SHARPEN)
    # Boost contrast
    img = ImageEnhance.Contrast(img).enhance(2.0)
    # Scale up if small (tesseract works better on larger images)
    w, h = img.size
    if w < 1920:
        scale = 1920 / w
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    return img

# ── OCR ───────────────────────────────────────────────────────────────────────
def extract_text(img: Image.Image, cfg: dict) -> str:
    # Set tesseract path if specified
    cmd = cfg.get("tesseract_cmd", "").strip()
    if cmd:
        pytesseract.pytesseract.tesseract_cmd = cmd
    elif sys.platform == "win32":
        # Common default Windows install path
        default = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        if os.path.exists(default):
            pytesseract.pytesseract.tesseract_cmd = default

    lang = cfg.get("lang", "eng")
    processed = preprocess(img)

    # PSM 3 = fully automatic page segmentation (good for mixed screen content)
    text = pytesseract.image_to_string(processed, lang=lang, config="--psm 3")
    return text.strip()

# ── log ────────────────────────────────────────────────────────────────────────
def append_log(text: str):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"\n[{ts}]\n{text}\n{'─'*60}\n")

# ── core action ────────────────────────────────────────────────────────────────
_busy = False

def do_grab(cfg: dict):
    global _busy
    if _busy:
        return
    _busy = True
    try:
        if cfg.get("notify"):
            notify("Video Text Grabber", "📸 Reading screen…")

        img  = take_screenshot()
        text = extract_text(img, cfg)

        if not text:
            if cfg.get("notify"):
                notify("Video Text Grabber", "No text found on screen.")
            return

        if cfg.get("auto_copy") and HAS_CLIPBOARD:
            pyperclip.copy(text)

        if cfg.get("save_log"):
            append_log(text)

        if cfg.get("notify"):
            preview = text[:80].replace("\n", " ")
            if len(text) > 80:
                preview += "…"
            notify("Video Text Grabber", f"Copied: {preview}")

        print(f"\n── Extracted ──\n{text}\n──────────────")

    except Exception as e:
        notify("Video Text Grabber", f"Error: {e}")
        print(f"Error: {e}", file=sys.stderr)
    finally:
        _busy = False

# ── tray ───────────────────────────────────────────────────────────────────────
def make_tray_icon(cfg_ref: list):
    def on_grab(icon, item):
        threading.Thread(target=do_grab, args=(cfg_ref[0],), daemon=True).start()

    def on_open_log(icon, item):
        if LOG_PATH.exists():
            if sys.platform == "win32":
                os.startfile(LOG_PATH)
            elif sys.platform == "darwin":
                os.system(f"open '{LOG_PATH}'")
            else:
                os.system(f"xdg-open '{LOG_PATH}' 2>/dev/null &")

    def on_open_config(icon, item):
        if sys.platform == "win32":
            os.startfile(CONFIG_PATH)
        elif sys.platform == "darwin":
            os.system(f"open '{CONFIG_PATH}'")
        else:
            os.system(f"xdg-open '{CONFIG_PATH}' 2>/dev/null &")

    def on_reload(icon, item):
        cfg_ref[0] = load_config()
        notify("Video Text Grabber", "Config reloaded.")

    def on_quit(icon, item):
        icon.stop()
        os._exit(0)

    hotkey = cfg_ref[0].get("hotkey", DEFAULT_CONFIG["hotkey"]).upper()

    menu = pystray.Menu(
        Item(f"Grab Text  ({hotkey})", on_grab, default=True),
        pystray.Menu.SEPARATOR,
        Item("Open Log",      on_open_log),
        Item("Edit Config",   on_open_config),
        Item("Reload Config", on_reload),
        pystray.Menu.SEPARATOR,
        Item("Quit", on_quit),
    )

    from PIL import ImageDraw
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([4, 4, 60, 60], fill=(60, 180, 255, 255))
    draw.text((20, 18), "T", fill=(10, 10, 10, 255))

    return pystray.Icon("VideoTextGrabber", img, "Video Text Grabber", menu)

# ── main ───────────────────────────────────────────────────────────────────────
def main():
    missing = []
    if not HAS_PIL:       missing.append("pillow")
    if not HAS_TESSERACT: missing.append("pytesseract")
    if not HAS_CLIPBOARD: missing.append("pyperclip")
    if not HAS_KEYBOARD:  missing.append("keyboard")
    if not HAS_TRAY:      missing.append("pystray")

    if missing:
        print("Missing dependencies. Run:")
        print(f"  pip install {' '.join(missing)}")
        sys.exit(1)

    cfg     = load_config()
    cfg_ref = [cfg]

    hotkey = cfg.get("hotkey", DEFAULT_CONFIG["hotkey"])
    keyboard.add_hotkey(hotkey, lambda: threading.Thread(
        target=do_grab, args=(cfg_ref[0],), daemon=True).start())

    print("Video Text Grabber (Free / Tesseract)")
    print(f"Hotkey : {hotkey.upper()}")
    print(f"Config : {CONFIG_PATH}")
    print(f"Log    : {LOG_PATH}")
    print("Running — press Ctrl+C to quit.\n")

    if HAS_TRAY:
        icon = make_tray_icon(cfg_ref)
        icon.run()
    else:
        signal.signal(signal.SIGINT, lambda *_: sys.exit(0))
        while True:
            time.sleep(1)

if __name__ == "__main__":
    main()
