from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome', headless=True)
    for width in [1440, 390]:
        page = browser.new_page(viewport={'width': width, 'height': 900})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto('http://localhost/portafolio/', wait_until='networkidle')
        assert page.locator('.scene-control, .scene-switcher').count() == 0
        canvas = page.locator('#architecture-scene.scene-ready canvas')
        canvas.scroll_into_view_if_needed()
        page.wait_for_timeout(350)
        first = canvas.screenshot(path=f'tmp/core-only-{width}.png')
        page.wait_for_timeout(250)
        assert first != canvas.screenshot(), 'Core should animate'
        page.emulate_media(reduced_motion='reduce')
        page.wait_for_timeout(350)
        still = canvas.screenshot()
        page.wait_for_timeout(250)
        assert still == canvas.screenshot(), 'Respect reduced motion'
        assert page.evaluate('document.documentElement.scrollWidth === innerWidth')
        assert not errors, errors
        page.close()
    browser.close()
    print('PASS: core only, no controls, animation and reduced motion, desktop and mobile.')
