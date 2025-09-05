# scraper_playwright.py
from playwright.sync_api import sync_playwright
from pathlib import Path
import time, csv, sys, json

TARGET_URL = "https://watson.soletanchefreyssinet.com/rules"
TIMEOUT_MS = 45_000  # 45s

def save_debug(page, name):
    dbg = Path("debug"); dbg.mkdir(exist_ok=True)
    page.screenshot(path=dbg / f"{name}.png", full_page=True)
    (dbg / f"{name}.html").write_text(page.content(), encoding="utf-8")

def find_tree_frame(page):
    """Return a Frame (or Page) that contains the jstree elements."""
    # Try main page first
    if page.locator(".jstree, a.jstree-anchor, li.jstree-node").first.is_visible(timeout=1000):
        return page
    # Otherwise scan frames
    for frame in page.frames:
        try:
            if frame.locator(".jstree, a.jstree-anchor, li.jstree-node").first.is_visible(timeout=1000):
                return frame
        except:
            continue
    return None

with sync_playwright() as p:
    # Launch Chromium in headless mode with typical server flags
    browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
    # Use storage_state (auth.json) generated locally
    context = browser.new_context(storage_state="auth.json")
    page = context.new_page()

    page.goto(TARGET_URL, wait_until="domcontentloaded")
    save_debug(page, "01_after_nav")

    # Wait for any jstree marker in any frame
    tree_holder = find_tree_frame(page)
    if not tree_holder:
        # give time for lazy widgets
        page.wait_for_timeout(3000)
        tree_holder = find_tree_frame(page)

    if not tree_holder:
        save_debug(page, "02_tree_not_found")
        print("[scraper] Could not find jstree in page or iframes. Likely auth expired.", file=sys.stderr)
        sys.exit(2)

    # Expand any collapsed nodes
    # Click all expand toggles (jstree-ocl) that are visible a few times (in case of deep trees)
    for _ in range(3):
        toggles = tree_holder.locator("li.jstree-node.jstree-closed i.jstree-ocl")
        count = toggles.count()
        if count == 0:
            break
        for i in range(count):
            try:
                toggles.nth(i).click()
                page.wait_for_timeout(400)
            except:
                pass

    save_debug(page, "03_after_expand")

    # Collect countries + color codes
    rows = []
    anchors = tree_holder.locator("a.jstree-anchor")
    count = anchors.count()
    for i in range(count):
        a = anchors.nth(i)
        name = (a.inner_text(timeout=2000) or "").strip()
        style = ""
        try:
            icon = a.locator("i.jstree-themeicon").first
            style = icon.get_attribute("style") or ""
        except:
            pass
        if style and "url" in style and "#" in style:
            try:
                color_svg = style.split('url("')[1].split('")')[0]
                color_number = color_svg.split('#')[1]
                rows.append((name, color_number))
            except:
                continue

    # Save CSV
    out = Path("output"); out.mkdir(parents=True, exist_ok=True)
    with (out / "Country_Risk.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Country", "Type of Risk"])
        w.writerows(rows)

    print(f"[scraper] Saved {len(rows)} rows to output/Country_Risk.csv")
    context.close()
    browser.close()
