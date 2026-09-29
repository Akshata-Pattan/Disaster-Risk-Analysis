document.addEventListener("DOMContentLoaded", () => {
    const score = document.querySelector(".score-ring");
    if (score) {
        const raw = document.querySelector(".score-ring strong")?.textContent || "0";
        const value = Math.max(0, Math.min(100, parseFloat(raw)));
        let deg = 0;
        const timer = setInterval(() => {
            deg += 4;
            if (deg >= value * 3.6) {
                deg = value * 3.6;
                clearInterval(timer);
            }
            score.style.background = `conic-gradient(var(--cyan) ${deg}deg, #182b42 ${deg}deg)`;
        }, 12);
    }

    document.querySelectorAll(".flash").forEach(el => {
        setTimeout(() => {
            el.style.opacity = "0";
            el.style.transform = "translateY(-8px)";
            el.style.transition = ".4s";
            setTimeout(() => el.remove(), 450);
        }, 5000);
    });
});
