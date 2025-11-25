// Initialize hero slider once DOM content is ready
document.addEventListener("DOMContentLoaded", () => {
    const slides = Array.from(document.querySelectorAll(".hero__slide"));
    const dots = Array.from(document.querySelectorAll(".hero__dot"));
    const prevBtn = document.querySelector(".hero__control--prev");
    const nextBtn = document.querySelector(".hero__control--next");
    let current = 0;
    let autoplayTimer;

    // Activate a specific slide + indicator
    const activateSlide = (index) => {
        slides.forEach((slide, idx) => {
            slide.classList.toggle("is-active", idx === index);
        });
        dots.forEach((dot, idx) => {
            dot.classList.toggle("is-active", idx === index);
        });
        current = index;
    };

    // Move slider to the next item (looped)
    const goNext = () => {
        const next = (current + 1) % slides.length;
        activateSlide(next);
    };

    // Move slider to the previous item (looped)
    const goPrev = () => {
        const prev = (current - 1 + slides.length) % slides.length;
        activateSlide(prev);
    };

    // Start autoplay (pause when user interacts)
    const startAutoplay = () => {
        stopAutoplay();
        autoplayTimer = setInterval(goNext, 5000);
    };

    // Stop autoplay to avoid double timers
    const stopAutoplay = () => {
        if (autoplayTimer) {
            clearInterval(autoplayTimer);
            autoplayTimer = null;
        }
    };

    // Bind controls
    if (prevBtn && nextBtn) {
        prevBtn.addEventListener("click", () => {
            goPrev();
            startAutoplay();
        });
        nextBtn.addEventListener("click", () => {
            goNext();
            startAutoplay();
        });
    }

    // Bind dots (direct slide navigation)
    dots.forEach((dot, idx) => {
        dot.addEventListener("click", () => {
            activateSlide(idx);
            startAutoplay();
        });
    });

    // Kick things off
    activateSlide(current);
    startAutoplay();

    // Tab filtering mock: toggles active class only (placeholder for future data hook)
    const tabs = Array.from(document.querySelectorAll(".section-header__tab"));
    tabs.forEach((tab) => {
        tab.addEventListener("click", () => {
            tabs.forEach((inner) => inner.classList.remove("is-active"));
            tab.classList.add("is-active");
            // NOTE: 실제 데이터 연동 시 이 자리에서 Ajax/Fetch 등으로 콘텐츠를 교체하세요.
        });
    });

    // Product card click → navigate to detail page
    const cards = Array.from(document.querySelectorAll(".product-card[data-product-url]"));
    console.log(cards);
    console.log("test");
    cards.forEach((card) => {
        const url = card.dataset.productUrl;
        if (!url) return;
        card.style.cursor = "pointer";
        card.addEventListener("click", () => {
            console.log("123");
            window.location.href = url;
        });
    });
});
