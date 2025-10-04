document.addEventListener("DOMContentLoaded", function () {

  function bindDayClicks() {
    document.querySelectorAll('.my-calendar td[data-date]').forEach(td => {
      // remove previous handler (to avoid دوبار شدن)
      td.replaceWith(td.cloneNode(true));
    });

    document.querySelectorAll('.my-calendar td[data-date]').forEach(td => {
      td.addEventListener('click', function () {
        const date = this.dataset.date; // 'YYYY-MM-DD' (میلادی)
        const dateInput = document.getElementById("id_date");
        if (dateInput) dateInput.value = date;

        document.querySelectorAll('.my-calendar td.selected').forEach(el => el.classList.remove('selected'));
        this.classList.add('selected');
      });
    });
  }

  function bindMonthNav() {
    document.querySelectorAll('.calendar-header a.btn-nav').forEach(a => {
      // clone to remove old listeners
      a.replaceWith(a.cloneNode(true));
    });

    document.querySelectorAll('.calendar-header a.btn-nav').forEach(a => {
      a.addEventListener('click', function (e) {
        e.preventDefault();
        let url = this.getAttribute('href');
        // append ajax flag
        url += (url.indexOf('?') === -1 ? '?' : '&') + 'ajax=1';
        fetch(url, { credentials: 'same-origin' })
          .then(r => {
            if (!r.ok) throw new Error("Network response was not ok");
            return r.text();
          })
          .then(html => {
            // replace calendar-card with returned HTML (partial)
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const newCalendar = doc.querySelector('.calendar-card') || doc.body;
            const oldCalendar = document.querySelector('.calendar-card');
            if (oldCalendar && newCalendar) {
              oldCalendar.innerHTML = newCalendar.innerHTML;
              // rebind handlers
              bindDayClicks();
              bindMonthNav();
            }
          })
          .catch(err => console.error("خطا در بارگذاری تقویم:", err));
      });
    });
  }

  // initial bind
  bindDayClicks();
  bindMonthNav();

  // اگر می‌خواهی روز انتخاب شده از سرور مشخص شده را هایلایت کنی:
  (function highlightServerSelected() {
    const selected = document.querySelector('.my-calendar td.selected');
    if (selected) {
      const dateInput = document.getElementById("id_date");
      if (dateInput && !dateInput.value) dateInput.value = selected.dataset.date;
    }
  })();

});
