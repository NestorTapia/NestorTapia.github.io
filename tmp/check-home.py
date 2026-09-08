import json
from playwright.sync_api import sync_playwright


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page()
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    for width, height in [(1440, 900), (390, 844), (320, 740), (768, 1024)]:
        page.set_viewport_size({"width": width, "height": height})
        page.goto("http://localhost/portafolio/", wait_until="networkidle")
        page.wait_for_timeout(1500)
        page.screenshot(path=f"tmp/home-{width}.png")
        assert "Desarrollador" in page.locator("h1").inner_text()
        assert page.locator("[data-filter]").count() == 0
        assert page.locator(".work-role").count() == 3
        for role in page.locator(".work-role p").all_text_contents():
            assert "backend" in role.lower()
        for section in ["#proyectos", "#habilidades", "#metodo", "#contacto"]:
            page.locator(section).scroll_into_view_if_needed()
            page.wait_for_timeout(2100)
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(600)
        page.screenshot(path=f"tmp/home-full-{width}.png", full_page=True)
        dimensions = page.evaluate("""() => ({
            width: innerWidth,
            scrollWidth: document.documentElement.scrollWidth,
            images: [...document.images].map(i => ({src: i.getAttribute('src'), loaded: i.complete && i.naturalWidth > 0})),
            overflow: [...document.querySelectorAll('main *, header *')].filter(e => {
                const r = e.getBoundingClientRect();
                return r.width > 0 && (r.right > innerWidth + 1 || r.left < -1);
            }).map(e => e.className)
        })""")
        print(json.dumps(dimensions))
        assert dimensions["scrollWidth"] == width, dimensions
        assert all(image["loaded"] for image in dimensions["images"])
        page.locator(".work-demiplie .work-media").click()
        page.wait_for_url("**/proyecto.php?slug=demiplie")
        assert page.locator("h1").count() == 1
    page.emulate_media(reduced_motion="reduce")
    page.goto("http://localhost/portafolio/", wait_until="networkidle")
    assert page.locator(".work.reveal:not(.is-visible)").count() == 0
    page.keyboard.press("Tab")
    assert page.locator(".skip-link").evaluate("e => e === document.activeElement")
    for slug in ["demiplie", "florexpress", "mettatalk"]:
        page.goto(f"http://localhost/portafolio/proyecto.php?slug={slug}", wait_until="domcontentloaded")
        assert "Backend" in page.locator(".case-summary-card").inner_text()
        assert page.evaluate("document.documentElement.scrollWidth === innerWidth")
        page.screenshot(path=f"tmp/case-{slug}-mobile.png")
    assert not errors, errors
    print("PASS: responsive layout, images, backend in all projects, case links, reduced motion, keyboard and no JS errors")
    browser.close()
