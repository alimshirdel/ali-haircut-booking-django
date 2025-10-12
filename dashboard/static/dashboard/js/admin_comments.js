function toggleComment(linkEl, id) {
  const shortEl = document.getElementById(`short-${id}`);
  const fullEl = document.getElementById(`full-${id}`);

  if (fullEl.classList.contains('d-none')) {
    shortEl.classList.add('d-none');
    fullEl.classList.remove('d-none');
    linkEl.textContent = 'بستن';
  } else {
    fullEl.classList.add('d-none');
    shortEl.classList.remove('d-none');
    linkEl.textContent = 'نمایش بیشتر';
  }
}
