#!/usr/bin/env python3
"""THE WORLD TODAY - Sunday 22 November 2026 in one image.

Deterministic, stdlib-only front page: own bitmap font, own drawing
primitives, own zlib PNG encoder. No files read, no network, no clock,
no randomness. Two runs produce byte-identical entry.png.
"""
import os
import struct
import zlib

W = 1000
H = 1000

# ---------------------------------------------------------------- palette
CREAM = (246, 239, 221)
PAPER = (251, 247, 233)
INK = (26, 23, 16)
SOFT = (74, 66, 52)
FAINT = (150, 138, 112)
RED = (163, 31, 31)
BLUE = (31, 74, 138)
TEAL = (18, 110, 102)
ORANGE = (214, 106, 24)
GOLD = (176, 128, 22)
PURPLE = (96, 54, 138)
GREEN = (44, 110, 44)
SKY = (198, 220, 232)
SMOKE = (120, 116, 108)

# ---------------------------------------------------------------- font
# 5x7 bitmap glyphs, '#' = ink. Uppercase only; text is uppercased on draw.
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "..##.", ".#...", "#....", "#####"),
    "3": ("#####", "...#.", "..#..", "...#.", "....#", "#...#", ".###."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".....", "..#.."),
    ",": (".....", ".....", ".....", ".....", "..#..", "..#..", ".#..."),
    ":": (".....", "..#..", "..#..", ".....", "..#..", "..#..", "....."),
    ";": (".....", "..#..", "..#..", ".....", "..#..", "..#..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "+": (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "$": ("..#..", ".####", "#.#.#", ".###.", "#.#.#", "####.", "..#.."),
    "%": ("##..#", "##.#.", "....#", "...#.", "..#..", ".#...", "#.##."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "*": (".....", "#.#.#", ".###.", "#####", ".###.", "#.#.#", "....."),
    "~": (".....", ".....", ".#.#.", "#.#.#", ".....", ".....", "....."),
    '"': ("#...#", "#...#", ".....", ".....", ".....", ".....", "....."),
    "\u00b7": (".....", ".....", ".....", "..#..", ".....", ".....", "....."),
}
ALIASES = {"\u2019": "'", "\u2018": "'", "\u2014": "-", "\u2013": "-",
           "\u2026": ".", "\u00a0": " "}


def clean(text):
    out = []
    for ch in text.upper():
        ch = ALIASES.get(ch, ch)
        out.append(ch if ch in FONT else " ")
    return "".join(out)


def text_w(text, sx):
    t = clean(text)
    if not t:
        return 0
    return len(t) * 6 * sx - sx


def draw_text(px, x, y, text, sx, sy, color, bold=False):
    t = clean(text)
    off = max(1, sx // 2) if bold else 0
    cx = x
    for ch in t:
        glyph = FONT[ch]
        for gy in range(7):
            row = glyph[gy]
            for gx in range(5):
                if row[gx] == "#":
                    px.fill(cx + gx * sx, y + gy * sy, sx, sy, color)
                    if bold:
                        px.fill(cx + gx * sx + off, y + gy * sy, sx, sy, color)
        cx += 6 * sx
    return cx - x


def draw_centered(px, cx, y, text, sx, sy, color, bold=False):
    w = text_w(text, sx)
    return draw_text(px, cx - w // 2, y, text, sx, sy, color, bold)


def wrap(text, max_chars):
    words = text.split()
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if len(trial) <= max_chars:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self):
        self.buf = bytearray(bytes(CREAM) * (W * H))

    def set(self, x, y, color):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            self.buf[i:i + 3] = bytes(color)

    def fill(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(W, x + w)
        y1 = min(H, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * W + x0) * 3
            self.buf[i:i + len(row)] = row

    def hline(self, x, y, w, color, th=1):
        self.fill(x, y, w, th, color)

    def vline(self, x, y, h, color, th=1):
        self.fill(x, y, th, h, color)

    def box(self, x, y, w, h, color, th=1):
        self.hline(x, y, w, color, th)
        self.hline(x, y + h - th, w, color, th)
        self.vline(x, y, h, color, th)
        self.vline(x + w - th, y, h, color, th)

    def circle(self, cx, cy, r, color, thick=0):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy)
                if thick:
                    if (r - thick) * (r - thick) <= d2 <= r * r:
                        self.set(xx, yy, color)
                elif d2 <= r * r:
                    self.set(xx, yy, color)

    def tri(self, x1, y1, x2, y2, x3, y3, color):
        minx = max(0, min(x1, x2, x3))
        maxx = min(W - 1, max(x1, x2, x3))
        miny = max(0, min(y1, y2, y3))
        maxy = min(H - 1, max(y1, y2, y3))
        d = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)
        if d == 0:
            return
        for yy in range(miny, maxy + 1):
            for xx in range(minx, maxx + 1):
                w1 = ((y2 - y3) * (xx - x3) + (x3 - x2) * (yy - y3)) / d
                w2 = ((y3 - y1) * (xx - x3) + (x1 - x3) * (yy - y3)) / d
                w3 = 1.0 - w1 - w2
                if w1 >= 0 and w2 >= 0 and w3 >= 0:
                    self.set(xx, yy, color)

    def line(self, x1, y1, x2, y2, color, th=2):
        steps = max(abs(x2 - x1), abs(y2 - y1), 1)
        for i in range(steps + 1):
            xx = x1 + (x2 - x1) * i // steps
            yy = y1 + (y2 - y1) * i // steps
            self.fill(xx - th // 2, yy - th // 2, th, th, color)


def png_bytes(px):
    raw = bytearray()
    stride = W * 3
    for yy in range(H):
        raw.append(0)
        raw += px.buf[yy * stride:(yy + 1) * stride]

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        c += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return c

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    out = b"\x89PNG\r\n\x1a\n"
    out += chunk(b"IHDR", ihdr)
    out += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    out += chunk(b"IEND", b"")
    return out


# ---------------------------------------------------------------- pictograms
def pic_cop31(px, x, y, w, h):
    """Globe with a cracked thermometer over it."""
    px.fill(x, y, w, h, (233, 226, 199))
    cx, cy, r = x + 92, y + h // 2, 37
    px.circle(cx, cy, r, BLUE)
    px.circle(cx, cy, r - 4, SKY)
    # continents: rough flat blobs
    for (bx, by, bw, bh) in ((cx - 30, cy - 26, 26, 14), (cx - 12, cy - 30, 16, 10),
                             (cx + 8, cy - 14, 24, 16), (cx - 26, cy + 2, 18, 20),
                             (cx + 16, cy + 12, 20, 12), (cx - 2, cy + 24, 12, 8)):
        px.fill(bx, by, bw, bh, GREEN)
    px.hline(cx - r, cy, 2 * r, BLUE, 2)
    px.vline(cx, cy - r, 2 * r, BLUE, 2)
    # thermometer, right side
    tx = x + 196
    px.fill(tx, y + 8, 20, 52, PAPER)
    px.box(tx, y + 8, 20, 52, INK, 2)
    px.fill(tx + 5, y + 30, 10, 26, RED)
    px.circle(tx + 10, y + 62, 13, PAPER)
    px.circle(tx + 10, y + 62, 10, RED)
    # crack across globe + thermometer
    pts = [(cx - 30, cy - 34), (cx - 12, cy - 12), (cx - 22, cy + 4),
           (cx - 2, cy + 22), (cx + 6, cy + 33)]
    for i in range(len(pts) - 1):
        px.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], RED, 3)
    px.line(tx + 2, y + 14, tx + 12, y + 28, INK, 3)
    px.line(tx + 12, y + 28, tx + 4, y + 40, INK, 3)
    # heat ticks
    for i in range(4):
        px.hline(tx + 26, y + 14 + i * 12, 10, RED, 3)


