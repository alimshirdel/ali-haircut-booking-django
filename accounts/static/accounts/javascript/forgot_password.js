let remaining = parseInt(document.getElementById("timer")?.dataset.remaining || "0");
const btn = document.getElementById("resend-btn");
const timerSpan = document.getElementById("timer");
let interval = null;

function updateTimer() {
    if (remaining <= 0) {
        btn.disabled = false;
        timerSpan.textContent = "";
        clearInterval(interval);
    } else {
        btn.disabled = true;
        let minutes = Math.floor(remaining / 60);
        let seconds = remaining % 60;
        timerSpan.textContent = `ارسال دوباره در ${minutes}:${seconds < 10 ? '0' + seconds : seconds}`;
        remaining--;
    }
}

// شروع تایمر
interval = setInterval(updateTimer, 1000);
updateTimer();

btn.addEventListener("click", function () {
    const identifier = document.getElementById("identifier").value;

    fetch(btn.dataset.url, {
        method: "POST",
        headers: {
            "X-CSRFToken": btn.dataset.csrf,
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: "resend=1&identifier=" + encodeURIComponent(identifier)
    })
        .then(response => response.text())
        .then(data => {
            clearInterval(interval);
            remaining = 5 * 60; // ریست تایمر
            interval = setInterval(updateTimer, 1000);
            updateTimer();

            alert("کد دوباره ارسال شد.");
        });
});
