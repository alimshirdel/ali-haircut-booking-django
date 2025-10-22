// shops.js
window.addEventListener('load', () => {
  const input = document.getElementById('ultra-search');
  const icon = document.getElementById('search-icon');
  const wave = document.getElementById('wave');
  const canvas = document.getElementById('particles');
  const ctx = canvas.getContext('2d');

  function resizeCanvas() {
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
  }
  window.addEventListener('resize', resizeCanvas);
  resizeCanvas();

  let particles = [];
  function createParticles(count) {
    particles = [];
    for (let i = 0; i < count; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        size: Math.random() * 3 + 1,
        speed: Math.random() * 1 + 0.5,
        color: `hsl(${Math.random() * 360},80%,70%)`
      });
    }
  }

  function renderParticles() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    particles.forEach(p => {
      ctx.fillStyle = p.color;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      ctx.fill();
      p.y -= p.speed;
      if (p.y < 0) {
        p.y = canvas.height;
        p.x = Math.random() * canvas.width;
      }
    });
    requestAnimationFrame(renderParticles);
  }

  createParticles(30);
  renderParticles();

  input.addEventListener('input', () => {
    icon.style.animation = 'iconDance 0.5s ease';
    setTimeout(() => { icon.style.animation = ''; }, 500);

    wave.classList.add('active');
    const length = input.value.length;
    let gradient;
    if (length < 5) gradient = 'linear-gradient(90deg, #ff6b81, #ff4757, #ff6b81)';
    else if (length < 10) gradient = 'linear-gradient(90deg, #ff7f50, #ff6347, #ff4500)';
    else gradient = 'linear-gradient(90deg, #6a5acd, #836fff, #8a2be2)';
    wave.style.background = gradient;
  });

  input.addEventListener('blur', () => {
    wave.classList.remove('active');
    wave.style.background = 'linear-gradient(90deg, #ff6b81, #ff4757, #ff6b81)';
  });
});
document.addEventListener("DOMContentLoaded", function () {
  const orderSelect = document.getElementById("order-select");
  if (!orderSelect) return; // stop if not found

  const form = orderSelect.closest("form");
  if (!form) return; // stop if no form found

  orderSelect.addEventListener("change", function () {
    const value = orderSelect.value;

    if (value === "distance") {
      if (navigator.geolocation) {
        orderSelect.disabled = true;
        orderSelect.options[orderSelect.selectedIndex].text = "در حال دریافت موقعیت...";

        navigator.geolocation.getCurrentPosition(
          function (pos) {
            const lat = pos.coords.latitude;
            const lng = pos.coords.longitude;

            let latInput = form.querySelector('input[name="lat"]');
            let lngInput = form.querySelector('input[name="lng"]');
            if (!latInput) {
              latInput = document.createElement("input");
              latInput.type = "hidden";
              latInput.name = "lat";
              form.appendChild(latInput);
            }
            if (!lngInput) {
              lngInput = document.createElement("input");
              lngInput.type = "hidden";
              lngInput.name = "lng";
              form.appendChild(lngInput);
            }

            latInput.value = lat;
            lngInput.value = lng;

            form.submit();
          },
          function () {
            alert("امکان دسترسی به موقعیت وجود ندارد ❌");
            orderSelect.disabled = false;
            orderSelect.options[orderSelect.selectedIndex].text = "نزدیکی 📍";
          }
        );
      } else {
        alert("مرورگر شما از موقعیت مکانی پشتیبانی نمی‌کند.");
      }
    } else {
      form.submit();
    }
  });
});
