document.addEventListener('DOMContentLoaded', function () {
  // — redirect (اگر وجود داشت)
  const redirectElement = document.getElementById('redirect');
  if (redirectElement) {
    setTimeout(function () {
      window.location.href = redirectElement.dataset.url;
    }, 3000);
  }

  // — انتخاب المان‌ها
  const btn = document.getElementById("resend-btn");
  const timerSpan = document.getElementById("timer");
  if (!btn || !timerSpan) return; // اگر صفحه OTP نیست از کار خارج شو

  // مقدار باقیمانده را از data-attribute خوانده و به عدد تبدیل کن
  let remaining = parseInt(timerSpan.dataset.remaining || "0", 10) || 0;
  let interval = null;

  // تابع بروزرسانی تایمر
  function updateTimer() {
    if (remaining <= 0) {
      btn.disabled = false;
      timerSpan.textContent = "";
      if (interval) {
        clearInterval(interval);
        interval = null;
      }
    } else {
      btn.disabled = true;
      const minutes = Math.floor(remaining / 60);
      const seconds = remaining % 60;
      timerSpan.textContent = `ارسال دوباره در ${minutes}:${seconds < 10 ? '0' + seconds : seconds}`;
      remaining--;
    }
  }

  // استارت اولیه تایمر (فقط یکبار)
  if (!interval) interval = setInterval(updateTimer, 1000);
  updateTimer();

  // کلیک روی دکمه resend
  btn.addEventListener("click", function () {
    // پیدا کردن identifier (مخفی یا فیلد شماره)
    const idEl = document.getElementById("identifier") || document.getElementById("user_phone") || document.querySelector('input[name="phone"]') || document.querySelector('input[name="identifier"]');
    const identifier = idEl ? idEl.value : "";

    // آماده‌سازی بدنه درخواست
    const bodyParts = ["resend=1"];
    if (identifier) bodyParts.push("identifier=" + encodeURIComponent(identifier));
    const body = bodyParts.join("&");

    // غیرفعال کردن دکمه سمت کلاینت تا جواب برگردد
    btn.disabled = true;

    fetch(window.location.href, {
      method: "POST",
      headers: {
        "X-CSRFToken": (document.querySelector("[name=csrfmiddlewaretoken]") || {}).value || "",
        "Content-Type": "application/x-www-form-urlencoded"
      },
      body: body
    })
      .then(function (response) {
        if (!response.ok) throw new Error("Network response was not ok");
        return response.text(); // سرور ممکن است html برگرداند
      })
      .then(function () {
        // ریست تایمر به 5 دقیقه و استارت دوباره
        if (interval) {
          clearInterval(interval);
          interval = null;
        }
        remaining = 5 * 60;
        interval = setInterval(updateTimer, 1000);
        updateTimer();
        alert("کد دوباره ارسال شد.");
      })
      .catch(function (err) {
        console.error("resend failed:", err);
        alert("ارسال مجدد ناموفق بود. دوباره تلاش کنید.");
        // در صورت خطا دکمه را فعال کن (یا تصمیم دیگری بگیر)
        btn.disabled = false;
      });
  });
});
