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

  // هندل انتخاب تاریخ و دریافت زمان‌ها بدون رفرش
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
            disablePastSlots(); // بعد از بارگذاری slotهای جدید
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
              disablePastSlots(); // بعد از جایگذاری
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
              bindDayClicks();
              bindMonthNav();
            }
          });
      });
    });
  }

  // اجرای اولیه برای روزها و ماه
  bindDayClicks();
  bindMonthNav();

  // --- تابع غیرفعال کردن slotهای گذشته ---
  function disablePastSlots() {
    const now = new Date();
    const nowMinutes = now.getHours() * 60 + now.getMinutes();

    document.querySelectorAll(".btn-slot").forEach((btn) => {
      const slotTimeStr = btn.value; // "HH:MM"
      const slotDateElement = btn.closest("form").previousElementSibling; // h4
      const slotDateStr = slotDateElement.dataset.date; // "YYYY-MM-DD"

      if (!slotTimeStr || !slotDateStr) return;

      const [slotHour, slotMinute] = slotTimeStr.split(":").map(Number);
      const slotMinutes = slotHour * 60 + slotMinute;

      const slotDate = new Date(slotDateStr);

      // اگر slot برای امروز است و زمان گذشته
      if (slotDate.toDateString() === now.toDateString() && slotMinutes <= nowMinutes) {
        btn.disabled = true;
        btn.classList.add("booked");
      }
    });
  }

  // اجرای اولیه و هر 5 دقیقه
  disablePastSlots();
  setInterval(disablePastSlots, 5 * 60 * 1000);
});
