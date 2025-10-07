const sidebar = document.getElementById('rightSidebar');
const toggleBtn = document.getElementById('sidebarToggle');
const closeBtn = document.getElementById('closeSidebar');

toggleBtn.addEventListener('click', () => {
  sidebar.classList.add('open');
  toggleBtn.style.display = 'none';  // مخفی کردن دکمه
});

closeBtn.addEventListener('click', () => {
  sidebar.classList.remove('open');
  toggleBtn.style.display = 'block'; // نمایش دوباره دکمه
});

// بستن نوار با کلیک بیرون از آن
window.addEventListener('click', (e) => {
  if (!sidebar.contains(e.target) && !toggleBtn.contains(e.target)) {
    sidebar.classList.remove('open');
    toggleBtn.style.display = 'block'; // نمایش دوباره دکمه
  }
});
