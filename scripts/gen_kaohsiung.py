"""Generate a hacker-green Kaohsiung skyline footer (gradient/3D style) as SVG.

Landmarks: 85 Sky Tower (高 shape), Kaohsiung Eye ferris wheel, Music Center
(whale/wave), harbor gantry cranes, Love River reflection.
"""
from pathlib import Path
import math

W, H = 1000, 260
GY = 186  # ground / waterline
OUT = Path(__file__).resolve().parent.parent / "assets" / "kaohsiung-skyline.svg"
OUT.parent.mkdir(parents=True, exist_ok=True)

city = []   # above-water elements (reflected in the river)


def rect(x, y, w, h, fill, extra=""):
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" {extra}/>'


def windows(x, w, top, gy, step=10):
    out = []
    wy = top + 9
    while wy < gy - 5:
        wx = x + 5
        while wx < x + w - 4:
            if (int(wx) * 3 + int(wy)) % 5 == 0:
                out.append(f'<rect x="{wx:.0f}" y="{wy:.0f}" width="2.5" height="3.5" fill="#0f8" opacity="0.65"/>')
            wx += 8
        wy += step
    return "".join(out)


# ---- BACK layer: distant buildings (darker, atmospheric) ----
back = [(20, 40, 60), (70, 30, 92), (150, 46, 70), (210, 34, 110),
        (330, 40, 64), (560, 36, 100), (610, 46, 72), (680, 34, 120),
        (860, 40, 86), (915, 50, 60)]
for (x, w, h) in back:
    city.append(rect(x, GY - h, w, h, "url(#gFar)", 'opacity="0.7"'))

# ---- Music Center (whale / wave) — left waterfront ----
mc = ['<g opacity="0.95">']
mc.append(f'<path d="M40,{GY} Q70,{GY-46} 105,{GY-20} Q135,{GY-52} 168,{GY} Z" fill="url(#gWave)"/>')
mc.append(f'<path d="M95,{GY} Q120,{GY-30} 150,{GY-14} Q175,{GY-40} 205,{GY} Z" fill="url(#gWave2)" opacity="0.9"/>')
mc.append('</g>')
city += mc

# ---- MID/front generic buildings (gradient, lit-left) ----
front = [(255, 30, 78), (288, 40, 120), (355, 26, 60), (388, 40, 96),
         (720, 30, 70), (826, 30, 96)]
for (x, w, h) in front:
    top = GY - h
    city.append(rect(x, top, w, h, "url(#gBld)"))
    city.append(f'<rect x="{x:.1f}" y="{top:.1f}" width="{w:.1f}" height="2.5" fill="#8dffc0" opacity="0.9"/>')  # lit top edge
    city.append(windows(x, w, top, GY))

# ---- 85 Sky Tower: single upper shaft that splits into two legs (iconic central void) ----
cx = 470
TOP = 36
merge_y = GY - 84             # legs split off below here
hw, leg_w = 25, 12
# upper single shaft
city.append(rect(cx - hw, TOP, 2 * hw, merge_y - TOP, "url(#g85)"))
# two legs; the gap between them (cx-13 .. cx+13) is the see-through void
city.append(rect(cx - hw, merge_y, leg_w, GY - merge_y, "url(#g85)"))
city.append(rect(cx + hw - leg_w, merge_y, leg_w, GY - merge_y, "url(#g85)"))
# tapered cap + antenna
city.append(f'<polygon points="{cx-hw},{TOP} {cx+hw},{TOP} {cx+8},{TOP-18} {cx-8},{TOP-18}" fill="url(#g85)"/>')
city.append(f'<rect x="{cx-1.5}" y="{TOP-56}" width="3" height="38" fill="#0f8"/>')
city.append(f'<circle cx="{cx}" cy="{TOP-58}" r="3.2" fill="#aaffcc"/>')
# lit left edges (3D) + windows on the upper shaft
city.append(f'<rect x="{cx-hw}" y="{TOP}" width="2.5" height="{merge_y-TOP}" fill="#8dffc0" opacity="0.85"/>')
city.append(f'<rect x="{cx-hw}" y="{merge_y}" width="2" height="{GY-merge_y}" fill="#7dffb0" opacity="0.7"/>')
city.append(f'<rect x="{cx+hw-leg_w}" y="{merge_y}" width="2" height="{GY-merge_y}" fill="#7dffb0" opacity="0.6"/>')
city.append(windows(cx - hw, 2 * hw, TOP + 16, merge_y - 6, step=12))

# ---- Kaohsiung Eye ferris wheel (right, on a mall block) ----
wx, wy, r = 700, GY - 96, 40
# support building
city.append(rect(wx - 40, GY - 58, 96, 58, "url(#gBld)"))
city.append(windows(wx - 40, 96, GY - 58, GY))
wheel = ['<g stroke-linecap="round">']
wheel.append(f'<line x1="{wx-18}" y1="{GY}" x2="{wx}" y2="{wy}" stroke="#0a7d4a" stroke-width="3"/>')
wheel.append(f'<line x1="{wx+18}" y1="{GY}" x2="{wx}" y2="{wy}" stroke="#0a7d4a" stroke-width="3"/>')
for k in range(12):
    a = math.pi * k / 6
    wheel.append(f'<line x1="{wx}" y1="{wy}" x2="{wx+r*math.cos(a):.1f}" y2="{wy+r*math.sin(a):.1f}" stroke="#1fd65f" stroke-width="1" opacity="0.7"/>')
