# JSON Watchface

<p align="center">
  <img src="https://img.shields.io/badge/Zepp_OS-watch_face-F57C00?style=flat-square" alt="Zepp OS watch face">
  <img src="https://img.shields.io/badge/Amazfit-Bip_6-1E88E5?style=flat-square" alt="Amazfit Bip 6">
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black" alt="JavaScript">
  <img src="https://img.shields.io/badge/Python-asset_generator-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python asset generator">
  <img src="https://img.shields.io/badge/iPhone_%26_Android-supported-555555?style=flat-square" alt="iPhone and Android supported">
  <img src="https://img.shields.io/badge/license-MIT-2E7D32?style=flat-square" alt="MIT license">
</p>

A watch face for **Amazfit Bip 6** (Zepp OS) that turns your wrist into a code editor. Your time, date and health stats live inside a `watchface.json` file, styled like VS Code.

<p align="center">
  <img src="docs/demo.gif" width="300" alt="JSON Watchface running in the Zepp OS simulator">
</p>

## Why JSON Watchface

- **Made for developers.** Line numbers, an editor tab, syntax colors and a monospace font. It looks like a file you'd have open at work, not a generic sport face.
- **Everything is live.** Time, weekday, date, steps, heart rate and battery update by themselves, right inside the string values.
- **Heart rate that keeps up.** The value refreshes while you're looking at the watch, so you don't need to switch faces to see a new reading.
- **Easy on the battery.** Pure black background for AMOLED, and background updates pause automatically when the screen is off.
- **Make it yours.** Every image is generated from a script. Switch themes, swap the font or resize for another watch in one command.
- **Works with iPhone and Android.** Installs through the official Zepp app with a QR code. No unofficial tools, no extra phone.

## Themes

Three color themes are included, and adding your own takes a few lines:

<p align="center">
  <img src="docs/themes.png" width="700" alt="vscode, dracula and monokai themes">
</p>

## Install

Requirements: [Node.js](https://nodejs.org) LTS and the Zeus CLI.

```bash
npm i @zeppos/zeus-cli -g
cd json-watchface
```

**On your watch**

1. Pair the Bip 6 with the Zepp app and enable **Developer Mode** (Profile → Settings → About, tap the Zepp logo repeatedly).
2. On your computer:
   ```bash
   zeus login
   zeus preview    # pick "bip-6", a QR code appears
   ```
3. In the Zepp app: Profile → Bip 6 → Developer Mode → scan icon → scan the QR → Install.

**In the simulator**

Install the [Zepp OS Simulator](https://docs.zepp.com/docs/guides/tools/simulator/), download the Bip 6 device, then run `zeus dev`. Long-press the screen and select **JSON Watchface**.

## Customize

```bash
pip install pillow
python tools/generate_assets.py --font path/to/JetBrainsMono-Medium.ttf --theme dracula
```

Options: `--theme {vscode,dracula,monokai}`, `--width`, `--height`, `--font-size`, `--line-height`, `--out`.

If you change the screen size or layout, the generator prints the new positions and saves them to `tools/layout.json`. Copy them into `SLOT` at the top of `watchface/index.js`.

JetBrains Mono is free at [jetbrains.com/lp/mono](https://www.jetbrains.com/lp/mono/).

## Project structure

```
json-watchface/
├── app.json                  # Zepp OS config (target: Amazfit Bip 6)
├── app.js
├── watchface/index.js        # watch face layout and live data
├── assets/bip-6/             # generated images
├── tools/
│   ├── generate_assets.py    # renders every image from a font
│   └── layout.json           # positions produced by the generator
└── docs/                     # README images
```

## License

Code: [MIT](LICENSE). Images in `assets/` are rendered from JetBrains Mono, licensed under the [SIL Open Font License 1.1](LICENSE-FONT.txt).