def pic_factory(px, x, y, w, h):
    """Candy factory with flames and smoke."""
    px.fill(x, y, w, h, (238, 228, 205))
    base = y + h - 6
    # smoke
    for (sx, sy, sr) in ((x + 66, y + 11, 10), (x + 84, y + 13, 12), (x + 104, y + 10, 9)):
        px.circle(sx, sy, sr, SMOKE)
    # chimney
    px.fill(x + 52, y + 18, 18, 40, (140, 74, 52))
    px.fill(x + 48, y + 14, 26, 6, INK)
    # sawtooth roof factory
    fx, fw = x + 30, 200
    fy = base - 44
    px.fill(fx, fy, fw, 44, (196, 178, 140))
    for i in range(4):
        px.tri(fx + i * 50, fy, fx + i * 50 + 25, fy - 16, fx + i * 50 + 50, fy, (120, 96, 64))
    px.box(fx, fy, fw, 44, INK, 2)
    # windows, some lit, some black
    for i in range(6):
        col = (250, 214, 110) if i % 2 == 0 else (52, 48, 44)
        px.fill(fx + 12 + i * 31, fy + 12, 18, 14, col)
    px.fill(fx + 84, base - 18, 30, 18, (84, 62, 40))
    # flames along the roof line
    for i in range(7):
        fx0 = fx + 14 + i * 27
        px.tri(fx0, fy - 2, fx0 + 9, fy - 22, fx0 + 18, fy - 2, ORANGE)
        px.tri(fx0 + 4, fy - 2, fx0 + 9, fy - 15, fx0 + 14, fy - 2, (245, 178, 44))
    # ground line + stretcher marks
    px.hline(x + 8, base, w - 16, INK, 2)
    px.fill(x + 244, base - 10, 34, 5, RED)
    px.fill(x + 250, base - 16, 5, 6, RED)
    px.fill(x + 264, base - 16, 5, 6, RED)


