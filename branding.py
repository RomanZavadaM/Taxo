# -*- coding: utf-8 -*-
"""Visual identity helpers for Taxo / Driver Worktime.

The artwork is intentionally text-free. Company naming stays dynamic and is
rendered separately from the icon/header so changing company details never
requires regenerating the brand image.
"""
from __future__ import annotations

import math
from pathlib import Path

PALETTE = {
    "navy": "#17395C",
    "blue": "#2F6B9A",
    "blue_dark": "#225275",
    "soft_blue": "#E8F0F7",
    "soft_blue_2": "#DCE8F2",
    "gold": "#D6A12A",
    "gold_soft": "#F4E6B8",
    "paper": "#F4F7FB",
    "panel": "#FFFFFF",
    "text": "#1F2D3A",
    "muted": "#66717D",
    "line": "#C8D4DF",
}


def apply_theme(root, ttk):
    """Apply a calm cross-platform office palette."""
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass

    root.configure(bg=PALETTE["paper"])
    style.configure(".", font=("TkDefaultFont", 10))
    style.configure("TFrame", background=PALETTE["paper"])
    style.configure("TLabel", background=PALETTE["paper"], foreground=PALETTE["text"])
    style.configure(
        "TLabelframe",
        background=PALETTE["paper"],
        bordercolor=PALETTE["line"],
        relief="solid",
    )
    style.configure(
        "TLabelframe.Label",
        background=PALETTE["paper"],
        foreground=PALETTE["navy"],
        font=("TkDefaultFont", 10, "bold"),
    )
    style.configure(
        "TButton",
        padding=(9, 5),
        background=PALETTE["soft_blue"],
        foreground=PALETTE["navy"],
        bordercolor=PALETTE["line"],
    )
    style.map(
        "TButton",
        background=[("active", PALETTE["soft_blue_2"]), ("pressed", PALETTE["soft_blue_2"])],
    )
    style.configure(
        "Accent.TButton",
        background=PALETTE["gold"],
        foreground=PALETTE["navy"],
        font=("TkDefaultFont", 10, "bold"),
    )
    style.map(
        "Accent.TButton",
        background=[("active", "#E2B53D"), ("pressed", "#C9931F")],
    )
    style.configure(
        "Treeview",
        background=PALETTE["panel"],
        fieldbackground=PALETTE["panel"],
        foreground=PALETTE["text"],
        rowheight=26,
        bordercolor=PALETTE["line"],
    )
    style.configure(
        "Treeview.Heading",
        background=PALETTE["soft_blue"],
        foreground=PALETTE["navy"],
        font=("TkDefaultFont", 10, "bold"),
        relief="flat",
    )
    style.map(
        "Treeview",
        background=[("selected", PALETTE["blue"])],
        foreground=[("selected", "#FFFFFF")],
    )
    style.configure("TNotebook", background=PALETTE["paper"], borderwidth=0)
    style.configure(
        "TNotebook.Tab",
        padding=(12, 7),
        background=PALETTE["soft_blue"],
        foreground=PALETTE["navy"],
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", PALETTE["panel"]), ("active", PALETTE["soft_blue_2"])],
        foreground=[("selected", PALETTE["blue_dark"])],
    )
    return style


