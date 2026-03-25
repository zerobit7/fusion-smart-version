# SmartVersion — Fusion 360 Add-In

**Automatic version tracking for Fusion 360 designs.**  
Every time you save, `version` increments by one — so you can embed the version number directly in your model and have it printed on the physical part.

[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20me%20a%20coffee-%E2%98%95-yellow)](https://buymeacoffee.com/zerobit7)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## What it does

- **Auto-increment on save** — `version` goes from 3 to 4 every time you hit Ctrl+S
- **Embeddable in your sketch** — reference `version` in a Fusion 360 text, extrude it, and the version number is physically on your part
- **Reset command** — start fresh from 1 whenever you need to

No cloud, no subscription, no fuss.

---

## Installation

1. Download or clone this repository
2. Copy the `SmartVersion` folder into:
   ```
   %appdata%\Autodesk\Autodesk Fusion 360\API\AddIns\
   ```
   On macOS:
   ```
   ~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/
   ```
3. In Fusion 360: **Utilities → Add-Ins → Scripts and Add-Ins**
4. Select `SmartVersion` → click **Run**
5. Optionally enable **Run on Startup** so it loads automatically

---

## Usage

### Version number in your model

1. Create a sketch on any face of your model
2. Insert a **Text** element
3. Type `version` as the text content — Fusion resolves it to the current value (e.g. `3`)
4. If you want to display it as `v3`, concatenate: `'v' + version`
5. Extrude or engrave — done

Every time you save, the number updates automatically.

### Reset version

**Utilities → Add-Ins → Reset Version to 1**

A confirmation dialog will appear before anything is changed. After resetting, save the file to confirm.

---

## How it works

SmartVersion hooks into Fusion's `documentSaving` event and updates a user parameter called `version` before each save. This ensures the version number embedded in the file always matches what you see in the title bar.

The parameter is a plain unitless integer — you can reference it anywhere Fusion accepts parameter expressions.

---

## Requirements

- Autodesk Fusion 360 (any recent version)
- Python API enabled (default in all installations)

---

## License

MIT — do whatever you want with it.
