# 🎬 Video Text Grabber

> Pause any video on your PC → press a hotkey → text is copied to your clipboard instantly.

Works with **any** video player — VLC, browser, Netflix, YouTube, anything on your screen.
Powered by [Tesseract OCR](https://github.com/tesseract-ocr/tesseract). **100% free. No API. No internet. Runs fully offline.**

---

## ✨ Features

- ⌨️ Global hotkey — works while any app is in focus
- 📋 Auto-copies extracted text to clipboard
- 🖼️ Grabs subtitles, on-screen labels, signs, slides — everything visible
- 🗂️ Saves a log of every extraction to `~/.video_text_grabber/history.log`
- 🔔 Desktop notification confirms what was found
- ⚙️ Simple JSON config — change hotkey, language, and more
- 🖥️ System tray icon with quick-access menu
- 🌐 Multi-language support (Arabic, French, German, and more)

---

## 🚀 Installation

### Step 1 — Install Tesseract OCR engine

| Platform | Command |
|----------|---------|
| **Windows** | Download installer → [github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki) |
| **macOS** | `brew install tesseract` |
| **Linux** | `sudo apt install tesseract-ocr` |

### Step 2 — Install Python dependencies

```bash
pip install pillow pytesseract pyperclip pystray keyboard
```

### Step 3 — Run

```bash
python grabber_free.py
```

A green dot will appear in your system tray — the app is running.

---

## 🎯 Usage

1. Open any video in any player and **pause it**
2. Press **`Ctrl + Shift + G`**
3. Wait ~1–2 seconds for OCR to finish
4. Text is in your clipboard — **paste anywhere with `Ctrl + V`**

---

## ⚙️ Configuration

Config file is auto-created on first run at:

```
~/.video_text_grabber/config.json
```

```json
{
  "hotkey": "ctrl+shift+g",
  "auto_copy": true,
  "save_log": true,
  "notify": true,
  "lang": "eng",
  "tesseract_cmd": ""
}
```

| Key | Description |
|-----|-------------|
| `hotkey` | Key combination to trigger grab |
| `auto_copy` | Auto-copy result to clipboard |
| `save_log` | Save all extractions to history log |
| `notify` | Show desktop notification |
| `lang` | Tesseract language code (`eng`, `ara`, `fra`, etc.) |
| `tesseract_cmd` | Full path to tesseract binary (leave blank for auto-detect) |

After editing, click **Reload Config** in the tray menu — no restart needed.

---

## 🌍 Multiple Languages

Install extra language packs then update `lang` in config:

```bash
# Arabic
sudo apt install tesseract-ocr-ara   →  "lang": "ara"

# French
sudo apt install tesseract-ocr-fra   →  "lang": "fra"

# Multiple at once
"lang": "eng+ara"
```

---

## 🖥️ Tray Menu

Right-click the tray icon for:

| Option | Action |
|--------|--------|
| Grab Text | Same as hotkey |
| Open Log | View extraction history |
| Edit Config | Open config file |
| Reload Config | Pick up config changes |
| Quit | Exit the app |

---

## 📋 Requirements

- Python 3.8+
- Tesseract OCR (system install)
- pip packages: `pillow pytesseract pyperclip pystray keyboard`

### Platform notes

| Platform | Notes |
|----------|-------|
| Windows | Works out of the box after Tesseract install |
| macOS | May need Accessibility permission — System Preferences → Security → Accessibility |
| Linux | Install `xclip` for clipboard: `sudo apt install xclip` |

---

## 📁 File Structure

```
video-text-grabber/
├── grabber_free.py   # main app
├── install_free.py   # one-command installer
└── README.md
```

---

## 👤 Author

**Hasnain** — [@Hasnaintnt](https://github.com/Hasnaintnt)

---

## 📄 License

MIT — free to use, modify, and distribute.
