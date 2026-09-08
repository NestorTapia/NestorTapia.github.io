from playwright.sync_api import sync_playwright


BASE = 'http://127.0.0.1:8765/portafolio/'
PAGES = {
    'index.html': 3,
    'proyecto-demiplie.html': 23,
    'proyecto-florexpress.html': 14,
    'proyecto-mettatalk.html': 1,
}

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(channel='chrome', headless=True)
    for width in (1440, 390):
        for path, expected_images in PAGES.items():
            page = browser.new_page(viewport={'width': width, 'height': 900})
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            response = page.goto(BASE + path, wait_until='networkidle')
            assert response and response.ok, (path, response.status if response else None)
            assert page.locator('a[href*=".php"]').count() == 0, path
            assert page.locator('text=<?php').count() == 0, path
            assert page.evaluate('document.documentElement.scrollWidth === innerWidth'), (path, width)
            if path == 'index.html':
                assert page.locator('.work').count() == expected_images
                assert page.locator('.skills-list li').count() == 16
                assert page.locator('#architecture-scene.scene-ready canvas').count() == 1
            else:
                assert page.locator('[data-gallery-image]').count() == expected_images, path
                for image in page.locator('[data-gallery-image] img').all():
                    image.scroll_into_view_if_needed()
                    image.evaluate('(element) => element.decode()')
                assert page.locator('[data-gallery-image] img').evaluate_all(
                    'images => images.every(image => image.complete && image.naturalWidth > 0)'
                ), path
            assert not errors, (path, errors)
            page.close()
    browser.close()
    print('PASS: root HTML is PHP-free, responsive, and loads scenes, projects and galleries.')
