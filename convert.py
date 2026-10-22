from playwright.sync_api import sync_playwright
from PIL import Image
from pathlib import Path
import io

ROOT = Path(__file__).resolve().parent
SVGS = [ROOT / "dark_mode.svg", ROOT / "light_mode.svg"]
CYCLE_DURATION_MS = 6000
FRAME_DELAY_MS = 50
FRAME_COUNT = CYCLE_DURATION_MS // FRAME_DELAY_MS

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome")  # use the runner's preinstalled Chrome, skips downloading Chromium + apt deps
    for svg in SVGS:
        page = browser.new_page(viewport={"width": 1200, "height": 850})
        page.goto(svg.as_uri(), wait_until="networkidle")
        page.evaluate("document.documentElement.pauseAnimations()")

        frames = []
        for frame_index in range(FRAME_COUNT):
            timestamp_seconds = frame_index * FRAME_DELAY_MS / 1000
            page.evaluate("""async (time) => {
                document.documentElement.setCurrentTime(time);
                await new Promise(requestAnimationFrame);
            }""", timestamp_seconds)
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