wheel.append(f'<circle cx="{wx}" cy="{wy}" r="{r}" fill="none" stroke="#22ff88" stroke-width="2.5"/>')
wheel.append(f'<circle cx="{wx}" cy="{wy}" r="{r-7}" fill="none" stroke="#0a7d4a" stroke-width="1" opacity="0.6"/>')
for k in range(12):
    a = math.pi * k / 6
    wheel.append(f'<circle cx="{wx+r*math.cos(a):.1f}" cy="{wy+r*math.sin(a):.1f}" r="2.4" fill="#aaffcc"/>')
wheel.append(f'<circle cx="{wx}" cy="{wy}" r="4" fill="#8dffc0"/>')
wheel.append('</g>')
city += wheel

# ---- Harbor gantry cranes (far right) ----
def crane(bx):
    g = ['<g stroke="#12b060" fill="url(#gCrane)">']
    g.append(rect(bx, GY - 92, 8, 92, "url(#gCrane)"))        # leg 1
    g.append(rect(bx + 40, GY - 92, 8, 92, "url(#gCrane)"))   # leg 2
    g.append(rect(bx - 18, GY - 96, 92, 7, "url(#gCrane)"))   # boom
    g.append(f'<line x1="{bx+4}" y1="{GY-92}" x2="{bx+58}" y2="{GY-116}" stroke="#12b060" stroke-width="3"/>')  # back stay
    g.append(rect(bx - 12, GY - 96, 6, 22, "#0a7d4a"))        # trolley/hoist
    g.append('</g>')
    return "".join(g)
city.append(crane(880))
city.append(crane(936))

# ---- assemble ----
city_svg = f'<g id="city">{"".join(city)}</g>'

# reflection in the Love River
reflection = (
    f'<g clip-path="url(#water)">'
    f'<use href="#city" transform="matrix(1,0,0,-1,0,{2*GY})" opacity="0.20"/>'
    f'<rect x="0" y="{GY}" width="{W}" height="{H-GY}" fill="url(#gFade)"/>'
)
for i in range(6):
    ry = GY + 8 + i * 8
    reflection += f'<rect x="0" y="{ry}" width="{W}" height="2.5" fill="#010604" opacity="0.55"/>'
reflection += '</g>'

ground = (
    f'<rect x="0" y="{GY}" width="{W}" height="2.5" fill="#00ff66" opacity="0.9"/>'
    f'<rect x="0" y="{GY}" width="{W}" height="3" fill="#7dffb0" opacity="0.5"/>'
)

label = (f'<text x="26" y="{H-14}" font-family="\'Share Tech Mono\', monospace" font-size="15" '
         f'fill="#4dffa6" opacity="0.9">clarke@kaohsiung:~$ <tspan fill="#8dffc0">./hello_world</tspan></text>')

defs = f'''<defs>
  <linearGradient id="gBld" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#1fd65f"/><stop offset="1" stop-color="#053322"/></linearGradient>
  <linearGradient id="gFar" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#0a5c2e"/><stop offset="1" stop-color="#02150c"/></linearGradient>
  <linearGradient id="g85" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#4dffa0"/><stop offset="0.5" stop-color="#12b060"/><stop offset="1" stop-color="#053d24"/></linearGradient>
  <linearGradient id="gWave" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#22ff88"/><stop offset="1" stop-color="#0a5c2e"/></linearGradient>
  <linearGradient id="gWave2" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#12b060"/><stop offset="1" stop-color="#053322"/></linearGradient>
  <linearGradient id="gCrane" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#1fd65f"/><stop offset="1" stop-color="#0a5c2e"/></linearGradient>
  <linearGradient id="gFade" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#010604" stop-opacity="0.1"/><stop offset="1" stop-color="#010604" stop-opacity="0.95"/></linearGradient>
  <radialGradient id="glow" cx="0.5" cy="0.1" r="0.9">
    <stop offset="0" stop-color="#00ff66" stop-opacity="0.13"/><stop offset="1" stop-color="#00ff66" stop-opacity="0"/></radialGradient>
  <clipPath id="water"><rect x="0" y="{GY}" width="{W}" height="{H-GY}"/></clipPath>
</defs>'''

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
       f'aria-label="Kaohsiung skyline">{defs}'
       f'<rect x="0" y="0" width="{W}" height="{H}" rx="10" fill="#010604"/>'
       f'<rect x="0" y="0" width="{W}" height="{H}" rx="10" fill="url(#glow)"/>'
       f'{city_svg}{ground}{reflection}{label}</svg>')
OUT.write_text(svg, encoding="utf-8")
print("wrote", OUT, len(svg), "bytes")
