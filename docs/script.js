/* Toggle card body */
function tc(header) {
  const body = header.nextElementSibling;
  if (body.style.display === 'none') {
    body.style.display = 'block';
  } else {
    body.style.display = 'none';
  }
}

/* Filter cards by search */
function filterCards() {
  const input = document.getElementById('search');
  const filter = input.value.toLowerCase();
  const cards = document.querySelectorAll('.c');
  let visible = 0;

  cards.forEach(card => {
    const name = card.getAttribute('data-n').toLowerCase();
    const caps = card.getAttribute('data-c').toLowerCase();
    if (name.indexOf(filter) > -1 || caps.indexOf(filter) > -1) {
      card.style.display = '';
      visible++;
    } else {
      card.style.display = 'none';
    }
  });

  const noResults = document.getElementById('noResults');
  noResults.style.display = visible > 0 ? 'none' : 'block';
}

/* Deep link support */
document.addEventListener('DOMContentLoaded', function () {
  const params = new URLSearchParams(window.location.search);
  const provider = params.get('provider');
  if (provider) {
    const card = document.querySelector(`.c[data-n*="${provider.toLowerCase()}"]`);
    if (card) {
      const header = card.querySelector('.ch');
      header.click();
      card.scrollIntoView({ behavior: 'smooth' });
    }
  }
});
