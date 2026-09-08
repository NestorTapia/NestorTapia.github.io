from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome', headless=True)
    page = browser.new_page(viewport={'width': 1280, 'height': 800})
    page.goto('http://localhost/portafolio/', wait_until='networkidle')
    card = page.locator('.work-mettatalk .work-media')
    card.scroll_into_view_if_needed()
    card.hover()
    page.wait_for_timeout(400)
    action = card.locator('.media-action')
    background = action.evaluate('(el) => getComputedStyle(el).backgroundColor')
    color = action.evaluate('(el) => getComputedStyle(el).color')
    assert background == 'rgb(255, 121, 93)', background
    assert color == 'rgb(7, 16, 21)', color
    assert action.locator('svg').count() == 1
    card.screenshot(path='tmp/project-hover.png')
    browser.close()
    print('PASS: project arrow remains visible on coral hover state.')
