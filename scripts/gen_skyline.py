"""Generate the hacker-green Taipei skyline footer as assets/taiwan-skyline.svg.

Pure Python (no deps). To turn the SVG into the PNG used by the README, open the
SVG in a browser and screenshot it, or rasterize with any SVG->PNG tool, e.g.:
    python scripts/gen_skyline.py
    # then rasterize assets/taiwan-skyline.svg -> assets/taiwan-skyline.png
"""
from pathlib import Path

W, H = 1000, 240
GY = 205  # ground baseline
OUT = Path(__file__).resolve().parent.parent / "assets" / "taiwan-skyline.svg"
OUT.parent.mkdir(parents=True, exist_ok=True)

parts = [
    f'<rect x="0" y="0" width="{W}" height="{H}" rx="10" fill="#010604"/>',
    f'<rect x="0" y="0" width="{W}" height="{H}" rx="10" fill="url(#glow)"/>',
]

# generic buildings behind Taipei 101: (x, width, height, antenna)
buildings = [
    (30, 46, 70, False), (82, 34, 110, True), (120, 40, 55, False),
    (165, 30, 95, False), (198, 52, 130, False), (255, 26, 72, True),
    (286, 44, 100, False), (335, 30, 60, False),
    (620, 40, 88, False), (665, 30, 120, True), (700, 48, 64, False),
    (755, 34, 108, False), (795, 44, 78, False), (845, 28, 132, True),
    (878, 46, 92, False), (930, 40, 66, False),
]
for (x, w, h, ant) in buildings:
    top = GY - h
    parts.append(f'<rect x="{x}" y="{top}" width="{w}" height="{h}" fill="url(#bld)"/>')
    if ant:
        cx = x + w / 2
        parts.append(f'<rect x="{cx-1}" y="{top-16}" width="2" height="16" fill="#0a5"/>')
    wy = top + 8
    while wy < GY - 6:
        wx = x + 6
        while wx < x + w - 4:
            if (int(wx) + int(wy)) % 7 == 0:
                parts.append(f'<rect x="{wx}" y="{wy}" width="3" height="4" fill="#0f6" opacity="0.7"/>')
            wx += 9
        wy += 11

# Taipei 101
cx = 480
base_half, seg_bottom, seg_h, n_seg = 34, 190, 15, 8
bh, th = 17, 25
parts.append(f'<rect x="{cx-base_half}" y="{seg_bottom}" width="{base_half*2}" height="{GY-seg_bottom}" fill="url(#t101)"/>')
parts.append(f'<polygon points="{cx-base_half},{seg_bottom} {cx-bh},{seg_bottom-10} {cx+bh},{seg_bottom-10} {cx+base_half},{seg_bottom}" fill="url(#t101)"/>')
y = seg_bottom - 10
for i in range(n_seg):
    yt = y - seg_h
    parts.append(f'<polygon points="{cx-bh},{y} {cx+bh},{y} {cx+th},{yt} {cx-th},{yt}" fill="url(#t101)"/>')
    y = yt
cap_top = y - 12
parts.append(f'<polygon points="{cx-bh},{y} {cx+bh},{y} {cx+6},{cap_top} {cx-6},{cap_top}" fill="url(#t101)"/>')
parts.append(f'<rect x="{cx-1.5}" y="{cap_top-40}" width="3" height="40" fill="#0f6"/>')
parts.append(f'<circle cx="{cx}" cy="{cap_top-42}" r="3" fill="#7dffb0"/>')

# ground glow + terminal label
parts.append(f'<rect x="0" y="{GY}" width="{W}" height="2" fill="#00ff41" opacity="0.9"/>')
parts.append(f'<rect x="0" y="{GY}" width="{W}" height="26" fill="url(#ground)"/>')
parts.append(
    f'<text x="24" y="{H-16}" font-family="\'Share Tech Mono\', monospace" font-size="15" '
    f'fill="#4dffa6" opacity="0.9">clarke@taipei:~$ <tspan fill="#7dffb0">./hello_world</tspan></text>'
)

defs = '''
<defs>
  <linearGradient id="t101" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#00ff88"/><stop offset="1" stop-color="#053d24"/>
  </linearGradient>
  <linearGradient id="bld" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#0a7d4a"/><stop offset="1" stop-color="#042b19"/>
  </linearGradient>
  <radialGradient id="glow" cx="0.5" cy="0" r="0.9">
    <stop offset="0" stop-color="#00ff41" stop-opacity="0.14"/><stop offset="1" stop-color="#00ff41" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="ground" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#00ff41" stop-opacity="0.35"/><stop offset="1" stop-color="#00ff41" stop-opacity="0"/>
  </linearGradient>
</defs>'''

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
       f'role="img" aria-label="Taipei skyline">{defs}{"".join(parts)}</svg>')
OUT.write_text(svg, encoding="utf-8")
print("wrote", OUT, len(svg), "bytes")
