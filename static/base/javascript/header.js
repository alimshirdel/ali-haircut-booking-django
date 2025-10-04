document.addEventListener('DOMContentLoaded', () => {
  // Toggle منوی فانتزی
  const toggleButtonFancy = document.getElementById('toggleMenuFancy');
  const navbarHeaderFancy = document.getElementById('navbarHeaderFancy');

  if (toggleButtonFancy && navbarHeaderFancy) {
    toggleButtonFancy.addEventListener('click', () => {
      navbarHeaderFancy.classList.toggle('show');
    });
  }

  // ایموجی‌ها
  const emojis = ["😊","😎","🤩","❤️","🎉","✨","🌟","😇","🥳","💖","😍","💕","😘","🙈","😜","😴","😉","🥰"];
  const container = document.getElementById("super-flying-emojis");
  if (!container) return;

  function createSuperEmoji() {
    const span = document.createElement("span");
    span.classList.add("emoji");
    span.textContent = emojis[Math.floor(Math.random()*emojis.length)];

    const direction = Math.random() > 0.5 ? "flyLeftToRight" : "flyRightToLeft";
    span.style.animationName = direction;

    span.style.top = -5 + Math.random()*10 + "px";
    const duration = 1.5 + Math.random()*1.5;
    span.style.animationDuration = duration + "s";

    container.appendChild(span);
    setTimeout(()=> span.remove(), duration*1000);
  }

  function initSuperEmojis() {
    for (let i = 0; i < 4; i++) {
      setTimeout(createSuperEmoji, i*300);
    }
    setInterval(createSuperEmoji, 500);
  }

  // اجرا
  initSuperEmojis();
});
