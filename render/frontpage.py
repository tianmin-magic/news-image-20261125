#!/usr/bin/env python3
"""Draw a one-page newspaper front page for 25 November 2026.

Only Pillow and the Liberation fonts are used. No network, no clock, no
randomness: the same input always produces the same bytes.
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FONT_DIR = "/usr/share/fonts/truetype/liberation"
SERIF_BOLD = os.path.join(FONT_DIR, "LiberationSerif-Bold.ttf")
SERIF = os.path.join(FONT_DIR, "LiberationSerif-Regular.ttf")
SANS_BOLD = os.path.join(FONT_DIR, "LiberationSans-Bold.ttf")
SANS = os.path.join(FONT_DIR, "LiberationSans-Regular.ttf")
SANS_ITALIC = os.path.join(FONT_DIR, "LiberationSans-Italic.ttf")

PAGE_W, PAGE_H = 1024, 1024
PAPER = (253, 253, 248)
INK = (18, 18, 18)
GREY = (96, 96, 92)
RED = (168, 32, 26)
GREEN = (28, 110, 58)
NAVY = (24, 42, 72)
MARGIN = 36


def load_font(path, size):
    return ImageFont.truetype(path, size)


def split_lines(text, font, max_w, draw):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = text.split()
    lines, current = [], ""
    for word in words:
        trial = word if not current else current + " " + word
        if draw.textlength(trial, font=font) <= max_w:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_rule(draw, x0, x1, y, width=2, colour=INK):
    draw.line([(x0, y), (x1, y)], fill=colour, width=width)


def draw_kicker(draw, text, x, y, size=16):
    font = load_font(SANS_BOLD, size)
    draw.text((x, y), text, font=font, fill=RED)
    return y + size + 5


def draw_wrapped(draw, text, font, x, y, max_w, leading, colour=INK):
    lines = split_lines(text, font, max_w, draw)
    for line in lines:
        draw.text((x, y), line, font=font, fill=colour)
        y += leading
    return y


def draw_masthead(draw, name):
    name_font = load_font(SERIF_BOLD, 62)
    w = draw.textlength(name, font=name_font)
    draw.text(((PAGE_W - w) / 2, 24), name, font=name_font, fill=INK)
    draw_rule(draw, MARGIN, PAGE_W - MARGIN, 100, 3)
    draw_rule(draw, MARGIN, PAGE_W - MARGIN, 105, 1)
    meta_font = load_font(SANS_BOLD, 16)
    left = "WEDNESDAY, 25 NOVEMBER 2026"
    right = "WORLD NEWS  •  ONE PAGE"
    draw.text((MARGIN, 114), left, font=meta_font, fill=GREY)
    rw = draw.textlength(right, font=meta_font)
    draw.text((PAGE_W - MARGIN - rw, 114), right, font=meta_font, fill=GREY)
    draw_rule(draw, MARGIN, PAGE_W - MARGIN, 140, 1)
    return 152


def draw_market_bars(draw, chart, x, y, w, h):
    """Horizontal bars for the day's market moves."""
    title_font = load_font(SANS_BOLD, 18)
    label_font = load_font(SANS, 18)
    value_font = load_font(SANS_BOLD, 18)
    draw.text((x, y), chart["title"], font=title_font, fill=INK)
    y += 30
    draw_rule(draw, x, x + w, y, 1)
    y += 12
    bars = chart["bars"]
    row_h = (h - 42) // len(bars)
    mid = x + 150
    scale = 10.0  # pixels per percentage point
    for i, bar in enumerate(bars):
        by = y + i * row_h
        draw.text((x, by), bar["label"], font=label_font, fill=INK)
        value = bar["value"]
        length = int(abs(value) * scale)
        if value < 0:
            draw.rectangle([mid - length, by + 2, mid, by + 18], fill=RED)
            draw.text((mid + 8, by), "%.1f%%" % value, font=value_font,
                      fill=RED)
        else:
            draw.rectangle([mid, by + 2, mid + length, by + 18], fill=GREEN)
            draw.text((mid + length + 6, by), "+%.1f%%" % value,
                      font=value_font, fill=GREEN)
        draw.line([(mid, by - 2), (mid, by + 20)], fill=GREY, width=1)
    return y + len(bars) * row_h


def draw_rocket_panel(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=NAVY)
    for sx, sy in [(18, 12), (52, 30), (88, 8), (120, 26), (30, 46),
                   (96, 44), (140, 12), (150, 48), (64, 52), (110, 54)]:
        draw.ellipse([x + sx - 2, y + sy - 2, x + sx + 2, y + sy + 2],
                     fill=(255, 255, 255))
    cx = x + w // 2
    draw.polygon([(cx - 10, y + h - 34), (cx + 10, y + h - 34),
                  (cx, y + h - 8)], fill=(255, 176, 32))
    draw.rectangle([cx - 14, y + 14, cx + 14, y + h - 34],
                   fill=(240, 240, 235))
    draw.polygon([(cx - 14, y + 14), (cx + 14, y + 14), (cx, y + 2)],
                 fill=(200, 40, 32))
    draw.polygon([(cx - 14, y + h - 44), (cx - 30, y + h - 28),
                  (cx - 14, y + h - 28)], fill=(200, 40, 32))
    draw.polygon([(cx + 14, y + h - 44), (cx + 30, y + h - 28),
                  (cx + 14, y + h - 28)], fill=(200, 40, 32))
    draw.ellipse([cx - 6, y + 20, cx + 6, y + 28], fill=NAVY)


