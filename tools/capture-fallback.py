from playwright.sync_api import sync_playwright


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.goto("http://localhost/portafolio/", wait_until="networkidle")
    scene = page.locator("#architecture-scene")
    scene.wait_for(state="visible")
    page.wait_for_timeout(1200)
    scene.screenshot(path="assets/architecture-fallback.png")
    browser.close()
