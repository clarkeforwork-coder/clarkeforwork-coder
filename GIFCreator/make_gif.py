"""Render index.html into ../header.gif (headless Chromium screencast + Pillow).

Usage:
    pip install playwright pillow
    playwright install chromium
    python make_gif.py

Captures the #stage element (800x387) for DURATION_MS, resamples to TARGET_FPS,
and writes an optimized animated GIF next to the repo root as header.gif.
"""
import io
import base64
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image

HERE = Path(__file__).resolve().parent
HTML = HERE / "index.html"
OUT = HERE.parent / "header.gif"

STAGE_W, STAGE_H = 800, 387
SCALE = 2
DURATION_MS = 6000
TARGET_FPS = 18
COLORS = 96

captured = []  # (timestamp_seconds, png_base64)

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(
        viewport={"width": STAGE_W + 40, "height": STAGE_H + 40},
        device_scale_factor=SCALE,
    )
    page.goto(HTML.as_uri())
    page.evaluate("document.fonts.ready")
    page.wait_for_timeout(800)
    page.reload()                       # restart animations at t=0 with fonts cached
    page.evaluate("document.fonts.ready")
    page.wait_for_timeout(250)

    box = page.eval_on_selector(
        "#stage",
        "el => { const r = el.getBoundingClientRect(); return {x:r.x, y:r.y, w:r.width, h:r.height}; }",
    )

    client = page.context.new_cdp_session(page)

    def on_frame(params):
        captured.append((params["metadata"]["timestamp"], params["data"]))
        try:
            client.send("Page.screencastFrameAck", {"sessionId": params["sessionId"]})
        except Exception:
            pass

    client.on("Page.screencastFrame", on_frame)
    client.send("Page.startScreencast", {
        "format": "png", "everyNthFrame": 1,
        "maxWidth": (STAGE_W + 40) * SCALE, "maxHeight": (STAGE_H + 40) * SCALE,
    })
    page.wait_for_timeout(DURATION_MS)
    client.send("Page.stopScreencast")
    browser.close()

t0 = captured[0][0]
times = [t - t0 for t, _ in captured]

# Derive the real screencast scale from the first frame (may be CSS px, not device px),
# then build the crop box from the stage's bounding rect. Do NOT assume device_scale_factor.
_probe = Image.open(io.BytesIO(base64.b64decode(captured[0][1])))
fw, fh = _probe.size
sx, sy = fw / (STAGE_W + 40), fh / (STAGE_H + 40)
crop = (
    round(box["x"] * sx), round(box["y"] * sy),
    round((box["x"] + box["w"]) * sx), round((box["y"] + box["h"]) * sy),
)
print(f"frame={fw}x{fh}  scale=({sx:.2f},{sy:.2f})  crop={crop}")

# Resample to TARGET_FPS: nearest frame to each evenly spaced tick
step = 1.0 / TARGET_FPS
picks, ti, j = [], 0.0, 0
while ti <= times[-1]:
    while j + 1 < len(times) and times[j + 1] < ti:
        j += 1
    picks.append(j)
    ti += step
picks = [p for i, p in enumerate(picks) if i == 0 or p != picks[i - 1]]

frames = []
for idx in picks:
    img = Image.open(io.BytesIO(base64.b64decode(captured[idx][1]))).convert("RGB")
    frames.append(img.crop(crop).resize((STAGE_W, STAGE_H), Image.LANCZOS))

durations = [int(1000 / TARGET_FPS)] * len(frames)
pal = [f.quantize(colors=COLORS, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE) for f in frames]
pal[0].save(OUT, save_all=True, append_images=pal[1:],
            duration=durations, loop=0, disposal=2, optimize=True)

print(f"frames={len(frames)}  {times[-1]:.1f}s  {len(frames)/times[-1]:.1f}fps  "
      f"{OUT.stat().st_size/1e6:.2f}MB -> {OUT}")