def pic_dymer(px, x, y, w, h):
    """Apartment block, one corner gone, rubble, drone overhead."""
    px.fill(x, y, w, h, (226, 230, 233))
    base = y + h - 4
    bx, bw = x + 74, 118
    by = y + 6
    bh = base - by - 10
    px.fill(bx, by, bw, bh, (178, 172, 160))
    px.box(bx, by, bw, bh, INK, 2)
    # window grid: 4 rows inside the block
    for r_i in range(4):
        for c_i in range(4):
            wx = bx + 10 + c_i * 27
            wy = by + 7 + r_i * 12
            if r_i < 2 and c_i > 1:
                continue  # blasted corner: no windows left
            col = (250, 226, 140) if (r_i + c_i) % 3 == 0 else (70, 76, 84)
            px.fill(wx, wy, 16, 8, col)
    # collapsed corner: jagged dark wedge
    px.tri(bx + bw - 52, by, bx + bw, by, bx + bw, by + 34, (52, 48, 44))
    px.tri(bx + bw - 52, by, bx + bw, by + 34, bx + bw - 20, by + 22, (52, 48, 44))
    px.line(bx + 14, by + 20, bx + 28, by + 34, INK, 3)
    px.line(bx + 28, by + 34, bx + 20, by + 46, INK, 3)
    # rubble pile
    for i in range(6):
        rx = bx - 8 + i * 22
        px.tri(rx, base, rx + 12, base - 12 - (i % 3) * 4, rx + 24, base, SMOKE)
    px.hline(x + 8, base, w - 16, INK, 2)
    # drone silhouette top right
    dx, dy = x + w - 52, y + 18
    px.fill(dx - 10, dy - 4, 20, 8, INK)
    for (ox, oy) in ((-22, -10), (14, -10), (-22, 6), (14, 6)):
        px.line(dx, dy, dx + ox + 4, dy + oy + 2, INK, 2)
        px.hline(dx + ox - 2, dy + oy, 12, INK, 3)
    px.vline(dx - 1, dy + 4, 10, RED, 3)


