"""
Generator aset untuk JSON Watchface.

Membuat background (bagian statis kode JSON), gambar digit, nama hari,
nama bulan, preview, dan icon dari font monospace. Semua ukuran dan
posisi slot dihitung otomatis, lalu disimpan ke layout.json supaya
watchface/index.js bisa disesuaikan.

Pemakaian:
    pip install pillow
    python tools/generate_assets.py --font path/ke/JetBrainsMono-Medium.ttf

Opsi lain: --width, --height, --radius, --theme, --out
"""
import argparse
import json
import os

from PIL import Image, ImageDraw, ImageFont

THEMES = {
    # warna ala VS Code Dark+
    "vscode": {
        "bg": (0, 0, 0), "tab_bg": (30, 30, 30), "tab_text": (220, 220, 220),
        "key": (156, 220, 254), "string": (206, 145, 120),
        "punct": (212, 212, 212), "line_no": (110, 118, 129),
    },
    "dracula": {
        "bg": (0, 0, 0), "tab_bg": (33, 34, 44), "tab_text": (248, 248, 242),
        "key": (139, 233, 253), "string": (241, 250, 140),
        "punct": (248, 248, 242), "line_no": (98, 114, 164),
    },
    "monokai": {
        "bg": (0, 0, 0), "tab_bg": (39, 40, 34), "tab_text": (248, 248, 242),
        "key": (102, 217, 239), "string": (230, 219, 116),
        "punct": (248, 248, 242), "line_no": (117, 113, 94),
    },
}

WEEK = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]  # Zepp OS: index 0 = Senin
MONTH = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
         "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def build_lines():
    """Setiap baris = daftar segmen (teks, peran). 'VAL:nama:panjang' = slot angka live."""
    return [
        [("{", "punct")],
        [("  ", "punct"), ('"time"', "key"), (':"', "punct"),
         ("VAL:hour:2", None), (":", "string"), ("VAL:minute:2", None),
         (":", "string"), ("VAL:second:2", None), ('",', "punct")],
        [("  ", "punct"), ('"date"', "key"), (':"', "punct"),
         ("VAL:week:3", None), (", ", "punct"), ("VAL:month:3", None),
         (" ", "punct"), ("VAL:day:2", None), ('",', "punct")],
        [("  ", "punct"), ('"stats"', "key"), (":{", "punct")],
        [("    ", "punct"), ('"steps"', "key"), (':"', "punct"),
         ("VAL:steps:5", None), ('",', "punct")],
        [("    ", "punct"), ('"heart"', "key"), (':"', "punct"),
         ("VAL:heart:3", None), ('",', "punct")],
        [("  ", "punct"), ("},", "punct")],
        [("  ", "punct"), ('"battery"', "key"), (':"', "punct"),
         ("VAL:battery:3", None), ('",', "punct")],
        [("}", "punct")],
    ]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--font", required=True, help="path font monospace (.ttf)")
    ap.add_argument("--width", type=int, default=390)
    ap.add_argument("--height", type=int, default=450)
    ap.add_argument("--radius", type=int, default=86, help="radius sudut layar (untuk preview)")
    ap.add_argument("--font-size", type=int, default=22)
    ap.add_argument("--line-height", type=int, default=37)
    ap.add_argument("--theme", choices=THEMES.keys(), default="vscode")
    ap.add_argument("--out", default="assets/bip-6")
    ap.add_argument("--layout", default="tools/layout.json")
    a = ap.parse_args()

    W, H, T = a.width, a.height, THEMES[a.theme]
    font = ImageFont.truetype(a.font, a.font_size)
    tab_font = ImageFont.truetype(a.font, round(a.font_size * 0.82))
    cw = font.getlength("0")
    asc, desc = font.getmetrics()
    cell_h = asc + desc

    tab_h = round(H * 0.12)
    top = tab_h + 26
    gutter_x = 22
    code_x = gutter_x + round(cw) + 14

    def col_x(col):
        return code_x + round(col * cw)

    def line_y(n):
        return top + (n - 1) * a.line_height

    for sub in ("digits", "week", "month"):
        os.makedirs(os.path.join(a.out, sub), exist_ok=True)

    # --- background ---
    bg = Image.new("RGB", (W, H), T["bg"])
    d = ImageDraw.Draw(bg)
    d.rectangle([0, 0, W, tab_h], fill=T["tab_bg"])
    label = "watchface.json ×"
    tx = 48
    tw = int(tab_font.getlength(label)) + 32
    d.rectangle([tx, 12, tx + tw, tab_h], fill=T["bg"])
    d.text((tx + 16, tab_h - 10), label, font=tab_font, fill=T["tab_text"], anchor="ls")

    slots = {}
    for i, segs in enumerate(build_lines(), 1):
        y = line_y(i)
        n = str(i)
        d.text((gutter_x + round(cw) - font.getlength(n), y), n, font=font, fill=T["line_no"])
        col = 0
        for text, role in segs:
            if text.startswith("VAL:"):
                _, name, length = text.split(":")
                length = int(length)
                slots[name] = {"x": col_x(col), "y": y, "w": round(length * cw), "h": cell_h}
                col += length
            else:
                d.text((col_x(col), y), text, font=font, fill=T[role])
                col += len(text)
    bg.save(os.path.join(a.out, "background.png"))

    # --- glyph (teks warna string, background transparan) ---
    def glyph(text, path):
        im = Image.new("RGBA", (round(cw * len(text)), cell_h), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((0, 0), text, font=font, fill=T["string"] + (255,))
        im.save(path)

    for k in range(10):
        glyph(str(k), os.path.join(a.out, "digits", f"{k}.png"))
    for i, w in enumerate(WEEK):
        glyph(w, os.path.join(a.out, "week", f"{i}.png"))
    for i, m in enumerate(MONTH):
        glyph(m, os.path.join(a.out, "month", f"{i}.png"))

    # --- preview & icon ---
    pv = bg.convert("RGBA")
    pd = ImageDraw.Draw(pv)
    sample = {"hour": "10", "minute": "10", "second": "00",
              "week": "Sun", "month": "Jan", "day": "28"}
    for k, v in sample.items():
        pd.text((slots[k]["x"], slots[k]["y"]), v, font=font, fill=T["string"])
    for k, v in {"steps": "7645", "heart": "68", "battery": "80"}.items():
        s = slots[k]
        pd.text((s["x"] + (s["w"] - font.getlength(v)) / 2, s["y"]), v, font=font, fill=T["string"])
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, W - 1, H - 1], radius=a.radius, fill=255)
    full = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    full.paste(pv, (0, 0), mask)
    full.resize((266, round(266 * H / W)), Image.LANCZOS).save(os.path.join(a.out, "preview.png"))

    icon = Image.new("RGBA", (248, 248), T["bg"] + (255,))
    ImageDraw.Draw(icon).text((124, 124), "{ }", font=ImageFont.truetype(a.font, 110),
                              fill=T["key"] + (255,), anchor="mm")
    icon.save(os.path.join(a.out, "icon.png"))

    # layout.json disimpan di luar folder assets supaya tidak ikut ter-bundle ke jam
    with open(a.layout, "w") as f:
        json.dump({"screen": [W, H], "theme": a.theme, "slots": slots}, f, indent=2)

    print(f"Aset dibuat di {a.out}")
    for k, s in slots.items():
        print(f"  {k:8s} x={s['x']:3d} y={s['y']:3d} w={s['w']}")


if __name__ == "__main__":
    main()
