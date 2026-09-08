import json
import base64
from playwright.sync_api import sync_playwright


def canvas_stats(page):
    encoded = base64.b64encode(page.locator('#architecture-scene canvas').screenshot()).decode('ascii')
    return page.evaluate("""async encoded => {
        const blob = await (await fetch(`data:image/png;base64,${encoded}`)).blob();
        const bitmap = await createImageBitmap(blob);
        const canvas = document.createElement('canvas');
        canvas.width = bitmap.width;
        canvas.height = bitmap.height;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(bitmap, 0, 0);
        const pixels = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
        const width = canvas.width;
        const height = canvas.height;
        let lit = 0;
        let cyan = 0;
        let coral = 0;
        for (let i = 0; i < pixels.length; i += 4) {
            const r = pixels[i], g = pixels[i + 1], b = pixels[i + 2], a = pixels[i + 3];
            if (a && r + g + b > 35) lit++;
            if (g > r * 1.1 && b > r) cyan++;
            if (r > g * 1.15 && r > b * 1.2) coral++;
        }
        return {width, height, lit, cyan, coral};
    }""", encoded)


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(channel='chrome', headless=True)
    errors = []

    for base in ['http://localhost/portafolio/', 'http://localhost/portafolio/docs/index.html']:
        for width, height in [(1440, 900), (390, 844)]:
            page = browser.new_page(viewport={'width': width, 'height': height})
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.goto(base, wait_until='networkidle')
            page.wait_for_timeout(900)
            assert page.locator('#architecture-scene.scene-ready canvas').count() == 1
            stats = canvas_stats(page)
            assert stats['lit'] > stats['width'] * stats['height'] * .02, stats
            assert stats['cyan'] > 100 and stats['coral'] > 100, stats
            assert page.evaluate('document.documentElement.scrollWidth === innerWidth')
            assert page.locator('.skills-list li').count() == 16
            assert page.locator('.work-role').count() == 3
            assert page.locator('.work img').count() == 3
            for item in page.locator('.work').all():
                item.scroll_into_view_if_needed()
                page.wait_for_timeout(250)
            assert page.locator('.work img').evaluate_all('imgs => imgs.every(img => img.complete && img.naturalWidth > 0)')
            page.evaluate('scrollTo(0, 0)')
            page.screenshot(path=f"tmp/final-{'static' if 'docs' in base else 'php'}-{width}.png", full_page=True)
            print(json.dumps({'base': base, 'viewport': width, 'canvas': stats}))
            page.close()

    page = browser.new_page(viewport={'width': 1280, 'height': 800})
    page.goto('http://localhost/portafolio/proyecto.php?slug=demiplie', wait_until='networkidle')
    first = page.locator('[data-gallery-image]').first
    first.click()
    assert page.locator('.image-viewer').evaluate('dialog => dialog.open')
    assert page.locator('.viewer-image').get_attribute('src') == first.get_attribute('data-gallery-image')
    page.keyboard.press('ArrowRight')
    assert page.locator('#viewer-position').inner_text().startswith('2 /')
    page.keyboard.press('Escape')
    assert not page.locator('.image-viewer').evaluate('dialog => dialog.open')

    page.goto('http://localhost/portafolio/docs/proyecto-demiplie.html', wait_until='networkidle')
    assert page.locator('a[href="index.html#proyectos"]').count() >= 1
    assert page.locator('[href*=".php"]').count() == 0
    assert not errors, errors
    print('PASS: WebGL pixels, responsive layout, static site, content, images and gallery viewer')
    browser.close()