# ---------------------------------------------------------------- content
LEADS = [
    {
        "num": "01", "tag": "GLOBAL \u00b7 CLIMATE", "color": RED, "pic": pic_cop31,
        "head": "COP31 COLLAPSES: NO DEAL IN ANTALYA",
        "detail": "EU, Panama, Marshall Islands and Norway reject the "
                  "'Antalya Pact'; fossil-fuel language stripped. First "
                  "collapse since Copenhagen 2009.",
        "src": "CONFIRMED \u00b7 REUTERS / AP",
    },
    {
        "num": "02", "tag": "ASIA \u00b7 DISASTER", "color": ORANGE, "pic": pic_factory,
        "head": "JAVA CANDY-FACTORY FIRE: 24 BODY BAGS",
        "detail": "Police carry 24 body bags from the Milkita factory "
                  "ruins at Cikande, Banten. About 36 workers still "
                  "missing; victims named only by DNA.",
        "src": "CONFIRMED \u00b7 BBC / REUTERS",
    },
    {
        "num": "03", "tag": "EUROPE \u00b7 WAR", "color": BLUE, "pic": pic_dymer,
        "head": "RUSSIAN DRONE HITS DYMER FLATS",
        "detail": "Drone slams a five-storey block in Dymer, Kyiv "
                  "region, early Sunday: 2 dead, up to 14 - incl. two "
                  "children - trapped, Zelenskiy says.",
        "src": "CONFIRMED \u00b7 REUTERS / AJ",
    },
]

TIER2 = [
    ("04", "AFRICA \u00b7 WAR", RED,
     "SEA DRONES HIT CORVETTE AT BENGHAZI",
     "Suspected Ukrainian drones hit Russia's Merkury; capsizes, 10 hurt."),
    ("05", "EUROPE \u00b7 WAR", BLUE,
     "SPARTA II TOWED AWAY, STILL BURNING",
     "Russian cargo ship hit by drones in Gulf of Finland; Kaliningrad alert."),
    ("06", "EUROPE \u00b7 SECURITY", BLUE,
     "POLAND CONFIRMS KH-101 MISSILES",
     "Prosecutors: Friday's intruders were Russian Kh-101s. NATO meets Monday."),
    ("07", "MIDDLE EAST \u00b7 CONFLICT", PURPLE,
     "SETTLERS TORCH CARS NEAR RAMALLAH",
     "12 Palestinian vehicles burned in 4 villages; 'terrorism' - Eisenkot."),
    ("08", "AFRICA \u00b7 CONFLICT", RED,
     "DRONE STRIKES HIT KHARTOUM, UN BASE",
     "UN facility damaged, staff inside; 3 killed in Omdurman. Saudis condemn."),
    ("09", "OCEANIA \u00b7 DEFENCE", TEAL,
     "MARLES TO US ON AUKUS: 'WRONG'",
     "Defence minister rejects CBO report on sub sales, A$368bn programme."),
    ("10", "EUROPE \u00b7 SPORT", GREEN,
     "LIVERPOOL 4-0 MAN UNITED",
     "Yoro off in 8'; Szoboszlai, Wirtz, Ngumoha, Munoz score in rout."),
]

NUMBERS = [
    "24 BODY BAGS RECOVERED",
    "~36 WORKERS STILL MISSING",
    "4-0 AT ANFIELD, UTD 19TH",
    "$450M SKUBAL METS DEAL",
    "AQI 538 IN LAHORE",
    "258 HOUSE SEATS FOR DEMS",
    "90+ NATIONS SIGN PLEDGE",
]

