from statistics import median

from playwright.sync_api import sync_playwright


def check(page, width, height):
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.set_viewport_size({"width": width, "height": height})
    page.goto("http://127.0.0.1:8765/portafolio/index.html", wait_until="networkidle")

    styles = page.evaluate("""
        () => ({
            backdrop: getComputedStyle(document.querySelector('.topbar')).backdropFilter,
            grid: getComputedStyle(document.querySelector('.intro'), '::before').display,
            workVisibility: getComputedStyle(document.querySelector('.work')).contentVisibility,
            largeReveals: document.querySelectorAll('.work.reveal, .gallery-section.reveal, .video-showcase.reveal').length
        })
    """)
    assert styles["backdrop"] == "none", styles
    assert styles["grid"] == "none", styles
    assert styles["workVisibility"] == "auto", styles
    assert styles["largeReveals"] == 0, styles

    frame_times = page.evaluate("""
        () => new Promise(resolve => {
            document.documentElement.style.scrollBehavior = 'auto';
            const values = [];
            const distance = document.documentElement.scrollHeight - innerHeight;
            const duration = 1400;
            const start = performance.now();
            let previous = start;
            function step(now) {
                values.push(now - previous);
                previous = now;
                const progress = Math.min((now - start) / duration, 1);
                scrollTo(0, distance * progress);
                if (progress < 1) requestAnimationFrame(step);
                else resolve(values.slice(3));
            }
            requestAnimationFrame(step);
        })
    """)
    assert page.evaluate("scrollY > 0")
    assert not errors, errors
    return {
        "viewport": f"{width}x{height}",
        "frames": len(frame_times),
        "median_ms": round(median(frame_times), 2),
        "max_ms": round(max(frame_times), 2),
    }


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page()
    print(check(page, 1440, 900))
    print(check(page, 390, 844))
    browser.close()
