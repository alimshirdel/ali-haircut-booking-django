// login.js
document.addEventListener('DOMContentLoaded', function () {
  // چک کردن اینکه آیا المان ریدایرکت وجود داره
  const redirectElement = document.getElementById('redirect');
  if (redirectElement) {
    setTimeout(function () {
      window.location.href = redirectElement.dataset.url;
    }, 3000);
  }
});