def draw_tower_panel(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(226, 226, 218))
    base = y + h - 6
    draw.rectangle([x + 8, base - 28, x + 34, base], fill=(70, 70, 66))
    draw.rectangle([x + 40, base - 44, x + 62, base], fill=(96, 96, 92))
    draw.rectangle([x + 68, base - 22, x + 92, base], fill=(70, 70, 66))
    tx = x + w - 52
    draw.polygon([(tx, y + 6), (tx + 22, y + 6), (tx + 16, base),
                  (tx + 6, base)], fill=(24, 42, 72))
    draw.line([(tx + 11, y + 6), (tx + 11, y)], fill=(24, 42, 72), width=2)
    for wy in range(y + 18, base - 6, 11):
        draw.rectangle([tx + 8, wy, tx + 14, wy + 5], fill=(255, 210, 90))


def draw_story_card(draw, story, x, y, w, graphic=None, graphic_h=64):
    yy = draw_kicker(draw, story["kicker"], x, y)
    head_font = load_font(SERIF_BOLD, 26)
    yy = draw_wrapped(draw, story["headline"], head_font, x, yy, w, 29)
    yy += 4
    if graphic == "rocket":
        draw_rocket_panel(draw, x, yy, w, graphic_h)
        yy += graphic_h + 8
    elif graphic == "tower":
        draw_tower_panel(draw, x, yy, w, graphic_h)
        yy += graphic_h + 8
    body_font = load_font(SANS, 17)
    lines = split_lines(story["body"], body_font, w, draw)
    for line in lines[:2]:
        draw.text((x, yy), line, font=body_font, fill=INK)
        yy += 21
    src_font = load_font(SANS_ITALIC, 13)
    draw.text((x, yy + 2), "— " + story["source"], font=src_font, fill=GREY)
    return yy + 15


def draw_also_today(draw, items, y):
    draw_rule(draw, MARGIN, PAGE_W - MARGIN, y, 2)
    y += 10
    label_font = load_font(SANS_BOLD, 17)
    draw.text((MARGIN, y), "ALSO TODAY", font=label_font, fill=RED)
    y += 26
    body_font = load_font(SANS, 16)
    sep = "   •   "
    lines, current = [], ""
    for item in items:
        trial = item if not current else current + sep + item
        if draw.textlength(trial, font=body_font) <= PAGE_W - 2 * MARGIN:
            current = trial
        else:
            lines.append(current)
            current = item
    if current:
        lines.append(current)
    for line in lines:
        draw.text((MARGIN, y), line, font=body_font, fill=INK)
        y += 21
    return y


def build_page(stories_path, out_path):
    with open(stories_path, encoding="utf-8") as fh:
        data = json.load(fh)
    img = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    draw = ImageDraw.Draw(img)

    y = draw_masthead(draw, data["masthead"])

    lead = data["lead"]
    left_w = 600
    right_x = MARGIN + left_w + 24
    right_w = PAGE_W - MARGIN - right_x
    y = draw_kicker(draw, lead["kicker"], MARGIN, y)
    head_font = load_font(SERIF_BOLD, 50)
    y = draw_wrapped(draw, lead["headline"], head_font, MARGIN, y,
                     left_w, 56)
    y += 6
    deck_font = load_font(SERIF, 21)
    lead_end = draw_wrapped(draw, lead["deck"], deck_font, MARGIN, y,
                            left_w, 28)
    src_font = load_font(SANS_ITALIC, 13)
    draw.text((MARGIN, lead_end + 6), "— " + lead["source"],
              font=src_font, fill=GREY)
    draw_market_bars(draw, lead["chart"], right_x, 168, right_w, 280)
    draw_rule(draw, MARGIN, PAGE_W - MARGIN, 492, 2)

    col_w = (PAGE_W - 2 * MARGIN - 36) // 2
    left_x = MARGIN
    right_col_x = MARGIN + col_w + 36
    top = 508
    yy = top
    for story in data["grid_left"]:
        yy = draw_story_card(draw, story, left_x, yy, col_w)
        if story is not data["grid_left"][-1]:
            draw_rule(draw, left_x, left_x + col_w, yy + 2, 1, GREY)
            yy += 8
    yy = top
    for story in data["grid_right"]:
        yy = draw_story_card(draw, story, right_col_x, yy, col_w,
                             graphic=story.get("graphic"), graphic_h=64)
        if story is not data["grid_right"][-1]:
            draw_rule(draw, right_col_x, right_col_x + col_w, yy + 2, 1,
                      GREY)
            yy += 8

    draw_also_today(draw, data["also_today"], 940)
    draw_rule(draw, MARGIN, PAGE_W - MARGIN, 1016, 1)
    img.save(out_path, "PNG")


def main(argv):
    stories = argv[1] if len(argv) > 1 else os.path.join(
        ROOT, "content", "stories.json")
    out = argv[2] if len(argv) > 2 else os.path.join(ROOT, "entry.png")
    build_page(stories, out)
    print("wrote", out)


if __name__ == "__main__":
    main(sys.argv)
