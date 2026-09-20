# -*- coding: utf-8 -*-
"""Visual identity helpers for Taxo / Driver Worktime.

Branding deliberately contains no enterprise name inside the artwork.  The
company name is rendered as live text from the company settings so one Taxo
build can be used by any carrier.
"""
from __future__ import annotations

from pathlib import Path

PALETTE = {
    "navy": "#0F3A67",
    "blue": "#087FC3",
    "blue_dark": "#075B8B",
    "sidebar": "#126B99",
    "header": "#EAF7FD",
    "header_2": "#DDF1FB",
    "soft_blue": "#EAF4FA",
    "soft_blue_2": "#D8ECF7",
    "gold": "#E6B52C",
    "gold_soft": "#FFF1B8",
    "cream": "#FFF9DD",
    "paper": "#F4FAFD",
    "panel": "#FFFFFF",
    "text": "#17324D",
    "muted": "#667A8D",
    "line": "#B8D7E8",
    "success": "#159A59",
    "success_soft": "#E6F6EC",
    "warning": "#E49B00",
    "warning_soft": "#FFF4D2",
    "danger": "#D9434E",
    "danger_soft": "#FDEBEC",
    "info_soft": "#E8F5FC",
}


def apply_theme(root, ttk):
    """Apply the approved calm blue/yellow office palette."""
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass

    root.configure(bg=PALETTE["paper"])
    style.configure(".", font=("TkDefaultFont", 10))
    style.configure("TFrame", background=PALETTE["paper"])
    style.configure("Card.TFrame", background=PALETTE["panel"], relief="solid", borderwidth=1)
    style.configure("Toolbar.TFrame", background=PALETTE["header"])
    style.configure("TLabel", background=PALETTE["paper"], foreground=PALETTE["text"])
    style.configure(
        "HeroTitle.TLabel",
        background=PALETTE["paper"],
        foreground=PALETTE["navy"],
        font=("TkDefaultFont", 17, "bold"),
    )
    style.configure(
        "SectionTitle.TLabel",
        background=PALETTE["paper"],
        foreground=PALETTE["navy"],
        font=("TkDefaultFont", 12, "bold"),
    )
    style.configure(
        "Muted.TLabel",
        background=PALETTE["paper"],
        foreground=PALETTE["muted"],
    )
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
        background=PALETTE["blue"],
        foreground="#FFFFFF",
        font=("TkDefaultFont", 10, "bold"),
        bordercolor=PALETTE["blue_dark"],
    )
    style.map(
        "Accent.TButton",
        background=[("active", PALETTE["blue_dark"]), ("pressed", PALETTE["navy"])],
        foreground=[("disabled", "#D9E4EB")],
    )
    style.configure(
        "Gold.TButton",
        background=PALETTE["gold"],
        foreground=PALETTE["navy"],
        font=("TkDefaultFont", 10, "bold"),
        bordercolor="#C99516",
    )
    style.map(
        "Gold.TButton",
        background=[("active", "#F0C84B"), ("pressed", "#D59D17")],
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
        background=[("selected", "#1597D4")],
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


def _draw_bus(draw, x, y, w, h):
    """Draw the yellow/black bus silhouette used by the approved reference."""
    from PIL import ImageDraw

    outline = "#101010"
    yellow = "#F2CF4B"
    yellow_dark = "#D6AF2C"
    wheel = "#111111"
    stroke = max(2, int(w * 0.018))

    # Main long body and short bonnet.
    body_right = x + int(w * 0.80)
    draw.rounded_rectangle(
        (x, y + int(h * 0.12), body_right, y + int(h * 0.80)),
        radius=max(5, int(h * 0.08)), fill=yellow, outline=outline, width=stroke
    )
    draw.polygon([
        (body_right - stroke, y + int(h * 0.42)),
        (x + int(w * 0.90), y + int(h * 0.42)),
        (x + int(w * 0.98), y + int(h * 0.56)),
        (x + w, y + int(h * 0.77)),
        (x + int(w * 0.78), y + int(h * 0.77)),
    ], fill=yellow, outline=outline)
    draw.line(
        (body_right, y + int(h * 0.12), body_right, y + int(h * 0.77)),
        fill=outline, width=stroke
    )

    # Windows.
    pad = int(w * 0.04)
    top = y + int(h * 0.23)
    bottom = y + int(h * 0.47)
    usable = int(w * 0.66)
    gap = max(2, int(w * 0.012))
    count = 6
    ww = int((usable - gap * (count - 1)) / count)
    for idx in range(count):
        wx = x + pad + idx * (ww + gap)
        draw.rectangle((wx, top, wx + ww, bottom), fill=outline)

    # Passenger door and decorative lines.
    door_x = x + int(w * 0.68)
    draw.rectangle(
        (door_x, y + int(h * 0.20), door_x + int(w * 0.07), y + int(h * 0.67)),
        fill=outline
    )
    draw.line(
        (x + pad, y + int(h * 0.56), x + int(w * 0.67), y + int(h * 0.56)),
        fill=outline, width=max(2, stroke // 2)
    )
    draw.line(
        (x + int(w * 0.02), y + int(h * 0.73), x + int(w * 0.78), y + int(h * 0.73)),
        fill=yellow_dark, width=max(2, stroke // 2)
    )

    # Wheels.
    wheel_r = max(5, int(h * 0.14))
    for cx in (x + int(w * 0.22), x + int(w * 0.83)):
        cy = y + int(h * 0.79)
        draw.ellipse((cx-wheel_r, cy-wheel_r, cx+wheel_r, cy+wheel_r), fill=wheel)
        hub = max(2, int(wheel_r * 0.38))
        draw.ellipse((cx-hub, cy-hub, cx+hub, cy+hub), fill=yellow)

    # Small front light.
    draw.ellipse(
        (
            x + int(w * 0.965), y + int(h * 0.60),
            x + int(w * 0.99), y + int(h * 0.66),
        ),
        fill=yellow_dark, outline=outline
    )


def create_brand_image(size=512):
    """Create the approved text-free cream/yellow bus mark."""
    from PIL import Image, ImageDraw

    size = int(size)
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    cream = "#FFF8D8"
    gold = "#F1D15A"
    edge = "#E6DDAF"

    # The supplied reference uses two irregular paper/sun shapes behind the bus.
    draw.polygon([
        (int(size*.29), int(size*.12)),
        (int(size*.72), int(size*.31)),
        (int(size*.64), int(size*.91)),
        (int(size*.24), int(size*.72)),
    ], fill=gold)
    draw.polygon([
        (int(size*.17), int(size*.24)),
        (int(size*.79), int(size*.27)),
        (int(size*.73), int(size*.76)),
        (int(size*.29), int(size*.85)),
    ], fill=cream, outline=edge)

    _draw_bus(
        draw,
        int(size * .14),
        int(size * .38),
        int(size * .72),
        int(size * .27),
    )
    return image


def brand_photo(master, size=96):
    """Return a PhotoImage of the text-free logo and keep ownership at caller."""
    from PIL import ImageTk

    return ImageTk.PhotoImage(create_brand_image(size), master=master)


def create_nav_icon(kind, size=28, color="#FFFFFF"):
    """Create small monochrome sidebar icons used by the approved shell."""
    from PIL import Image, ImageDraw

    size=int(size)
    img=Image.new("RGBA",(size,size),(0,0,0,0))
    d=ImageDraw.Draw(img)
    w=max(2,size//10)
    c=color
    k=(kind or "").lower()

    if k=="people":
        r=size*.16
        d.ellipse((size*.16,size*.10,size*.16+2*r,size*.10+2*r),outline=c,width=w)
        d.ellipse((size*.50,size*.16,size*.50+2*r,size*.16+2*r),outline=c,width=w)
        d.arc((size*.08,size*.40,size*.55,size*.92),190,350,fill=c,width=w)
        d.arc((size*.38,size*.44,size*.92,size*.94),190,350,fill=c,width=w)
    elif k=="calendar":
        d.rounded_rectangle((size*.12,size*.18,size*.88,size*.88),radius=max(2,size//10),outline=c,width=w)
        d.line((size*.12,size*.36,size*.88,size*.36),fill=c,width=w)
        for x in (size*.32,size*.56,size*.76):
            d.ellipse((x-size*.035,size*.52-size*.035,x+size*.035,size*.52+size*.035),fill=c)
            d.ellipse((x-size*.035,size*.70-size*.035,x+size*.035,size*.70+size*.035),fill=c)
        d.line((size*.30,size*.08,size*.30,size*.27),fill=c,width=w)
        d.line((size*.70,size*.08,size*.70,size*.27),fill=c,width=w)
    elif k=="bus":
        d.rounded_rectangle((size*.08,size*.25,size*.88,size*.72),radius=max(2,size//10),outline=c,width=w)
        for x0,x1 in ((.18,.35),(.40,.57),(.62,.78)):
            d.rectangle((size*x0,size*.34,size*x1,size*.49),outline=c,width=max(1,w-1))
        d.ellipse((size*.19,size*.66,size*.36,size*.83),outline=c,width=w)
        d.ellipse((size*.63,size*.66,size*.80,size*.83),outline=c,width=w)
    elif k=="route":
        d.ellipse((size*.10,size*.12,size*.34,size*.36),outline=c,width=w)
        d.ellipse((size*.66,size*.64,size*.90,size*.88),outline=c,width=w)
        d.line((size*.24,size*.34,size*.35,size*.56,size*.55,size*.44,size*.76,size*.66),fill=c,width=w)
    elif k=="document":
        d.polygon([(size*.18,size*.10),(size*.64,size*.10),(size*.84,size*.30),(size*.84,size*.90),(size*.18,size*.90)],outline=c)
        d.line((size*.64,size*.10,size*.64,size*.30,size*.84,size*.30),fill=c,width=w)
        for y in (.45,.60,.75):
            d.line((size*.30,size*y,size*.72,size*y),fill=c,width=max(1,w-1))
    elif k=="book":
        d.arc((size*.08,size*.16,size*.49,size*.88),80,280,fill=c,width=w)
        d.arc((size*.51,size*.16,size*.92,size*.88),260,100,fill=c,width=w)
        d.line((size*.50,size*.20,size*.50,size*.86),fill=c,width=w)
    elif k=="chart":
        for x,h in ((.18,.30),(.42,.48),(.66,.68)):
            d.rectangle((size*x,size*(.88-h),size*(x+.14),size*.88),outline=c,width=w)
    elif k=="gear":
        d.ellipse((size*.27,size*.27,size*.73,size*.73),outline=c,width=w)
        d.ellipse((size*.42,size*.42,size*.58,size*.58),outline=c,width=w)
        for a,b,cx,cy in (
            (.44,.06,.50,.20),(.44,.74,.50,.94),(.06,.44,.20,.50),(.74,.44,.94,.50),
        ):
            d.rectangle((size*a,size*b,size*cx,size*cy),outline=c,width=max(1,w-1))
    elif k=="disc":
        d.ellipse((size*.12,size*.12,size*.88,size*.88),outline=c,width=w)
        d.ellipse((size*.40,size*.40,size*.60,size*.60),outline=c,width=w)
        d.arc((size*.22,size*.22,size*.78,size*.78),20,150,fill=c,width=max(1,w-1))
    else:
        d.ellipse((size*.22,size*.22,size*.78,size*.78),outline=c,width=w)
    return img


def nav_photo(master, kind, size=28, color="#FFFFFF"):
    from PIL import ImageTk
    return ImageTk.PhotoImage(create_nav_icon(kind,size,color),master=master)


def install_runtime_icon(root):
    """Set the same text-free logo as the application icon."""
    photo = brand_photo(root, 128)
    root.iconphoto(True, photo)
    root._taxo_brand_icon = photo
    return photo


def draw_brand_header(canvas, company_name="", app_label="Taxo / Driver Worktime"):
    """Render the light approved main header with a dynamic enterprise name."""
    from PIL import ImageTk

    width = max(760, int(canvas.winfo_width() or 760))
    height = max(96, int(canvas.winfo_height() or 96))
    canvas.delete("all")
    canvas.configure(bg=PALETTE["header"], highlightthickness=0)

    logo = create_brand_image(90)
    photo = ImageTk.PhotoImage(logo, master=canvas)
    canvas._taxo_header_logo = photo
    canvas.create_image(18, height / 2, anchor="w", image=photo)

    name = (company_name or "").strip() or "Назва підприємства"
    canvas.create_text(
        120, height * .35, anchor="w",
        text=f"Taxo / {name}",
        fill="#151A73", font=("TkDefaultFont", 19, "bold")
    )
    canvas.create_text(
        122, height * .66, anchor="w",
        text="Автотранспортне підприємство",
        fill=PALETTE["blue_dark"], font=("TkDefaultFont", 11)
    )

    # Approved central handwritten-style idea, rendered with a portable font.
    canvas.create_text(
        max(500, width * .47), height * .42, anchor="center",
        text="Рухаємо людей", fill="#1556C0",
        font=("TkDefaultFont", 11, "italic")
    )
    canvas.create_text(
        max(500, width * .47), height * .64, anchor="center",
        text="до кращого завтра!", fill="#1556C0",
        font=("TkDefaultFont", 11, "italic")
    )
    canvas.create_line(
        max(425, width * .41), height * .79,
        max(590, width * .54), height * .65,
        fill=PALETTE["gold"], width=3
    )
    if width >= 1050:
        canvas.create_text(
            width - 24, height * .50, anchor="e",
            text="Надійний перевізник\nнашого регіону",
            justify="right", fill="#6D95B5",
            font=("TkDefaultFont", 10, "italic")
        )
    canvas.create_line(0, height - 2, width, height - 2, fill="#7CC5E8", width=2)


def configure_toplevel(win):
    """Apply the brand basics to a secondary window."""
    win.configure(bg=PALETTE["paper"])
    try:
        install_runtime_icon(win)
    except Exception:
        pass


def generate_build_icons(base_dir=None):
    """Generate PNG/ICO/ICNS assets during packaging."""
    base = Path(base_dir or Path.cwd())
    out = base / "build_assets"
    out.mkdir(parents=True, exist_ok=True)

    icon = create_brand_image(1024)
    png = out / "taxo_icon.png"
    ico = out / "taxo_icon.ico"
    icns = out / "taxo_icon.icns"
    icon.save(png, format="PNG")
    icon.save(
        ico,
        format="ICO",
        sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)],
    )
    icon.save(icns, format="ICNS")
    return {"png": png, "ico": ico, "icns": icns}


if __name__ == "__main__":
    paths = generate_build_icons()
    for key, path in paths.items():
        print(f"{key}: {path}")
