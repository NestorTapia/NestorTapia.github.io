from playwright.sync_api import sync_playwright

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 390, "height": 844})
    page.goto("http://127.0.0.1:8765/portafolio/proyecto-demiplie.html", wait_until="networkidle")
    print(page.evaluate("""
        () => ({
            viewport: innerWidth,
            scrollWidth: document.documentElement.scrollWidth,
            offenders: [...document.querySelectorAll('body *')]
                .map(element => {
                    const box = element.getBoundingClientRect();
                    return { tag: element.tagName, cls: element.className, left: box.left, right: box.right, width: box.width };
                })
                .filter(item => item.left < -1 || item.right > innerWidth + 1)
                .slice(0, 20)
        })
    """))
    browser.close()
