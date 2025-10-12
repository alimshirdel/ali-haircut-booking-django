document.addEventListener("DOMContentLoaded", function () {
  const comments = document.querySelectorAll(".comment-item");
  const btn = document.getElementById("toggle-comments-btn");
  const VISIBLE_COUNT = 3;
  let expanded = false;

  if (!btn || comments.length <= VISIBLE_COUNT) {
    if (btn) btn.style.display = "none";
    return;
  }

  btn.addEventListener("click", function () {
    expanded = !expanded;

    comments.forEach((c, i) => {
      if (i >= VISIBLE_COUNT) {
        c.classList.toggle("d-none", !expanded);
      }
    });

    btn.textContent = expanded ? "نمایش کمتر ⬆️" : "نمایش بیشتر 💬";
  });
});