def _draw_bus(draw, x, y, w, h, *, body="#F7FAFC", window="#2F6B9A", outline="#17395C"):
    r = max(4, int(h * 0.09))
    draw.rounded_rectangle((x, y, x + w, y + h), radius=r, fill=body, outline=outline, width=max(2, w // 48))
    pad = int(w * 0.09)
    top = y + int(h * 0.13)
    bottom = y + int(h * 0.53)
    gap = max(2, int(w * 0.025))
    total = w - pad * 2
    window_w = (total - gap * 3) // 4
    for i in range(4):
        wx = x + pad + i * (window_w + gap)
        draw.rectangle((wx, top, wx + window_w, bottom), fill=window)
    bumper_y = y + int(h * 0.72)
    draw.rectangle((x + pad, bumper_y, x + w - pad, bumper_y + max(2, h // 20)), fill=outline)
    wheel_r = max(3, int(h * 0.11))
    for cx in (x + int(w * 0.22), x + int(w * 0.78)):
        draw.ellipse((cx - wheel_r, y + h - wheel_r, cx + wheel_r, y + h + wheel_r), fill=outline)


def create_brand_image(size=512):
    """Create a text-free sun + bus mark based on the approved reference."""
    from PIL import Image, ImageDraw

    size = int(size)
    image = Image.new("RGBA", (size, size), PALETTE["navy"])
    draw = ImageDraw.Draw(image)
    cx, cy = size * 0.5, size * 0.43
    sun_r = size * 0.19
    for angle in range(0, 360, 22):
        rad = math.radians(angle)
        inner = sun_r * 1.18
        outer = sun_r * 1.66
        x1 = cx + math.cos(rad) * inner
        y1 = cy + math.sin(rad) * inner
        x2 = cx + math.cos(rad) * outer
        y2 = cy + math.sin(rad) * outer
        draw.line((x1, y1, x2, y2), fill=PALETTE["gold"], width=max(4, size // 42))
    draw.ellipse((cx - sun_r, cy - sun_r, cx + sun_r, cy + sun_r), fill=PALETTE["gold"])

    bus_w = int(size * 0.47)
    bus_h = int(size * 0.25)
    bus_x = int(cx - bus_w / 2)
    bus_y = int(cy - bus_h * 0.36)
    _draw_bus(draw, bus_x, bus_y, bus_w, bus_h)
    return image


def install_runtime_icon(root):
    """Set a generated application icon without any embedded company name."""
    from PIL import ImageTk

    photo = ImageTk.PhotoImage(create_brand_image(96), master=root)
    root.iconphoto(True, photo)
    root._taxo_brand_icon = photo
    return photo


def draw_brand_header(canvas, company_name="", app_label="Taxo / Driver Worktime"):
    """Render a compact banner. The company name is always dynamic text."""
    width = max(640, int(canvas.winfo_width() or 640))
    height = max(86, int(canvas.winfo_height() or 86))
    canvas.delete("all")
    canvas.configure(bg=PALETTE["navy"], highlightthickness=0)

    cx, cy = 82, height // 2
    for angle in range(0, 360, 30):
        rad = math.radians(angle)
        r1, r2 = 27, 39
        canvas.create_line(
            cx + math.cos(rad) * r1,
            cy + math.sin(rad) * r1,
            cx + math.cos(rad) * r2,
            cy + math.sin(rad) * r2,
            fill=PALETTE["gold"],
            width=4,
            capstyle="round",
        )
    canvas.create_oval(cx - 24, cy - 24, cx + 24, cy + 24, fill=PALETTE["gold"], outline="")
    bx, by, bw, bh = 48, cy - 13, 68, 34
    canvas.create_rectangle(bx, by, bx + bw, by + bh, fill="#F7FAFC", outline=PALETTE["navy"], width=2)
    for i in range(4):
        wx = bx + 7 + i * 15
        canvas.create_rectangle(wx, by + 5, wx + 11, by + 16, fill=PALETTE["blue"], outline="")
    canvas.create_oval(bx + 10, by + bh - 4, bx + 20, by + bh + 6, fill=PALETTE["navy"], outline="")
    canvas.create_oval(bx + bw - 20, by + bh - 4, bx + bw - 10, by + bh + 6, fill=PALETTE["navy"], outline="")

    name = (company_name or "").strip() or "Назва підприємства"
    canvas.create_text(145, height * 0.40, anchor="w", text=name, fill="#FFFFFF", font=("TkDefaultFont", 18, "bold"))
    canvas.create_text(146, height * 0.69, anchor="w", text=app_label, fill=PALETTE["soft_blue"], font=("TkDefaultFont", 10))
    canvas.create_text(
        width - 24,
        height * 0.52,
        anchor="e",
        text="План  •  Факт  •  Документи",
        fill=PALETTE["gold_soft"],
        font=("TkDefaultFont", 10, "bold"),
    )


def generate_build_icons(base_dir=None):
    """Generate PNG/ICO/ICNS assets during packaging, keeping binaries out of Git."""
    base = Path(base_dir or Path.cwd())
    out = base / "build_assets"
    out.mkdir(parents=True, exist_ok=True)

    icon = create_brand_image(1024)
    png = out / "taxo_icon.png"
    ico = out / "taxo_icon.ico"
    icns = out / "taxo_icon.icns"
    icon.save(png, format="PNG")
    icon.save(ico, format="ICO", sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])
    icon.save(icns, format="ICNS")
    return {"png": png, "ico": ico, "icns": icns}


if __name__ == "__main__":
    paths = generate_build_icons()
    for key, path in paths.items():
        print(f"{key}: {path}")
