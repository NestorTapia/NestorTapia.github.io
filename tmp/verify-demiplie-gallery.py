from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome', headless=True)
    for suffix in ['proyecto.php?slug=demiplie', 'docs/proyecto-demiplie.html']:
        for width in [1440, 390]:
            page = browser.new_page(viewport={'width': width, 'height': 900})
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.goto('http://localhost/portafolio/' + suffix, wait_until='networkidle')
            assert page.locator('.gallery-section').count() == 8
            shots = page.locator('[data-gallery-image]')
            assert shots.count() == 23
            for shot in shots.all():
                shot.scroll_into_view_if_needed()
                image = shot.locator('img')
                image.evaluate('(img) => img.decode()')
                assert 'demiplie-gallery-updated/' in image.get_attribute('src')
                assert image.evaluate('(img) => Math.abs(img.width / img.height - img.naturalWidth / img.naturalHeight) < .03')
            shots.first.click()
            assert page.locator('.image-viewer').evaluate('(d) => d.open')
            for index in range(1, 23):
                page.keyboard.press('ArrowRight')
            assert page.locator('#viewer-position').inner_text().startswith('23 / 23')
            page.keyboard.press('Escape')
            assert not page.locator('.image-viewer').evaluate('(d) => d.open')
            assert page.evaluate('document.documentElement.scrollWidth === innerWidth')
            page.locator('.gallery-section').last.screenshot(path=f'tmp/demiplie-python-{width}.png')
            assert not errors, errors
            page.close()
    page = browser.new_page()
    page.goto('http://localhost/portafolio/', wait_until='networkidle')
    assert page.locator('.work-demiplie img').get_attribute('src') == 'assets/projects/demiplie.png'
    browser.close()
    print('PASS: 23 images, 8 sections, original proportions, lightbox, original cover and static pages.')