BRIEFS_LEFT = [
    "11 ME CLAIM: HOUTHIS SAY THEY STRUCK SAUDI RABIGH OIL REFINERY",
    "12 ME CLAIM: IRAN SAYS 2 MORE TANKERS HIT MINES NEAR HORMUZ",
    "13 ME CLAIM: BAHRAIN SAYS IRANIAN DEBRIS FIRED A CIVIL SITE, 2 HURT",
    "14 ME FIRE AT HARTHA POWER PLANT NEAR BASRA KILLS 4, INJURES 35",
    "15 EU ZELENSKYY: CRIMEA BRIDGE STRIKES A 'FAIR RESPONSE'",
    "16 EU POLAND: RUSSIA TWICE TRIED TO KILL A RAPPER ON POLISH SOIL",
    "17 NA DEMOCRATS REACH 258 HOUSE SEATS, BIGGEST SINCE EARLY 1990S",
    "18 NA TRUMP ORDER: CONTRACTORS MUST FLAG OVERSIGHT REQUESTS",
    "19 NA TRUMP: WORK WITH DEMOCRATS ON 10% CREDIT-CARD RATE CAP",
    "20 NA DNI CLAYTON: 'PUTIN IS NOT AMERICA'S FRIEND' ON UKRAINE",
    "21 NA BESSENT: US SEEKS NVIDIA ANSWERS ON CHIP SALES TO CHINA",
    "22 NA FBI PROBES APPARENT HACK OF CRIMINAL-JUSTICE DATABASE",
    "23 NA ICE ARRESTS ON SEA-TAC JETWAY CONDEMNED; FATHER, GIRL HELD",
]
BRIEFS_RIGHT = [
    "24 NA COURT: PREGNANT-WORKER ACCOMMODATION LAW UNCONSTITUTIONAL",
    "25 AM MEXICO CAPTURES 'EL CHAPO ISIDRO' IN SINALOA RAID; 11 KILLED",
    "26 AS S. KOREA EDUCATION MINISTER QUITS OVER AI-CHEATING EXAM RULES",
    "27 AS LAHORE WORLD'S MOST POLLUTED MAJOR CITY SUNDAY, AQI 538",
    "28 AS OKINAWA FETES RESTORED SHURI CASTLE HALL, 7 YRS AFTER FIRE",
    "29 AF WHO: FIGHTING NEAR CONGO EBOLA ZONE DISRUPTED RESPONSE",
    "30 MK GULF BOURSES SLIDE: SAUDI -2.0%, EGYPT -2.9%, QATAR -1.6%",
    "31 TE ANTHROPIC'S RECORD IPO RAISES HOPES OF NONPROFIT WINDFALL",
    "32 SP VERSTAPPEN WINS LAS VEGAS GP THRILLER, 35 LEAD CHANGES",
    "33 SP KANSAS CITY WIN FIRST NWSL TITLE, 2-1 OVER WASHINGTON",
    "34 SP SKUBAL AGREES RECORD $450M, 9-YEAR DEAL WITH THE NY METS",
    "35 CU 'HUNGER GAMES' PREQUEL GOES BIG AT BOX OFFICE DESPITE GTA VI",
    "36 EU ITALIAN JEWELLER PAOLO BULGARI DIES AGED 89",
]

DATE_CHECK = ("NOT SUNDAY, SO NOT IN THIS PAPER: BEPICOLOMBO REACHED MERCURY - "
              "SAT 21 NOV \u00b7 GTA VI $3.79BN SALES RECORD - FRI 20 NOV \u00b7 FCC VOTE ON "
              "CHINESE TELECOMS - THU 19 NOV \u00b7 ICJ ROHINGYA RULING - THU 19 NOV \u00b7 "
              "PERU M6.7 QUAKE - FRI 20 NOV \u00b7 ENGLAND 37-12 ALL BLACKS AND NIGERIA "
              "BOAT - SAT 21 NOV \u00b7 SHENZHEN SUMMIT - 19-20 NOV")


# ---------------------------------------------------------------- layout
MX = 26            # side margin
CW = W - 2 * MX    # 948 content width


