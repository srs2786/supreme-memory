import os
import json
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def load_style():
    with open("config/style_guide.json") as f:
        return json.load(f)["card"]

def get_font(size: int, bold=False):
    """Load font — bundled DejaVu first, then system fallbacks."""
    bundled = "assets/fonts/DejaVuSans-Bold.ttf" if bold else "assets/fonts/DejaVuSans.ttf"
    candidates = [
        bundled,
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/HelveticaNeue.ttc",
    ]
    for path in candidates:
        try:
            idx = 1 if (bold and path.endswith("Helvetica.ttc")) else 0
            return ImageFont.truetype(path, size, index=idx)
        except Exception:
            continue
    return ImageFont.load_default()

def wrap_text(text: str, font, max_width: int) -> list[str]:
    dummy = Image.new("RGB", (1, 1))
    d = ImageDraw.Draw(dummy)
    lines = []
    for para in text.split("\n"):
        words = para.split()
        current = []
        for word in words:
            test = " ".join(current + [word])
            if d.textbbox((0, 0), test, font=font)[2] <= max_width:
                current.append(word)
            else:
                if current:
                    lines.append(" ".join(current))
                current = [word]
        if current:
            lines.append(" ".join(current))
    return lines

def circular_crop(path: str, size=80):
    img = Image.open(path).convert("RGBA").resize((size, size))
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)
    img.putalpha(mask)
    return img

def render_card(draft: dict, slug: str) -> str:
    """Render 1200x1200px card and save as JPEG. Returns file path."""
    style = load_style()
    W = style["width"]
    H = style["height"]
    PAD_X = style["padding_x"]
    PAD_Y = style["padding_y"]
    CONTENT_W = W - (PAD_X * 2)
    colors = style["colors"]

    # Fonts
    f_name     = get_font(30, bold=True)
    f_title    = get_font(22, bold=False)
    f_headline = get_font(64, bold=True)
    f_num      = get_font(20, bold=False)
    f_sec_bold = get_font(30, bold=True)
    f_body     = get_font(24, bold=False)
    f_footer   = get_font(22, bold=False)

    img = Image.new("RGB", (W, H), "#FFFFFF")
    d = ImageDraw.Draw(img)

    y = PAD_Y

    # Header row
    headshot_path = "assets/headshots/head_shot.jpg"
    if os.path.exists(headshot_path):
        hs = circular_crop(headshot_path, 80)
        img.paste(hs, (PAD_X, y), hs)

    d.text((PAD_X + 96, y + 14), "Sarabpreet Singh",
           font=f_name, fill=colors["black"])
    d.text((PAD_X + 96, y + 48), "Manufacturing Systems Architect",
           font=f_title, fill=colors["light_grey"])
    y += 80 + 40

    # Headline
    headline_lines = wrap_text(draft["headline"], f_headline, CONTENT_W)
    for line in headline_lines:
        d.text((PAD_X, y), line, font=f_headline, fill=colors["black"])
        bbox = d.textbbox((0, 0), line, font=f_headline)
        y += (bbox[3] - bbox[1]) + 10
    y += 28

    # Divider
    d.line([(PAD_X, y), (W - PAD_X, y)], fill=colors["divider"], width=1)
    y += 28

    # Sections
    for section in draft.get("sections", []):
        d.text((PAD_X, y), section["number"],
               font=f_num, fill="#AAAAAA")
        y += 8 + 20

        title_lines = wrap_text(section["title"], f_sec_bold, CONTENT_W)
        for line in title_lines:
            d.text((PAD_X, y), line, font=f_sec_bold, fill=colors["dark_grey"])
            bbox = d.textbbox((0, 0), line, font=f_sec_bold)
            y += (bbox[3] - bbox[1]) + 4
        y += 8

        body_lines = wrap_text(section["body"], f_body, CONTENT_W)
        for line in body_lines:
            d.text((PAD_X, y), line, font=f_body, fill="#666666")
            bbox = d.textbbox((0, 0), line, font=f_body)
            y += (bbox[3] - bbox[1]) + 6
        y += 28

        # Safety check — stop if exceeding canvas (leave room for footer)
        if y > H - 160:
            break

    # Footer
    footer_y = H - PAD_Y - 40
    d.line([(PAD_X, footer_y), (W - PAD_X, footer_y)],
           fill=colors["divider"], width=1)
    d.text((PAD_X, footer_y + 14), "@sarabpreetsingh",
           font=f_footer, fill=colors["light_grey"])

    # Save
    out_dir = Path(f"output/linkedin/{slug}")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = str(out_dir / "post.jpg")
    img.save(out_path, "JPEG", quality=95)
    print(f"[Card] Saved to {out_path}")
    return out_path
