#!/usr/bin/env python3
"""THE WORLD TODAY - Sunday 22 November 2026. Stdlib only, deterministic."""
import os, struct, zlib

W, H = 1000, 1000
PAPER = (246, 241, 226); INK = (22, 22, 22); RED = (164, 28, 28)
BLUE = (52, 74, 112); GREY = (105, 105, 96); PANEL = (255, 253, 244)
TAN = (231, 222, 196); LGREY = (210, 205, 188)

px = bytearray(bytes(PAPER) * (W * H))

def set_px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3; px[i:i+3] = bytes(c)

def rect(x, y, w, h, c):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            set_px(xx, yy, c)

def hline(x, y, w, c, t=1):
    rect(x, y, w, t, c)

def vline(x, y, h, c, t=1):
    rect(x, y, t, h, c)

def box(x, y, w, h, c, t=2):
    hline(x, y, w, c, t); hline(x, y + h - t, w, c, t)
    vline(x, y, h, c, t); vline(x + w - t, y, h, c, t)

def circle(cx, cy, r, c):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                set_px(xx, yy, c)

def tri(x, y, s, c):
    for i in range(s):
        rect(x + i // 2, y + i, max(1, s - i), 1, c)

def ring(cx, cy, r, c, t=2):
    for yy in range(cy - r - t, cy + r + t + 1):
        for xx in range(cx - r - t, cx + r + t + 1):
            d = ((xx - cx) ** 2 + (yy - cy) ** 2) ** 0.5
            if abs(d - r) < t:
                set_px(xx, yy, c)

def diag(x0, y0, x1, y1, c, t=2):
    steps = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(steps + 1):
        xx = x0 + (x1 - x0) * i // steps
        yy = y0 + (y1 - y0) * i // steps
        rect(xx, yy, t, t, c)

def arc(cx, cy, r, c, t=2):
    # right-side arc (signal wave)
    for a in range(-55, 56):
        import math
        xx = int(cx + r * math.cos(math.radians(a)))
        yy = int(cy + r * math.sin(math.radians(a)))
        rect(xx, yy, t, t, c)

def arc_left(cx, cy, r, c, t=2):
    for a in range(125, 236):
        import math
        xx = int(cx + r * math.cos(math.radians(a)))
        yy = int(cy + r * math.sin(math.radians(a)))
        rect(xx, yy, t, t, c)

# ---- 5x7 bitmap font (rows of 5 bits) ----
G = {
'A':("01110","10001","10001","11111","10001","10001","10001"),
'B':("11110","10001","10001","11110","10001","10001","11110"),
'C':("01110","10001","10000","10000","10000","10001","01110"),
'D':("11100","10010","10001","10001","10001","10010","11100"),
'E':("11111","10000","10000","11110","10000","10000","11111"),
'F':("11111","10000","10000","11110","10000","10000","10000"),
'G':("01110","10001","10000","10111","10001","10001","01111"),
'H':("10001","10001","10001","11111","10001","10001","10001"),
'I':("01110","00100","00100","00100","00100","00100","01110"),
'J':("00111","00010","00010","00010","00010","10010","01100"),
'K':("10001","10010","10100","11000","10100","10010","10001"),
'L':("10000","10000","10000","10000","10000","10000","11111"),
'M':("10001","11011","10101","10101","10001","10001","10001"),
'N':("10001","11001","10101","10011","10001","10001","10001"),
'O':("01110","10001","10001","10001","10001","10001","01110"),
'P':("11110","10001","10001","11110","10000","10000","10000"),
'Q':("01110","10001","10001","10001","10101","10010","01101"),
'R':("11110","10001","10001","11110","10100","10010","10001"),
'S':("01111","10000","10000","01110","00001","00001","11110"),
'T':("11111","00100","00100","00100","00100","00100","00100"),
'U':("10001","10001","10001","10001","10001","10001","01110"),
'V':("10001","10001","10001","10001","10001","01010","00100"),
'W':("10001","10001","10001","10101","10101","11011","10001"),
'X':("10001","01010","00100","00100","01010","10001","10001"),
'Y':("10001","01010","00100","00100","00100","00100","00100"),
'Z':("11111","00001","00010","00100","01000","10000","11111"),
'0':("01110","10001","10011","10101","11001","10001","01110"),
'1':("00100","01100","00100","00100","00100","00100","01110"),
'2':("01110","10001","00001","00110","01000","10000","11111"),
'3':("11110","00001","00001","01110","00001","00001","11110"),
'4':("00010","00110","01010","10010","11111","00010","00010"),
'5':("11111","10000","11110","00001","00001","10001","01110"),
'6':("00110","01000","10000","11110","10001","10001","01110"),
'7':("11111","00001","00010","00100","01000","01000","01000"),
'8':("01110","10001","10001","01110","10001","10001","01110"),
'9':("01110","10001","10001","01111","00001","00010","01100"),
' ':("00000",)*7,
'.':("00000","00000","00000","00000","00000","01100","01100"),
',':("00000","00000","00000","00000","01100","00100","01000"),
'-':("00000","00000","00000","01110","00000","00000","00000"),
"'":("00100","00100","01000","00000","00000","00000","00000"),
':':("00000","01100","01100","00000","01100","01100","00000"),
'/':("00001","00010","00010","00100","01000","01000","10000"),
'+':("00000","00100","00100","01110","00100","00100","00000"),
'$':("00100","01111","10100","01110","00101","11110","00100"),
'%':("11001","11010","00010","00100","01000","01011","10011"),
'(':("00010","00100","01000","01000","01000","00100","00010"),
')':("01000","00100","00010","00010","00010","00100","01000"),
'!':("00100","00100","00100","00100","00100","00000","00100"),
'?':("01110","10001","00001","00110","00100","00000","00100"),
}

def tw(s, sc):
    return len(s) * (5 * sc + sc) - (sc if s else 0)

def draw_text(x, y, s, sc=1, c=INK, bold=False):
    s = s.upper()
    cx = x
    for ch in s:
        g = G.get(ch, G[' '])
        for r in range(7):
            for col in range(5):
                if g[r][col] == '1':
                    rect(cx + col * sc, y + r * sc, sc, sc, c)
                    if bold:
                        rect(cx + col * sc + sc // 2, y + r * sc, max(1, sc // 2), sc, c)
        cx += 6 * sc
    return cx

def centered(y, s, sc, c=INK, bold=False):
    draw_text((W - tw(s, sc)) // 2, y, s, sc, c, bold)

def wrap(s, sc, maxw):
    words, lines, cur = s.upper().split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if tw(t, sc) <= maxw:
            cur = t
        else:
            if cur: lines.append(cur)
            cur = w_
    if cur: lines.append(cur)
    return lines

def block(x, y, s, sc, maxw, c=INK, lh=None, maxlines=99, bold=False):
    lh = lh or (7 * sc + 3 * sc // 2 + 2)
    lines = wrap(s, sc, maxw)[:maxlines]
    for i, ln in enumerate(lines):
        draw_text(x, y + i * lh, ln, sc, c, bold)
    return y + len(lines) * lh

# ---- Masthead ----
centered(10, "THE WORLD TODAY", 2, RED, True)
centered(34, "SUNDAY 22 NOVEMBER 2026", 5, INK, True)
centered(78, "32 STORIES - 6 REGIONS - EVERY ONE FROM THIS SUNDAY", 2, BLUE)
hline(16, 104, W - 32, INK, 3); hline(16, 110, W - 32, RED, 1)

# Timeline strip
tl = [("OVERNIGHT", "CHINA HITS BACK ON FCC BAN"),
      ("MORNING", "AUKUS ROW - INDIA 629-6"),
      ("MIDDAY", "VOYAGER 1 NOW ONE LIGHT-DAY FROM EARTH"),
      ("EVENING", "THOUSANDS MARCH IN LISBON OVER LIVING COSTS")]
for i, (a, b) in enumerate(tl):
    x = 16 + i * 243
    rect(x, 116, 234, 42, TAN); box(x, 116, 234, 42, INK, 1)
    draw_text(x + 8, 121, a, 1, RED, True)
    block(x + 8, 133, b, 1, 218, INK, lh=10, maxlines=2)

# ---- Lead tier ----
leads = [
 ("MIDDLE EAST - CONFLICT", "BAHRAIN SAYS IRANIAN ATTACK HITS PLANT",
  "AIR DEFENCES INTERCEPT ATTACKS AS SMOKE RISES OVER INDUSTRIAL SITE.", "CONFIRMED - REUTERS"),
 ("ASIA - POLITICS", "CHINA OPPOSES US FCC BAN ON TELECOMS",
  "COMMERCE MINISTRY ON SUNDAY FIRMLY OPPOSES BAN ON DIRECT US NUMBERS.", "CONFIRMED - REUTERS"),
 ("OCEANIA - DEFENCE", "AUSTRALIA SLAMS US REPORT ON AUKUS",
  "MARLES CRITICISES CBO CLAIM PACT CUTS US ATTACK SUBMARINES.", "CONFIRMED - REUTERS"),
 ("EUROPE - CLIMATE", "FOSSIL FUEL FIGHT DEADLOCKS COP31",
  "NEARLY 200 COUNTRIES STUCK IN ANTALYA ON A NEW CLIMATE DEAL.", "CONFIRMED - BBC"),
]
for i, (tag, head, det, src) in enumerate(leads):
    x = 16 + i * 243; y = 168
    rect(x, y, 234, 262, PANEL); box(x, y, 234, 262, INK, 2)
    # illustration
    rect(x + 10, y + 10, 214, 66, TAN)
    if i == 0:
        # Factory: block + chimneys, smoke plume, starburst interception
        rect(x + 24, y + 50, 92, 20, INK)
        rect(x + 24, y + 46, 92, 4, INK)
        rect(x + 36, y + 26, 12, 24, INK)
        rect(x + 62, y + 32, 10, 18, INK)
        # windows
        rect(x + 82, y + 56, 8, 8, PANEL); rect(x + 96, y + 56, 8, 8, PANEL)
        # smoke plume from main chimney
        circle(x + 42, y + 20, 6, GREY); circle(x + 52, y + 16, 8, GREY)
        circle(x + 64, y + 14, 6, GREY); circle(x + 74, y + 16, 4, LGREY)
        # starburst / flak burst in sky to the right
        bcx, bcy = x + 168, y + 32
        circle(bcx, bcy, 5, RED)
        hline(bcx - 16, bcy - 1, 32, RED, 3); vline(bcx - 1, bcy - 16, 32, RED, 3)
        diag(bcx - 11, bcy - 11, bcx - 6, bcy - 6, RED, 3); diag(bcx + 6, bcy - 6, bcx + 11, bcy - 11, RED, 3)
        diag(bcx - 11, bcy + 11, bcx - 6, bcy + 6, RED, 3); diag(bcx + 6, bcy + 6, bcx + 11, bcy + 11, RED, 3)
        circle(x + 188, y + 56, 3, BLUE); circle(x + 140, y + 54, 3, BLUE)
    elif i == 1:
        # Telecom mast with signal arcs, prohibition circle + slash
        vline(x + 92, y + 24, 42, INK, 4)
        hline(x + 76, y + 34, 36, INK, 3); hline(x + 80, y + 46, 28, INK, 3)
        diag(x + 78, y + 66, x + 94, y + 48, INK, 3); diag(x + 108, y + 66, x + 94, y + 48, INK, 3)
        rect(x + 70, y + 66, 48, 3, INK)
        circle(x + 94, y + 22, 4, INK)
        arc(x + 94, y + 22, 10, BLUE, 2); arc(x + 94, y + 22, 17, BLUE, 2)
        arc_left(x + 94, y + 22, 10, BLUE, 2); arc_left(x + 94, y + 22, 17, BLUE, 2)
        # bold red prohibition over the mast on the right side
        ring(x + 156, y + 43, 24, RED, 4)
        diag(x + 139, y + 60, x + 173, y + 26, RED, 5)
    elif i == 2:
        # Submarine: hull, conning tower, periscope, waves
        # waves on surface (top) and below hull
        for wx in range(x + 22, x + 200, 18):
            hline(wx, y + 18, 10, BLUE, 2); hline(wx + 4, y + 21, 6, BLUE, 2)
            hline(wx, y + 68, 10, BLUE, 2); hline(wx + 4, y + 65, 6, BLUE, 2)
        # hull
        rect(x + 36, y + 48, 132, 14, BLUE)
        tri(x + 166, y + 48, 14, BLUE)
        rect(x + 28, y + 50, 10, 10, BLUE)
        # conning tower + periscope
        rect(x + 82, y + 36, 36, 12, BLUE)
        vline(x + 98, y + 24, 12, BLUE, 3); hline(x + 98, y + 24, 13, BLUE, 3)
        # portholes
        circle(x + 58, y + 55, 3, PANEL); circle(x + 78, y + 55, 3, PANEL)
        circle(x + 128, y + 55, 3, PANEL); circle(x + 148, y + 55, 3, PANEL)
    else:
        # Globe with lat/long arcs + thermometer beside it
        gcx, gcy = x + 78, y + 43
        circle(gcx, gcy, 25, BLUE); circle(gcx, gcy, 23, PANEL)
        # latitude lines (clipped chords)
        hline(gcx - 20, gcy - 12, 40, BLUE, 2); hline(gcx - 23, gcy, 46, BLUE, 2); hline(gcx - 20, gcy + 12, 40, BLUE, 2)
        # longitude arcs: vertical line + side arcs approximated by rings segments
        vline(gcx - 1, gcy - 23, 46, BLUE, 2)
        ring(gcx, gcy, 12, BLUE, 1)
        # equator emphasis
        hline(gcx - 23, gcy - 1, 46, BLUE, 1)
        # thermometer: tube, bulb, mercury, scale ticks
        tx = x + 150
        rect(tx, y + 18, 10, 36, INK); rect(tx + 2, y + 20, 6, 32, PANEL)
        rect(tx + 3, y + 32, 4, 20, RED)
        circle(tx + 5, y + 60, 9, INK); circle(tx + 5, y + 60, 6, RED)
        hline(tx + 12, y + 24, 10, INK, 2); hline(tx + 12, y + 34, 10, INK, 2); hline(tx + 12, y + 44, 10, INK, 2)
    circle(x + 22, y + 88, 11, RED)
    draw_text(x + 17, y + 84, str(i + 1), 1, PANEL, True)
    draw_text(x + 40, y + 84, tag, 1, RED, True)
    yy = block(x + 10, y + 104, head, 2, 214, INK, lh=18, maxlines=3, bold=True)
    block(x + 10, yy + 4, det, 1, 214, INK, lh=10, maxlines=4)
    draw_text(x + 10, y + 240, src, 1, BLUE, True)

# ---- Second tier ----
draw_text(16, 442, "AROUND THE WORLD", 2, RED, True); hline(16, 462, W - 32, INK, 2)
cells = [
 ("ASIA - SPORT", "INDIA 629-6 IN WELLINGTON", "PANT CENTURY - HIGHEST INDIA TALLY IN NZ."),
 ("AMERICAS - CRIME", "EL CHAPO ISIDRO ARRESTED", "FBI MOST-WANTED CARTEL BOSS HELD IN SHOOT-OUT."),
 ("AMERICAS - SECURITY", "FBI PROBES DATABASE HACK", "APPARENT HACK OF US CRIMINAL DATABASE."),
 ("AMERICAS - HEALTH", "ROUNDUP DEAL APPROVED", "JUDGE OKAYS 7.25BN DOLLAR CANCER SETTLEMENT."),
 ("AMERICAS - POLITICS", "MAMDANI RIKERS PLAN", "NEW YORK JAIL TO CLOSE BY 2032 UNDER PLAN."),
 ("EUROPE - POLITICS", "BLAIR WARNS ON EU RETURN", "UK SHOULD REJOIN ONLY IF IT LEADS ON TECH."),
 ("EUROPE - CULTURE", "CATHERINE ON CANCER FILM", "PRINCESS TALKS OPENLY IN BBC DOCUMENTARY."),
 ("ASIA - POLITICS", "CHAHAL JOINS BJP IN INDIA", "CRICKETER GIVEN ROLE IN PARTY OBC MORCHA."),
 ("MIDDLE EAST - POLITICS", "EX-PM BACKS EISENKOT", "FORMER ISRAELI PM SAYS NO TO NETANYAHU."),
 ("AFRICA - POLITICS", "NIGERIA YOUTH AND 2027", "FEWER YOUNG VOTERS REGISTER THAN IN 2023."),
]
for idx, (tag, head, det) in enumerate(cells):
    col, row = idx % 5, idx // 5
    x = 16 + col * 195; y = 470 + row * 88
    rect(x, y, 186, 80, PANEL); box(x, y, 186, 80, GREY, 1)
    draw_text(x + 7, y + 6, str(idx + 5), 1, RED, True)
    draw_text(x + 26, y + 6, tag, 1, BLUE, True)
    yy = block(x + 7, y + 20, head, 1, 172, INK, lh=10, maxlines=2, bold=True)
    block(x + 7, yy + 2, det, 1, 172, GREY, lh=10, maxlines=3)

# ---- Also on Sunday ----
draw_text(16, 656, "ALSO ON SUNDAY", 2, RED, True); hline(16, 676, W - 32, INK, 2)
also = [
 "PERU - 152 HOMES UNINHABITABLE IN REVISED QUAKE INVENTORY",
 "SAUDI ARABIA - FOUR FOG WARNINGS ISSUED, TWO ORANGE",
 "CROATIA - RALLY HELD OVER A PATIENT DEATH",
 "ITALY - DESIGNER PAOLO BULGARI HAS DIED",
 "FIJI - SUNDAY TIMES: COURiers PAID IN METH, PAPER SAYS",
 "FIJI - IRELAND BEAT FIJI A IN RUGBY, SAYS SUNDAY TIMES",
 "PORTUGAL - THOUSANDS MARCH IN LISBON ON LIVING COSTS",
 "USA - FIRST CHILD MEASLES DEATH IN VIRGINIA SINCE 1978",
 "SPACE - VOYAGER 1 NOW ONE LIGHT-DAY FROM EARTH",
 "UN - TALKS TO CONTINUE TOWARD 2028 LETHAL-WEAPONS DEAL",
 "ASIA - JAPAN AND INDIA DEEPEN DEFENCE COOPERATION",
 "TECH - TIKTOK LAUNCHES DEEPFAKE TOOL FOR PUBLIC FIGURES",
 "TRADE - INDIA-CANADA CEPA TALKS ROUND SIX ENDS IN DELHI",
 "INDIA - CHEETAH BIRTHS FOUR CUBS AT KUNO, COUNT NOW 62",
 "USA - NIKHIL GUPTA GIVEN 235 MONTHS IN MURDER PLOT CASE",
 "INDIA - MODI OPENS NITISH SETU AND BIHAR PROJECTS",
 "INDIA - BHASHINI AI PASSES 11 BILLION INFERENCES AT SUMMIT",
 "CULTURE - WASHINGTON HAIR LOCK SELLS FOR 4000 DOLLARS",
]
# fix accidental mixed case
also = [a.replace("COUriers", "COURIERS") for a in also]
for idx, item in enumerate(also):
    col, row = idx // 6, idx % 6
    x = 16 + col * 326; y = 684 + row * 24
    draw_text(x, y, str(idx + 15) + ".", 1, RED, True)
    block(x + 28, y, item, 1, 292, INK, lh=10, maxlines=2)

# ---- Date check ----
y = 836
rect(16, y, W - 32, 76, TAN); box(16, y, W - 32, 76, RED, 2)
draw_text(26, y + 8, "DATE CHECK - LEFT OUT ON PURPOSE: BROKE BEFORE SUNDAY", 1, RED, True)
block(26, y + 24, "ENGLAND 37-12 RECORD WIN OVER ALL BLACKS WAS SATURDAY 21 NOV. NIGERIA FUNERAL BOAT SANK FRIDAY - 24 TOLL CONFIRMED SATURDAY. KYIV BARRAGE, ICJ MYANMAR RULING AND SHENZHEN TRILATERAL WERE ALL 21 NOV.", 1, W - 52, INK, lh=10, maxlines=4)

# ---- Footer ----
hline(16, 924, W - 32, INK, 2)
centered(932, "SOURCES: REUTERS - BBC - AP VIA REPORTS - NDTV - INDIA TODAY - FIJI TIMES", 1, BLUE)
centered(948, "EVERY STORY HERE HAPPENED OR WAS FIRST REPORTED ON SUNDAY 22 NOVEMBER 2026.", 1, INK, True)
centered(964, "THE WORLD TODAY - SUNDAY EDITION - PAGE ONE OF ONE", 1, GREY)

# ---- PNG encode ----
raw = b"".join(b"\x00" + bytes(px[y * W * 3:(y + 1) * W * 3]) for y in range(H))
def chunk(t, d):
    c = struct.pack(">I", len(d)) + t + d
    return c + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
png = (b"\x89PNG\r\n\x1a\n"
       + chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
       + chunk(b"IDAT", zlib.compress(raw, 9))
       + chunk(b"IEND", b""))
out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
os.makedirs(out, exist_ok=True)
with open(os.path.join(out, "entry.png"), "wb") as f:
    f.write(png)
print("wrote", os.path.join(out, "entry.png"), len(png))
