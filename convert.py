from playwright.sync_api import sync_playwright
from PIL import Image
from pathlib import Path
import io

ROOT = Path(__file__).resolve().parent
SVGS = [ROOT / "dark_mode.svg", ROOT / "light_mode.svg"]
FRAME_COUNT = 140
FRAME_DELAY_MS = 50

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome")  # use the runner's preinstalled Chrome, skips downloading Chromium + apt deps
    for svg in SVGS:
        page = browser.new_page(viewport={"width": 1200, "height": 850})
        page.goto(svg.as_uri(), wait_until="networkidle")

        frames = []
        for _ in range(FRAME_COUNT):
            page.wait_for_timeout(FRAME_DELAY_MS)
            frames.append(page.screenshot())

        name = svg.with_suffix(".webp")
        images = [Image.open(io.BytesIO(f)) for f in frames]
        images[0].save(
            name,
            save_all=True,
            append_images=images[1:],
            duration=FRAME_DELAY_MS,
            loop=0,
        )
        print(f"Saved {name}")
        page.close()

    browser.close()
