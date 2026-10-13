"""
Icon generator and visual assets for Shalbny.
Loads the official Shalbny brand icon and tray icons with procedural geometric fallback.
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw


def _get_assets_dir() -> Path:
    """Returns the assets directory path across development and frozen binaries."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / "assets"
    return Path(__file__).resolve().parent.parent.parent / "assets"


def render_geometric_portal_icon(size: int = 64, is_paused: bool = False) -> Image.Image:
    """
    Renders the official Shalbny geometric icon fallback:
    A sleek electric cyan-blue rounded square with a hollow center and cobalt shaded facet.
    """
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    pad = max(2, int(size * 0.08))
    thickness = max(4, int(size * 0.22))
    outer_r = max(3, int(size * 0.20))
    inner_r = max(2, int(size * 0.10))

    if is_paused:
        light_blue = (120, 144, 156, 255)  # Muted Slate Blue
        dark_blue = (69, 90, 100, 255)
    else:
        light_blue = (2, 156, 255, 255)    # #029CFF Electric Azure
        dark_blue = (0, 98, 177, 255)      # #0062B1 Royal Cobalt

    # 1. Outer rounded rect
    draw.rounded_rectangle([pad, pad, size - pad, size - pad], radius=outer_r, fill=light_blue)

    # 2. Right-side shaded facet with 45-degree corner seams
    inner_left = pad + thickness
    inner_top = pad + thickness
    inner_right = size - pad - thickness
    inner_bottom = size - pad - thickness

    dark_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d_draw = ImageDraw.Draw(dark_layer)
    d_draw.rounded_rectangle([pad, pad, size - pad, size - pad], radius=outer_r, fill=dark_blue)

    mask = Image.new("L", (size, size), 0)
    m_draw = ImageDraw.Draw(mask)
    m_poly = [
        (inner_right, inner_top),
        (size, 0),
        (size, size),
        (inner_right, inner_bottom)
    ]
    m_draw.polygon(m_poly, fill=255)

    img = Image.composite(dark_layer, img, mask)

    # 3. Transparent center hole
    hole_mask = Image.new("RGBA", (size, size), (0, 0, 0, 255))
    h_draw = ImageDraw.Draw(hole_mask)
    h_draw.rounded_rectangle([inner_left, inner_top, inner_right, inner_bottom], radius=inner_r, fill=(0, 0, 0, 0))

    _, _, _, hole_a = hole_mask.split()
    final_a = Image.eval(hole_a, lambda p: 0 if p == 0 else 255)
    final_img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    final_img.paste(img, (0, 0), mask=final_a)

    return final_img


def create_tray_icon(is_paused: bool = False, size: int = 64) -> Image.Image:
    """Loads and returns the official tray icon, falling back to geometric renderer."""
    filename = "tray_icon_paused.png" if is_paused else "tray_icon.png"
    tray_file = _get_assets_dir() / filename
    if tray_file.exists():
        try:
            im = Image.open(tray_file).convert("RGBA")
            if im.size != (size, size):
                im = im.resize((size, size), Image.Resampling.LANCZOS)
            return im
        except Exception:
            pass
    return render_geometric_portal_icon(size=size, is_paused=is_paused)


def create_app_icon(size: int = 64) -> Image.Image:
    """Loads and returns the official app icon, falling back to geometric renderer."""
    logo_file = _get_assets_dir() / "logo.png"
    if logo_file.exists():
        try:
            im = Image.open(logo_file).convert("RGBA")
            if im.size != (size, size):
                im = im.resize((size, size), Image.Resampling.LANCZOS)
            return im
        except Exception:
            pass
    return render_geometric_portal_icon(size=size, is_paused=False)
