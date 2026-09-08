const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
window.lucide?.createIcons();

const progress = document.querySelector('.scroll-progress');
if (progress) {
    let progressFrame = 0;
    const updateProgress = () => {
        progressFrame = 0;
        const scrollable = document.documentElement.scrollHeight - innerHeight;
        progress.style.transform = `scaleX(${scrollable > 0 ? scrollY / scrollable : 0})`;
    };
    const requestProgressUpdate = () => {
        if (!progressFrame) progressFrame = requestAnimationFrame(updateProgress);
    };
    updateProgress();
    addEventListener('scroll', requestProgressUpdate, { passive: true });
    addEventListener('resize', requestProgressUpdate, { passive: true });
}

const revealTargets = document.querySelectorAll(
    '.workflow-step, .case-summary-card'
);

if (reduceMotion || !('IntersectionObserver' in window)) {
    revealTargets.forEach((target) => target.classList.add('is-visible'));
} else {
    revealTargets.forEach((target, index) => {
        target.classList.add('reveal');
        const delay = target.classList.contains('work')
            ? Math.min(index % 3, 2) * 55
            : Math.min(index % 4, 3) * 80;

        target.style.setProperty('--delay', `${delay}ms`);
    });

    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (!entry.isIntersecting) {
                return;
            }

            entry.target.classList.add('is-visible');
            observer.unobserve(entry.target);
        });
    }, {
        threshold: 0.08,
        rootMargin: '0px 0px -40px 0px',
    });

    revealTargets.forEach((target) => observer.observe(target));
}

const sectionLinks = [...document.querySelectorAll('.nav-links a[href^="#"]')];
if ('IntersectionObserver' in window && sectionLinks.length) {
    const activeSection = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (!entry.isIntersecting) return;
            sectionLinks.forEach(link => {
                if (link.hash === `#${entry.target.id}`) link.setAttribute('aria-current', 'location');
                else link.removeAttribute('aria-current');
            });
        });
    }, { rootMargin: '-15% 0px -60% 0px', threshold: 0 });
    sectionLinks.forEach(link => {
        const section = document.querySelector(link.hash);
        if (section) activeSection.observe(section);
    });
}

const viewer = document.querySelector('.image-viewer');
const galleryItems = [...document.querySelectorAll('[data-gallery-image]')];
if (viewer && galleryItems.length) {
    const image = viewer.querySelector('.viewer-image');
    const caption = viewer.querySelector('#viewer-caption');
    const position = viewer.querySelector('#viewer-position');
    const previous = viewer.querySelector('[data-viewer-prev]');
    const next = viewer.querySelector('[data-viewer-next]');
    let current = 0;

    function show(index) {
        current = Math.max(0, Math.min(galleryItems.length - 1, index));
        const item = galleryItems[current];
        image.src = item.dataset.galleryImage;
        image.alt = item.dataset.caption;
        caption.textContent = item.dataset.caption;
        position.textContent = `${current + 1} / ${galleryItems.length}`;
        previous.disabled = current === 0;
        next.disabled = current === galleryItems.length - 1;
    }

    galleryItems.forEach((item, index) => item.addEventListener('click', () => {
        show(index);
        viewer.showModal();
        document.body.classList.add('viewer-open');
    }));
    previous.addEventListener('click', () => show(current - 1));
    next.addEventListener('click', () => show(current + 1));
    viewer.querySelector('[data-viewer-close]').addEventListener('click', () => viewer.close());
    viewer.addEventListener('close', () => document.body.classList.remove('viewer-open'));
    viewer.addEventListener('click', event => { if (event.target === viewer) viewer.close(); });
    viewer.addEventListener('keydown', event => {
        if (event.key === 'ArrowRight') { event.preventDefault(); show(current + 1); }
        if (event.key === 'ArrowLeft') { event.preventDefault(); show(current - 1); }
    });
}
