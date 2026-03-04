(function() {
  const html = document.documentElement;
  const saved = localStorage.getItem('theme') || 'dark';
  html.setAttribute('data-theme', saved);

  window.toggleTheme = function() {
    const current = html.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
  };

  /* Mobile tab switching */
  window.switchMobileTab = function(tab) {
    var chat = document.querySelector('.chat-panel');
    var calc = document.querySelector('.calc-panel');
    var tabs = document.querySelectorAll('.mobile-tab');
    if (!chat || !calc) return;
    tabs.forEach(function(t) { t.classList.remove('active'); });
    if (tab === 'chat') {
      chat.classList.add('mobile-active');
      calc.classList.remove('mobile-active');
      tabs[0].classList.add('active');
    } else {
      calc.classList.add('mobile-active');
      chat.classList.remove('mobile-active');
      tabs[1].classList.add('active');
    }
  };

  /* Default to calc panel on mobile */
  document.addEventListener('DOMContentLoaded', function() {
    if (window.innerWidth <= 768) {
      var calc = document.querySelector('.calc-panel');
      if (calc) calc.classList.add('mobile-active');
    }
  });
})();
