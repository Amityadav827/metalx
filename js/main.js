/* ═══════════════════════════════════════════════
   MetalX — main.js
   ═══════════════════════════════════════════════ */
(function () {
    'use strict';

    /* ────────────────────────────────────────────
       HERO CAROUSEL
    ──────────────────────────────────────────── */
    const carousel = document.getElementById('heroCarousel');

    if (carousel) {
        const slides = carousel.querySelectorAll('.carousel-slide');
        const dots = carousel.querySelectorAll('.carousel-dot');
        const prevBtn = document.getElementById('carouselPrev');
        const nextBtn = document.getElementById('carouselNext');
        const counter = document.getElementById('currentSlide');
        const counterTotal = carousel.querySelector('.counter-total');
        const progBar = document.getElementById('progressBar');

        const TOTAL = slides.length;
        const AUTO_DELAY = 5500;  // ms per slide
        const PROG_DUR = AUTO_DELAY;

        let current = 0;
        let activeIndexes = Array.from(slides, function (_, i) { return i; });
        let autoTimer = null;
        let progTimer = null;
        let isAnimating = false;

        function activePosition(index) {
            const pos = activeIndexes.indexOf(index);
            return pos === -1 ? 0 : pos;
        }

        function nextFiltered(delta) {
            const pos = activePosition(current);
            const nextPos = (pos + delta + activeIndexes.length) % activeIndexes.length;
            return activeIndexes[nextPos];
        }

        function updateCounter() {
            if (counter) counter.textContent = String(activePosition(current) + 1).padStart(2, '0');
            if (counterTotal) counterTotal.textContent = String(activeIndexes.length).padStart(2, '0');
        }

        function setCategory(category) {
            activeIndexes = Array.from(slides).reduce(function (list, slide, i) {
                const cats = (slide.dataset.category || '').split(' ');
                if (!category || cats.includes(category)) list.push(i);
                return list;
            }, []);
            if (!activeIndexes.length) activeIndexes = Array.from(slides, function (_, i) { return i; });

            dots.forEach(function (dot, i) {
                const visible = activeIndexes.includes(i);
                dot.hidden = !visible;
                dot.setAttribute('aria-hidden', visible ? 'false' : 'true');
            });

            updateCounter();
        }

        /* -- go to slide n -- */
        function goTo(n, direction) {
            if (isAnimating || n === current) return;
            isAnimating = true;

            // outgoing slide
            slides[current].classList.remove('active');
            slides[current].classList.add('prev');
            dots[current].classList.remove('active');
            dots[current].setAttribute('aria-selected', 'false');

            current = (n + TOTAL) % TOTAL;

            // incoming slide
            slides[current].classList.add('active');
            slides[current].classList.remove('prev');
            dots[current].classList.add('active');
            dots[current].setAttribute('aria-selected', 'true');

            // counter
            updateCounter();

            // clean up prev class after transition
            setTimeout(function () {
                carousel.querySelectorAll('.carousel-slide.prev')
                    .forEach(function (s) { s.classList.remove('prev'); });
                isAnimating = false;
            }, 1200);
        }

        /* -- progress bar -- */
        function startProgress() {
            if (progBar) {
                progBar.style.transition = 'none';
                progBar.style.width = '0%';
                // force reflow
                void progBar.offsetWidth;
                progBar.style.transition = 'width ' + PROG_DUR + 'ms linear';
                progBar.style.width = '100%';
            }
        }

        /* -- auto play -- */
        function startAuto() {
            if (carousel.classList.contains('entrance-active')) return;
            stopAuto();
            startProgress();
            autoTimer = setTimeout(function () {
                goTo(nextFiltered(1));
                startAuto();
            }, AUTO_DELAY);
        }

        function stopAuto() {
            clearTimeout(autoTimer);
            clearTimeout(progTimer);
        }

        /* -- controls -- */
        if (prevBtn) {
            prevBtn.addEventListener('click', function () {
                goTo(nextFiltered(-1));
                stopAuto();
                startAuto();
            });
        }
        if (nextBtn) {
            nextBtn.addEventListener('click', function () {
                goTo(nextFiltered(1));
                stopAuto();
                startAuto();
            });
        }

        dots.forEach(function (dot, i) {
            dot.addEventListener('click', function () {
                if (!activeIndexes.includes(i)) return;
                goTo(i);
                stopAuto();
                startAuto();
            });
        });

        /* -- keyboard -- */
        document.addEventListener('keydown', function (e) {
            if (carousel.getBoundingClientRect().bottom <= 0) return;
            if (e.key === 'ArrowLeft') { goTo(nextFiltered(-1)); stopAuto(); startAuto(); }
            if (e.key === 'ArrowRight') { goTo(nextFiltered(1)); stopAuto(); startAuto(); }
        });

        /* -- touch/swipe -- */
        let touchStartX = 0;
        carousel.addEventListener('touchstart', function (e) {
            touchStartX = e.touches[0].clientX;
        }, { passive: true });
        carousel.addEventListener('touchend', function (e) {
            const diff = touchStartX - e.changedTouches[0].clientX;
            if (Math.abs(diff) > 50) {
                diff > 0 ? goTo(nextFiltered(1)) : goTo(nextFiltered(-1));
                stopAuto();
                startAuto();
            }
        }, { passive: true });

        /* -- pause on hover -- */
        carousel.addEventListener('mouseenter', stopAuto);
        carousel.addEventListener('mouseleave', startAuto);

        /* -- init -- */
        updateCounter();
        if (!carousel.classList.contains('entrance-active')) startAuto();

        /* -- entrance screen choice -- */
        document.addEventListener('mxChoice', function (e) {
            const detail = e.detail || {};
            stopAuto();
            setCategory(detail.category);
            if (detail.slide != null) {
                goTo(detail.slide);
            }
            updateCounter();
            startAuto();
        });
    }

    /* ────────────────────────────────────────────
       HEADER — scroll behaviour
    ──────────────────────────────────────────── */
    const header = document.querySelector('.site-header');
    const isHome = document.body.classList.contains('page-home');

    function onScroll() {
        if (!header) return;
        const scrolled = window.scrollY > 80;
        header.classList.toggle('scrolled', scrolled);
        if (isHome) header.classList.toggle('transparent', !scrolled);
    }

    if (isHome && header) header.classList.add('transparent');
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();

    /* ────────────────────────────────────────────
       MOBILE MENU
    ──────────────────────────────────────────── */
    const hamburgerBtn = document.querySelector('.hamburger-btn');
    const overlay = document.querySelector('.mobile-menu-overlay');
    const closeBtn = document.querySelector('.mobile-close');

    function openMenu() {
        if (!overlay) return;
        overlay.classList.add('open');
        document.body.style.overflow = 'hidden';
        if (hamburgerBtn) hamburgerBtn.setAttribute('aria-expanded', 'true');
    }
    function closeMenu() {
        if (!overlay) return;
        overlay.classList.remove('open');
        document.body.style.overflow = '';
        if (hamburgerBtn) hamburgerBtn.setAttribute('aria-expanded', 'false');
    }

    if (hamburgerBtn) hamburgerBtn.addEventListener('click', openMenu);
    if (closeBtn) closeBtn.addEventListener('click', closeMenu);
    if (overlay) overlay.addEventListener('click', function (e) {
        if (e.target === overlay) closeMenu();
    });
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && overlay && overlay.classList.contains('open')) closeMenu();
    });

    /* ── Desktop dropdown stability ── */
    document.querySelectorAll('.primary-nav .has-dropdown').forEach(function (dropdown) {
        let closeTimer;

        function openDropdown() {
            clearTimeout(closeTimer);
            dropdown.classList.add('dropdown-open');
        }

        function closeDropdown() {
            clearTimeout(closeTimer);
            closeTimer = setTimeout(function () {
                dropdown.classList.remove('dropdown-open');
            }, 400);
        }

        dropdown.addEventListener('pointerenter', openDropdown);
        dropdown.addEventListener('pointerleave', closeDropdown);
        dropdown.addEventListener('focusin', openDropdown);
        dropdown.addEventListener('focusout', closeDropdown);
    });

    /* ── Mobile sub-menu toggles ── */
    document.querySelectorAll('.mobile-nav-toggle').forEach(function (toggle) {
        toggle.addEventListener('click', function () {
            const sub = this.closest('.mobile-nav-item').querySelector('.mobile-sub-menu');
            const icon = this.querySelector('.toggle-icon');
            if (!sub) return;
            const open = sub.classList.toggle('open');
            if (icon) icon.textContent = open ? '−' : '+';
        });
    });

    /* ────────────────────────────────────────────
       PRODUCTS PAGE — filter tabs + load more
    ──────────────────────────────────────────── */
    const filterTabs = document.querySelectorAll('.filter-tab');
    const pxCards = Array.from(document.querySelectorAll('.px-card'));
    const loadBtn = document.getElementById('load-more-btn');
    const PER_PAGE = 12;

    let activeFilter = 'all';
    let visibleCount = PER_PAGE;

    function getFiltered() {
        if (activeFilter === 'all') return pxCards;
        return pxCards.filter(function (c) {
            return (c.dataset.cat || '').split(' ').includes(activeFilter);
        });
    }

    function renderProducts() {
        const filtered = getFiltered();
        pxCards.forEach(function (c) { c.classList.add('hidden'); });
        filtered.forEach(function (c, i) {
            if (i < visibleCount) c.classList.remove('hidden');
        });
        if (loadBtn) {
            loadBtn.style.display = filtered.length > visibleCount ? 'inline-block' : 'none';
        }
    }

    filterTabs.forEach(function (tab) {
        tab.addEventListener('click', function () {
            filterTabs.forEach(function (t) {
                t.classList.remove('active');
                t.setAttribute('aria-selected', 'false');
            });
            this.classList.add('active');
            this.setAttribute('aria-selected', 'true');
            activeFilter = this.dataset.filter;
            visibleCount = PER_PAGE;
            renderProducts();
        });
    });

    if (loadBtn) {
        loadBtn.addEventListener('click', function () {
            visibleCount += PER_PAGE;
            renderProducts();
        });
    }

    if (pxCards.length) renderProducts();

    /* ────────────────────────────────────────────
       SCROLL-TRIGGERED FADE-UP
    ──────────────────────────────────────────── */
    const fadeObserver = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                fadeObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1, rootMargin: '0px 0px -48px 0px' });

    document.querySelectorAll('.fade-up').forEach(function (el) {
        fadeObserver.observe(el);
    });

    /* ────────────────────────────────────────────
       HASH ANCHOR SCROLL (products page)
    ──────────────────────────────────────────── */
    if (window.location.hash) {
        const target = document.querySelector(window.location.hash);
        if (target) {
            setTimeout(function () {
                const offset = (header ? header.offsetHeight : 72) + 24;
                window.scrollTo({ top: target.offsetTop - offset, behavior: 'smooth' });
            }, 150);
        }
    }

})();