def masthead(px):
    px.hline(MX, 14, CW, INK, 3)
    px.hline(MX, 20, CW, INK, 1)
    draw_centered(px, W // 2, 27, "THE WORLD TODAY", 2, 2, INK, bold=True)
    draw_text(px, MX, 27, "EST. 2026", 1, 1, SOFT)
    draw_text(px, W - MX - text_w("ONE DAY, ONE PAGE", 1), 27,
              "ONE DAY, ONE PAGE", 1, 1, SOFT)
    # the date: biggest type on the page
    draw_centered(px, W // 2, 50, "SUNDAY 22 NOVEMBER 2026", 6, 6, INK, bold=True)
    draw_centered(px, W // 2, 100,
                  "36 STORIES \u00b7 7 REGIONS \u00b7 EVERY ONE FROM THIS SUNDAY",
                  1, 2, RED, bold=True)
    px.hline(MX, 122, CW, INK, 1)
    px.hline(MX, 126, CW, INK, 3)


def timeline(px):
    y = 136
    px.box(MX, y, CW, 34, INK, 1)
    px.fill(MX, y, 118, 34, INK)
    draw_text(px, MX + 10, y + 6, "SUNDAY IN", 1, 1, CREAM, bold=True)
    draw_text(px, MX + 10, y + 20, "UTC TIME", 1, 1, CREAM, bold=True)
    x0, x1 = MX + 140, W - MX - 16
    ty = y + 21
    px.hline(x0, ty, x1 - x0, SOFT, 2)
    for hr in range(0, 25, 4):
        tx = x0 + (x1 - x0) * hr // 24
        px.vline(tx, ty - 3, 7, INK, 2)
        lbl = "%02d:00" % hr
        draw_text(px, tx - text_w(lbl, 1) // 2, y + 25, lbl, 1, 1, SOFT)
    pins = [
        (1, "KHARTOUM DRONES", RED),
        (4, "DYMER HIT", BLUE),
        (9, "JAVA SEARCH", ORANGE),
        (15, "RAMALLAH ARSON", PURPLE),
        (19, "COP31 ENDS", RED),
        (22, "LIV 4-0 UTD", GREEN),
    ]
    for hr, lbl, col in pins:
        tx = x0 + (x1 - x0) * hr // 24
        px.circle(tx, ty, 4, col)
        lw = text_w(lbl, 1)
        lx = min(max(tx - lw // 2, MX + 124), W - MX - lw)
        draw_text(px, lx, y + 5, lbl, 1, 1, col, bold=True)


def leads(px):
    y = 182
    pw = (CW - 24) // 3
    for i, lead in enumerate(LEADS):
        x = MX + i * (pw + 12)
        if i:
            px.vline(x - 7, y, 196, FAINT, 1)
        lead["pic"](px, x, y, pw, 76)
        px.box(x, y, pw, 76, INK, 1)
        draw_text(px, x, y + 84, lead["num"] + "  " + lead["tag"], 1, 2,
                  lead["color"], bold=True)
        hy = y + 104
        for ln in wrap(lead["head"], 24):
            draw_text(px, x, hy, ln, 2, 2, INK, bold=True)
            hy += 17
        dy = hy + 3
        for ln in wrap(lead["detail"], 50):
            draw_text(px, x, dy, ln, 1, 2, SOFT)
            dy += 15
        draw_text(px, x, y + 196 - 7, lead["src"], 1, 1, lead["color"], bold=True)
    px.hline(MX, y + 204, CW, INK, 2)


def tier2(px):
    y = 398
    cw4 = (CW - 36) // 4
    cells = list(TIER2)
    for idx in range(8):
        col = idx % 4
        row = idx // 4
        x = MX + col * (cw4 + 12)
        yy = y + row * 84
        if col:
            px.vline(x - 7, yy, 74, FAINT, 1)
        if idx < 7:
            num, tag, color, head, det = cells[idx]
            draw_text(px, x, yy, num + " " + tag, 1, 1, color, bold=True)
            hy = yy + 11
            for ln in wrap(head, 37)[:2]:
                draw_text(px, x, hy, ln, 1, 2, INK, bold=True)
                hy += 16
            for ln in wrap(det, 36)[:2]:
                draw_text(px, x, hy, ln, 1, 1, SOFT)
                hy += 9
        else:
            px.fill(x - 4, yy - 4, cw4 + 8, 78, (238, 228, 199))
            px.box(x - 4, yy - 4, cw4 + 8, 78, INK, 1)
            draw_text(px, x + 4, yy + 2, "BY THE NUMBERS", 1, 2, RED, bold=True)
            ny = yy + 20
            for n in NUMBERS:
                draw_text(px, x + 4, ny, "\u00b7 " + n, 1, 1, INK)
                ny += 8
    px.hline(MX, y + 168, CW, INK, 2)


def briefs(px):
    y = 578
    draw_text(px, MX, y, "ALSO ON SUNDAY", 2, 2, INK, bold=True)
    note = "ITEMS 11-36 \u00b7 WIRES OF THE DAY"
    draw_text(px, W - MX - text_w(note, 1), y + 7, note, 1, 1, SOFT)
    px.hline(MX, y + 18, CW, FAINT, 1)
    colw = (CW - 16) // 2
    for j, group in enumerate((BRIEFS_LEFT, BRIEFS_RIGHT)):
        x = MX + j * (colw + 16)
        if j:
            px.vline(x - 9, y + 26, 268, FAINT, 1)
        yy = y + 26
        for b in group:
            num, rest = b.split(" ", 1)
            draw_text(px, x, yy, num, 1, 2, RED, bold=True)
            lines = wrap(rest, 71)
            for k, ln in enumerate(lines):
                draw_text(px, x + 20, yy + k * 16, ln, 1, 2, INK)
            yy += len(lines) * 16 + 5


def bottom(px):
    y = 884
    bw = 612
    px.box(MX, y, bw, 74, INK, 1)
    px.fill(MX, y, 118, 16, RED)
    draw_text(px, MX + 8, y + 4, "DATE CHECK", 1, 1, CREAM, bold=True)
    draw_text(px, MX + 126, y + 4, "FAMOUS STORIES WE LEFT OUT - WRONG DAY",
              1, 1, RED, bold=True)
    yy = y + 22
    for ln in wrap(DATE_CHECK, 99):
        draw_text(px, MX + 8, yy, ln, 1, 1, SOFT)
        yy += 9
    x2 = MX + bw + 14
    px.box(x2, y, W - MX - x2, 74, INK, 1)
    draw_text(px, x2 + 8, y + 6, "WHY TRUST THIS PAGE?", 1, 2, INK, bold=True)
    yy = y + 24
    for ln in wrap("EVERY ITEM ABOVE WAS REPORTED ON SUNDAY 22 NOV 2026. "
                   "UNCONFIRMED CLAIMS ARE LABELLED CLAIM.", 51):
        draw_text(px, x2 + 8, yy, ln, 1, 1, SOFT)
        yy += 9
    px.hline(MX, 968, CW, INK, 1)
    draw_centered(px, W // 2, 974,
                  "SOURCES: REUTERS \u00b7 AP \u00b7 BBC \u00b7 AL JAZEERA \u00b7 "
                  "EVERY STORY DATED SUNDAY 22 NOVEMBER 2026",
                  1, 2, INK, bold=True)


def main():
    px = Canvas()
    px.fill(0, 0, W, H, CREAM)
    masthead(px)
    timeline(px)
    leads(px)
    tier2(px)
    briefs(px)
    bottom(px)
    data = png_bytes(px)
    if os.path.isdir("/output"):
        path = "/output/entry.png"
    else:
        path = "./entry.png"
    with open(path, "wb") as fh:
        fh.write(data)


if __name__ == "__main__":
    main()
