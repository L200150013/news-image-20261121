#!/usr/bin/env python3
"""news-image-20261121: one front page summing up Saturday 21 November 2026.

Draws a 1024x1024 PNG with PIL only. Deterministic: no network, no clock,
no randomness. Writes entry.png into MAKEFUN_OUTPUT_DIR (default "out").
"""
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 22

PAPER = (247, 243, 234)
INK = (26, 26, 26)
MUTED = (90, 86, 76)
RULE = (26, 26, 26)
PANEL = (255, 253, 247)
PANEL_LINE = (196, 188, 168)
LAND = (232, 222, 196)
LAND_LINE = (150, 138, 108)
SEA = (214, 228, 232)

# Topic colours: conflict/security, climate/environment, economy,
# justice/politics, other.
TOPIC = {
    "conflict": (179, 38, 30),
    "climate": (29, 111, 184),
    "economy": (154, 107, 0),
    "justice": (46, 125, 50),
    "other": (107, 107, 107),
}
TOPIC_NAME = {
    "conflict": "Conflict & security",
    "climate": "Climate & environment",
    "economy": "Economy",
    "justice": "Justice & politics",
    "other": "Science & other",
}

# Continent colours for the map.
CONTINENT = {
    "North America": (46, 111, 183),
    "South America": (61, 158, 87),
    "Europe": (122, 79, 163),
    "Africa": (192, 122, 26),
    "Asia": (178, 58, 72),
    "Oceania": (42, 157, 143),
}

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(text, fnt, max_w):
    """Greedy wrap; returns list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if fnt.getlength(trial) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_lines(text, fnt, max_w, max_lines, label):
    lines = wrap(text, fnt, max_w)
    if len(lines) > max_lines:
        raise SystemExit("OVERFLOW %s: %r -> %d lines" % (label, text, len(lines)))
    return lines


def draw_text_block(draw, lines, fnt, x, y, lh, color=INK):
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=color)
        y += lh
    return y


# ---------------------------------------------------------------- stories
# (number, kicker, topic, headline, deck, icon)
LEADS = [
    (1, "MIDDLE EAST · RIYADH", "conflict",
     "Coalition says it downed three missiles aimed at Riyadh",
     "Two more intercepted over Jazan; alerts sound for a third night.",
     "missile"),
    (2, "EUROPE · KYIV", "conflict",
     "Kyiv bridges hit; missiles land in Poland",
     "Kyiv reports 400+ drones and 110 missiles; at least eight dead.",
     "bridge"),
    (3, "WORLD · ANTALYA", "climate",
     "COP31 slips into overtime with no deal",
     "Draft drops every mention of fossil fuels; a third text due Saturday.",
     "globe"),
    (4, "SPACE · MERCURY", "other",
     "BepiColombo fires up for Mercury orbit",
     "After eight years, the ESA–JAXA craft begins its capture burn.",
     "planet"),
    (5, "ASIA · THE HAGUE", "justice",
     "World court: Myanmar committed genocide",
     "The ICJ ruling is a landmark for the Rohingya case.",
     "scales"),
    (6, "EUROPE · COPENHAGEN", "conflict",
     "Denmark expels Russian diplomat",
     "Moscow is accused of plotting to kill a US-Ukrainian rapper.",
     "envelope"),
    (7, "SOUTH AMERICA · PERU", "other",
     "Magnitude 6.8 quake shakes Peru",
     "The tremor struck at 01:09 UTC Saturday; felt in Lima.",
     "wave"),
    (8, "EUROPE", "justice",
     "Gen Z marches in 25 European states",
     "Thousands rally over costs, military spending and climate.",
     "people"),
    (9, "ASIA · MUMBAI", "economy",
     "Record foreign cash floods Indian shares",
     "November inflows hit ₹1.22 lakh crore, a monthly record.",
     "chart"),
    (10, "N. AMERICA · WASHINGTON", "economy",
     "Trump threatens tax on overseas AI hubs",
     "US firms building data centres abroad face a new levy.",
     "chip"),
    (11, "ASIA · ULAANBAATAR", "justice",
     "Mongolia's president resigns",
     "The resignation clears the way for a snap election.",
     "flag"),
]

# (number, region, topic, one-line story)
ALSO = [
    (12, "NEW YORK", "justice", "Mamdani sets 2032 as the date to close Rikers Island."),
    (13, "BRUSSELS", "economy", "EU sends Ukraine nearly €8bn, its largest reforms payment."),
    (14, "GAZA", "conflict", "Israeli drone strikes kill seven Palestinians in central Gaza."),
    (15, "HUDAYDAH", "conflict", "UN warns attacks on the port threaten a vital aid lifeline."),
    (16, "WASHINGTON", "economy", "Trump calls on Nvidia to reinstate 'brilliant' Jensen Huang."),
    (17, "NEW DELHI", "justice", "Nepal's PM begins his first foreign visit, in Delhi."),
    (18, "WELLINGTON", "other", "Rahul's 100 completes the SENA set for an Indian opener."),
    (19, "WASHINGTON", "other", "US declassifies more UFO footage filmed in the Middle East."),
    (20, "JOHANNESBURG", "justice", "Nearly 600 women killed in South Africa in three months."),
    (21, "LAGOS", "other", "Boat carrying mourners capsizes in Nigeria, killing at least four."),
    (22, "KINSHASA", "other", "Ebola outbreak in Congo hits children hardest."),
    (23, "PARIS", "justice", "French police sentenced over beating of producer Michel Zecler."),
    (24, "PARIS", "justice", "Depardieu investigated over sexual allegations."),
    (25, "NEW YORK", "economy", "Tech sell-off drags markets as Anthropic shares slide."),
    (26, "WASHINGTON", "economy", "US lawmakers push tougher AI chip rules in China crackdown."),
    (27, "NEW DELHI", "justice", "Man jailed 19+ years in US plot to kill Sikh separatist leader."),
    (28, "CALIFORNIA", "economy", "State subpoenas Nvidia over alleged Chinese chip deals."),
    (29, "TAIPEI", "justice", "Taiwan tells Meta China-linked accounts try to sway elections."),
    (30, "BRASÍLIA", "justice", "Brazil bolsters legal protection of Indigenous land."),
    (31, "KYIV", "other", "Ukraine to send food aid to nine countries."),
    (32, "MOSCOW", "conflict", "Putin rejects energy and Black Sea ceasefire, vows retribution."),
    (33, "JOHANNESBURG", "justice", "ANC fights to hold South Africa's key cities after setback."),
    (34, "GAZA", "other", "Displaced children in Gaza mark World Children's Day."),
    (35, "PORT-AU-PRINCE", "conflict", "Two Salvadoran soldiers killed in Haiti handling explosives."),
]

# Map pins: number -> (lon, lat, label offset dx, dy, place)
PINS = {
    1: (46.7, 24.6, 16, -14, "Riyadh"),
    2: (30.5, 50.4, 20, -14, "Kyiv"),
    3: (30.7, 36.9, 18, 14, "Antalya"),
    4: (8.65, 49.87, 20, 18, "Darmstadt (ESOC)"),
    5: (4.3, 52.08, -22, -14, "The Hague"),
    6: (12.57, 55.68, 16, -16, "Copenhagen"),
    7: (-76.0, -11.0, -18, 12, "Junín, Peru"),
    8: (4.35, 50.85, -24, 18, "Brussels"),
    9: (72.87, 19.07, 12, -12, "Mumbai"),
    10: (-77.03, 38.9, -16, 12, "Washington"),
    11: (106.9, 47.92, 16, -14, "Ulaanbaatar"),
}

# Coarse continent polygons (lon, lat), equirectangular.
CONTINENTS = {
    "North America": [
        (-168, 66), (-140, 70), (-120, 72), (-95, 80), (-80, 73), (-65, 60),
        (-55, 52), (-60, 45), (-75, 35), (-80, 26), (-90, 21), (-97, 16),
        (-105, 20), (-115, 28), (-125, 40), (-125, 49), (-145, 60), (-168, 66),
    ],
    "Greenland": [
        (-45, 60), (-30, 68), (-20, 70), (-35, 76), (-55, 74), (-58, 64),
        (-45, 60),
    ],
    "South America": [
        (-80, 10), (-70, 12), (-60, 8), (-50, 0), (-35, -8), (-40, -20),
        (-48, -28), (-58, -35), (-65, -45), (-70, -54), (-73, -40),
        (-75, -20), (-80, -5), (-80, 10),
    ],
    "Europe": [
        (-10, 36), (-9, 43), (-2, 48), (0, 51), (5, 53), (8, 57), (10, 59),
        (18, 56), (21, 55), (24, 58), (28, 60), (30, 62), (32, 70), (40, 68),
        (44, 66), (40, 60), (35, 55), (30, 50), (28, 45), (23, 40), (19, 42),
        (12, 44), (8, 44), (3, 42), (-2, 37), (-10, 36),
    ],
    "Africa": [
        (-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (32, 31), (35, 28),
        (40, 20), (43, 12), (51, 11), (48, 0), (40, -10), (35, -20),
        (32, -29), (25, -34), (18, -35), (15, -27), (12, -18), (9, -1),
        (9, 4), (-8, 5), (-13, 8), (-17, 15),
    ],
    "Asia": [
        (32, 70), (40, 68), (55, 70), (70, 72), (90, 75), (110, 76),
        (130, 72), (150, 70), (170, 67), (178, 65), (170, 60), (160, 60),
        (158, 52), (142, 50), (140, 40), (130, 35), (127, 35), (122, 30),
        (120, 22), (110, 20), (105, 10), (100, 8), (97, 15), (92, 20),
        (88, 22), (80, 15), (75, 8), (72, 20), (66, 25), (60, 25), (55, 26),
        (50, 29), (48, 30), (44, 29), (40, 32), (36, 36), (32, 42), (30, 46),
        (28, 50), (32, 55), (35, 62), (32, 70),
    ],
    "Oceania": [
        (113, -22), (114, -30), (115, -35), (125, -33), (130, -32),
        (137, -35), (140, -38), (145, -38), (150, -37), (153, -32),
        (153, -27), (150, -22), (146, -19), (142, -15), (142, -11),
        (136, -12), (132, -12), (130, -13), (126, -14), (122, -17),
        (118, -20), (113, -22),
    ],
    "Japan": [
        (130, 31), (132, 33), (135, 34), (138, 35), (140, 38), (141, 42),
        (143, 44), (141, 40), (139, 37), (136, 33), (130, 31),
    ],
    "UK": [
        (-5, 50), (-3, 53), (-5, 56), (-2, 58), (0, 53), (-1, 51), (-5, 50),
    ],
    "NZ": [
        (167, -45), (174, -41), (178, -38), (175, -36), (172, -40), (167, -45),
    ],
}
CONTINENT_OF_POLY = {
    "North America": "North America", "Greenland": "North America",
    "South America": "South America", "Europe": "Europe",
    "Africa": "Africa", "Asia": "Asia", "Oceania": "Oceania",
    "Japan": "Asia", "UK": "Europe", "NZ": "Oceania",
}


def tint(color, bg, amount):
    """Mix color toward bg by amount (0..1)."""
    return tuple(int(color[i] * (1 - amount) + bg[i] * amount) for i in range(3))


# ---------------------------------------------------------------- icons
def draw_icon(draw, kind, x, y, s, accent):
    """Small flat glyph in a s x s box at (x, y)."""
    if kind == "missile":
        draw.polygon([(x + 6, y + s - 6), (x + s - 8, y + 8), (x + s - 4, y + 4),
                      (x + 8, y + s - 2)], fill=accent)
        draw.polygon([(x + 2, y + s - 2), (x + 8, y + s - 8), (x + 4, y + s - 2)],
                     fill=(212, 90, 40))
    elif kind == "bridge":
        draw.arc([x + 2, y + 6, x + s - 2, y + s - 2], 180, 360, fill=INK, width=2)
        draw.arc([x + 8, y + 12, x + s - 8, y + s - 2], 180, 360, fill=accent, width=2)
        draw.line([x + 2, y + s - 6, x + s - 2, y + s - 6], fill=INK, width=2)
        draw.line([x + 6, y + 4, x + 6, y + s - 6], fill=INK, width=2)
        draw.line([x + s - 6, y + 4, x + s - 6, y + s - 6], fill=INK, width=2)
    elif kind == "globe":
        draw.ellipse([x + 3, y + 3, x + s - 3, y + s - 3], outline=INK, width=2)
        draw.arc([x + 8, y + 3, x + s - 8, y + s - 3], 270, 90, fill=accent, width=2)
        draw.arc([x + 8, y + 3, x + s - 8, y + s - 3], 90, 270, fill=accent, width=2)
        draw.line([x + 3, y + s // 2, x + s - 3, y + s // 2], fill=accent, width=2)
    elif kind == "planet":
        draw.ellipse([x + 5, y + 6, x + s - 5, y + s - 6], fill=accent)
        draw.arc([x, y + s // 2 - 4, x + s, y + s // 2 + 8], 200, 340, fill=INK, width=2)
        draw.arc([x, y + s // 2 - 4, x + s, y + s // 2 + 8], 20, 160, fill=INK, width=2)
    elif kind == "scales":
        draw.line([x + s // 2, y + 3, x + s // 2, y + s - 4], fill=INK, width=2)
        draw.line([x + 3, y + 7, x + s - 3, y + 7], fill=INK, width=2)
        draw.polygon([(x + 2, y + 9), (x + 10, y + 9), (x + 6, y + 17)], fill=accent)
        draw.polygon([(x + s - 10, y + 9), (x + s - 2, y + 9), (x + s - 6, y + 17)],
                     fill=accent)
        draw.line([x + 4, y + s - 4, x + s - 4, y + s - 4], fill=INK, width=2)
    elif kind == "envelope":
        draw.rectangle([x + 3, y + 7, x + s - 3, y + s - 6], outline=INK, width=2)
        draw.line([x + 3, y + 7, x + s // 2, y + s // 2 + 2], fill=accent, width=2)
        draw.line([x + s - 3, y + 7, x + s // 2, y + s // 2 + 2], fill=accent, width=2)
    elif kind == "wave":
        pts = [(x + 2, y + s // 2), (x + 7, y + 6), (x + 11, y + s - 6),
               (x + 15, y + 8), (x + 19, y + s // 2 + 4), (x + 23, y + 6),
               (x + s - 2, y + s // 2)]
        draw.line(pts, fill=accent, width=2, joint="curve")
        draw.line([x + 2, y + s - 3, x + s - 2, y + s - 3], fill=INK, width=1)
    elif kind == "people":
        for cx in (x + 7, x + s // 2, x + s - 7):
            draw.ellipse([cx - 4, y + 3, cx + 4, y + 11], fill=INK)
            draw.arc([cx - 6, y + 12, cx + 6, y + s - 2], 180, 360, fill=accent, width=2)
    elif kind == "chart":
        draw.line([x + 3, y + s - 4, x + s - 3, y + s - 4], fill=INK, width=2)
        draw.line([x + 3, y + s - 4, x + 3, y + 4], fill=INK, width=2)
        for i, h in enumerate((8, 13, 18)):
            bx = x + 7 + i * 7
            draw.rectangle([bx, y + s - 4 - h, bx + 5, y + s - 4], fill=accent)
    elif kind == "chip":
        draw.rectangle([x + 8, y + 8, x + s - 8, y + s - 8], outline=INK, width=2)
        draw.rectangle([x + 12, y + 12, x + s - 12, y + s - 12], fill=accent)
        for i in range(3):
            yy = y + 10 + i * 5
            draw.line([x + 2, yy, x + 8, yy], fill=INK, width=2)
            draw.line([x + s - 8, yy, x + s - 2, yy], fill=INK, width=2)
    elif kind == "flag":
        draw.line([x + 6, y + 3, x + 6, y + s - 3], fill=INK, width=2)
        draw.polygon([(x + 6, y + 4), (x + s - 3, y + 8), (x + 6, y + 13)],
                     fill=accent)


# ---------------------------------------------------------------- layout
def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    f_title = font(SERIF_B, 44)
    f_date = font(SANS_B, 17)
    f_claim = font(SANS_B, 17)
    f_kicker = font(SANS_B, 10)
    f_head = font(SERIF_B, 16)
    f_head_wide = font(SERIF_B, 17)
    f_deck = font(SANS, 12)
    f_section = font(SANS_B, 15)
    f_map_title = font(SANS_B, 14)
    f_legend = font(SANS, 11)
    f_legend_b = font(SANS_B, 11)
    f_also = font(SANS, 11)
    f_also_b = font(SANS_B, 11)
    f_footer = font(SANS, 11)
    f_num = font(SANS_B, 11)
    f_pin = font(SANS_B, 10)

    # ---- masthead ----
    title = "THE WORLD IN ONE PAGE"
    tw = f_title.getlength(title)
    d.text(((W - tw) / 2, 12), title, font=f_title, fill=INK)
    d.text((MARGIN, 66), "SATURDAY 21 NOVEMBER 2026", font=f_date, fill=INK)
    claim = "35 STORIES · 6 CONTINENTS"
    d.text((W - MARGIN - f_claim.getlength(claim), 66), claim, font=f_claim,
           fill=(179, 38, 30))
    d.line([MARGIN, 94, W - MARGIN, 94], fill=RULE, width=3)
    d.line([MARGIN, 99, W - MARGIN, 99], fill=RULE, width=1)

    # ---- lead panels: 3 + 4 + 4 ----
    lead_top = 108
    row_h = 132
    row_gap = 7
    rows = [LEADS[0:3], LEADS[3:7], LEADS[7:11]]
    y = lead_top
    for ri, row in enumerate(rows):
        n = len(row)
        pw = (W - 2 * MARGIN - (n - 1) * 6) // n
        for ci, (num, kicker, topic, headline, deck, icon) in enumerate(row):
            x = MARGIN + ci * (pw + 6)
            accent = TOPIC[topic]
            d.rectangle([x, y, x + pw, y + row_h], fill=PANEL, outline=PANEL_LINE)
            d.rectangle([x, y, x + 6, y + row_h], fill=accent)
            # top strip: number circle, kicker, icon
            d.ellipse([x + 12, y + 8, x + 34, y + 30], fill=INK)
            nt = str(num)
            d.text((x + 23 - f_num.getlength(nt) / 2, y + 10), nt, font=f_num,
                   fill=(255, 255, 255))
            if f_kicker.getlength(kicker) > pw - 84:
                raise SystemExit("OVERFLOW kicker %d: %r" % (num, kicker))
            d.text((x + 40, y + 12), kicker, font=f_kicker, fill=accent)
            draw_icon(d, icon, x + pw - 38, y + 6, 28, accent)
            # headline (2 lines max) and deck (2 lines max)
            hf = f_head_wide if n == 3 else f_head
            hw = pw - 24
            hl = fit_lines(headline, hf, hw, 2, "headline %d" % num)
            hy = y + 38
            hy = draw_text_block(d, hl, hf, x + 12, hy, 20)
            dl = fit_lines(deck, f_deck, pw - 24, 2, "deck %d" % num)
            draw_text_block(d, dl, f_deck, x + 12, y + row_h - 38, 15, color=MUTED)
        y += row_h + row_gap
    map_top = y + 2

    # ---- map panel ----
    map_h = 208
    d.rectangle([MARGIN, map_top, W - MARGIN, map_top + map_h], fill=SEA,
                outline=PANEL_LINE)
    d.text((MARGIN + 10, map_top + 8), "WHERE IT HAPPENED", font=f_map_title,
           fill=INK)
    d.text((MARGIN + 10, map_top + 28),
           "Numbered pins match the lead stories above.",
           font=f_legend, fill=MUTED)

    map_x0, map_y0 = MARGIN + 8, map_top + 52
    map_w, map_h_in = 660, 148

    def proj(lon, lat):
        return (map_x0 + (lon + 180) / 360.0 * map_w,
                map_y0 + (75 - lat) / 135.0 * map_h_in)

    for name, poly in CONTINENTS.items():
        cont = CONTINENT_OF_POLY[name]
        fill = tint(CONTINENT[cont], LAND, 0.55)
        pts = [proj(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=fill, outline=tint(CONTINENT[cont], INK, 0.35))

    # pins with per-pin offsets
    for num, (lon, lat, dx, dy, _place) in sorted(PINS.items()):
        px, py = proj(lon, lat)
        cx, cy = px + dx, py + dy
        d.line([px, py, cx, cy], fill=INK, width=1)
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=INK)
        d.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=INK,
                  outline=(255, 255, 255), width=1)
        nt = str(num)
        d.text((cx - f_pin.getlength(nt) / 2, cy - 7), nt, font=f_pin,
               fill=(255, 255, 255))

    # legend: continents + topic key, side by side, inside the map panel
    lx = MARGIN + 690
    ly = map_top + 52
    d.text((lx, ly), "CONTINENTS", font=f_legend_b, fill=INK)
    ly2 = ly + 18
    for name, color in CONTINENT.items():
        d.rectangle([lx, ly2 + 1, lx + 10, ly2 + 11], fill=color)
        d.text((lx + 15, ly2), name, font=f_legend, fill=INK)
        ly2 += 16
    lx2 = lx + 145
    f_topic = font(SANS, 10)
    f_topic_b = font(SANS_B, 10)
    d.text((lx2, ly), "TOPIC COLOURS", font=f_topic_b, fill=INK)
    ly2 = ly + 18
    for key in ("conflict", "climate", "economy", "justice", "other"):
        d.rectangle([lx2, ly2 + 1, lx2 + 10, ly2 + 11], fill=TOPIC[key])
        d.text((lx2 + 15, ly2), TOPIC_NAME[key], font=f_topic, fill=INK)
        ly2 += 16
    # pin 4 note (Mercury has no Earth spot; pin sits on mission control)
    d.text((MARGIN + 10, map_top + map_h - 18),
           "Pin 4 sits on Darmstadt (ESOC): BepiColombo is bound for Mercury, not Earth.",
           font=f_legend, fill=MUTED)

    also_top = map_top + map_h + 12

    # ---- ALSO ON #12-35 ----
    d.text((MARGIN, also_top), "ALSO ON SATURDAY", font=f_section, fill=INK)
    d.line([MARGIN, also_top + 22, W - MARGIN, also_top + 22], fill=RULE, width=2)
    col_w = (W - 2 * MARGIN - 20) // 2
    row_y = also_top + 30
    row_h2 = 16
    for i, (num, region, topic, text) in enumerate(ALSO):
        col = i // 12
        r = i % 12
        x = MARGIN + col * (col_w + 20)
        yy = row_y + r * row_h2
        accent = TOPIC[topic]
        d.rectangle([x, yy + 2, x + 4, yy + 12], fill=accent)
        head = "%d. %s — " % (num, region)
        hw = f_also_b.getlength(head)
        if f_also_b.getlength(head) + f_also.getlength(text) > col_w - 10:
            raise SystemExit("OVERFLOW also %d: %s%s" % (num, head, text))
        d.text((x + 9, yy), head, font=f_also_b, fill=INK)
        d.text((x + 9 + hw, yy), text, font=f_also, fill=INK)

    # ---- footer ----
    fy = also_top + 30 + 12 * row_h2 + 8
    d.line([MARGIN, fy, W - MARGIN, fy], fill=RULE, width=1)
    d.text((MARGIN, fy + 7),
           "Every story above was reported on Saturday 21 November 2026; "
           "disputed claims are attributed to those who made them.",
           font=f_footer, fill=INK)
    d.text((MARGIN, fy + 23),
           "Sources: Reuters · AP · AFP · BBC · Al Jazeera · ESA · USGS · "
           "IGP · All times UTC unless stated.",
           font=f_footer, fill=MUTED)

    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "out"
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    img.save(path, "PNG")
    return path


if __name__ == "__main__":
    print(build())
