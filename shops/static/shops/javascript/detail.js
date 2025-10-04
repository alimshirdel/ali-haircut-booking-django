document.addEventListener('DOMContentLoaded', function () {
  // نمایش یا مخفی کردن فرم رزرو
  const showBtn = document.getElementById('show-reservation');
  const formDiv = document.querySelector('.reservation-form');

  if (showBtn && formDiv) {
    showBtn.addEventListener('click', function (e) {
      e.preventDefault();
      if (formDiv.style.display === "none" || formDiv.style.display === "") {
        formDiv.style.display = "block";
        formDiv.scrollIntoView({ behavior: "smooth" });
      } else {
        formDiv.style.display = "none";
      }
    });
  }

  // نمایش نقشه
  const mapDiv = document.getElementById('map');
  if (mapDiv) {
    const lat = parseFloat(mapDiv.dataset.lat);
    const lng = parseFloat(mapDiv.dataset.lng);
    const name = mapDiv.dataset.name;
    const address = mapDiv.dataset.address;

    const map = L.map('map').setView([lat, lng], 16);
    L.tileLayer('https://a.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/">OSM</a>',
      maxZoom: 19
    }).addTo(map);
    L.marker([lat, lng]).addTo(map).bindPopup(`<b>${name}</b><br>${address}`).openPopup();

    window.addEventListener('resize', function () {
      map.invalidateSize();
    });
  }

  // هندل کردن فرم انتخاب تاریخ بدون رفرش
  const reservationForm = document.getElementById("reservationForm");
  const timesContainer = document.getElementById("timesContainer");

  function toPersianDigits(str) {
    const persianDigits = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];
    return str.replace(/\d/g, function (d) { return persianDigits[d]; });
  }

  function formatPersianDate(dateStr) {
    const fp = window.flatpickr.parseDate(dateStr, "Y-m-d");
    if (!fp) return dateStr;
    const year = fp.getFullYear();
    const month = fp.getMonth() + 1;
    const day = fp.getDate();
    return `${toPersianDigits(day.toString())}/${toPersianDigits(month.toString())}/${toPersianDigits(year.toString())}`;
  }

  if (reservationForm && timesContainer) {
    reservationForm.addEventListener("submit", function (e) {
      e.preventDefault();

      const selectedDate = document.getElementById("date").value;
      const url = `${window.location.pathname}?date=${selectedDate}`;

      fetch(url)
        .then(res => res.text())
        .then(html => {
          const parser = new DOMParser();
          const doc = parser.parseFromString(html, "text/html");
          const newTimes = doc.querySelector("#timesContainer");

          if (newTimes) {
            newTimes.querySelectorAll('h4').forEach(h4 => {
              const isoDate = h4.dataset.date;
              h4.textContent = formatPersianDate(isoDate);
            });

            timesContainer.innerHTML = newTimes.innerHTML;
          }
        })
        .catch(err => {
          console.error("خطا در دریافت زمان‌ها:", err);
          timesContainer.innerHTML = "<p>خطا در بارگذاری زمان‌ها.</p>";
        });
    });
  }

  // Flatpickr Jalali برای input تاریخ
  flatpickr("#date", {
    dateFormat: "Y-m-d",
    altInput: true,
    altFormat: "Y/m/d",
    allowInput: true,
    jalali: true,
  });
});

// شروع مطالعه

// وقتی DOM حاضر شد — (اگر قبلاً listener داری، محتوای زیر را اضافه کن)
document.querySelectorAll('.my-calendar td[data-date]').forEach(td => {
  td.addEventListener('click', function () {
    const date = this.dataset.date; // 'YYYY-MM-DD' (میلادی)
    // مقدار input تاریخ را هم ست کن تا فرم GET قبلی تو کار کنه:
    const dateInput = document.getElementById("date");
    if (dateInput) dateInput.value = date;

    // هایلایت سلکت شده:
    document.querySelectorAll('.my-calendar td.selected').forEach(el => el.classList.remove('selected'));
    this.classList.add('selected');

    // fetch برای دریافت timesContainer از سرور (قابلیت بدون رفرش)
    const url = `${window.location.pathname}?date=${date}`;
    fetch(url)
      .then(res => res.text())
      .then(html => {
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, "text/html");
        const newTimes = doc.querySelector("#timesContainer");
        if (newTimes) {
          document.getElementById("timesContainer").innerHTML = newTimes.innerHTML;
          // بعد از جایگذاری، اگر لازم باشه می‌تونی event handler های دکمه‌ها رو دوباره bind کنی
        }
      })
      .catch(err => {
        console.error("خطا در دریافت زمان‌ها:", err);
      });
  });
});
document.addEventListener("DOMContentLoaded", function () {
  // --- هندل کلیک روزها ---
  function bindDayClicks() {
    document.querySelectorAll('.my-calendar td[data-date]').forEach(td => {
      td.addEventListener('click', function () {
        const date = this.dataset.date;
        const dateInput = document.getElementById("date");
        if (dateInput) dateInput.value = date;

        document.querySelectorAll('.my-calendar td.selected').forEach(el => el.classList.remove('selected'));
        this.classList.add('selected');

        const url = `${window.location.pathname}?date=${date}`;
        fetch(url)
          .then(res => res.text())
          .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, "text/html");
            const newTimes = doc.querySelector("#timesContainer");
            if (newTimes) {
              document.getElementById("timesContainer").innerHTML = newTimes.innerHTML;
            }
          });
      });
    });
  }

  // --- هندل کلیک دکمه‌های ماه ---
  function bindMonthNav() {
    document.querySelectorAll('.calendar-header a.btn-nav').forEach(btn => {
      btn.addEventListener('click', function (e) {
        e.preventDefault();
        const url = this.href;

        fetch(url)
          .then(res => res.text())
          .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, "text/html");
            const newCalendar = doc.querySelector(".calendar-card");
            if (newCalendar) {
              document.querySelector(".calendar-card").innerHTML = newCalendar.innerHTML;
              bindDayClicks();   // روزهای جدید
              bindMonthNav();    // دکمه‌های ماه جدید
            }
          });
      });
    });
  }

  // اول بارگذاری
  bindDayClicks();
  bindMonthNav();
});

// پایان مطالعه 