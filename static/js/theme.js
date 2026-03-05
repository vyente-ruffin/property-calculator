(function() {
  const html = document.documentElement;
  const saved = localStorage.getItem('theme') || 'dark';
  html.setAttribute('data-theme', saved);

  /* Theme toggle with icon */
  window.toggleTheme = function() {
    const current = html.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
    const btn = document.getElementById('themeBtn');
    if (btn) btn.textContent = next === 'dark' ? '☀️' : '🌙';
  };

  /* Restore theme icon on load */
  document.addEventListener('DOMContentLoaded', function() {
    const btn = document.getElementById('themeBtn');
    if (btn) btn.textContent = html.getAttribute('data-theme') === 'dark' ? '☀️' : '🌙';
    initCurrencyFormatting();
  });

  /* Chat panel toggle */
  window.toggleChat = function() {
    var panel = document.getElementById('chatPanel');
    var btn = document.getElementById('chatToggle');
    if (!panel || !btn) return;
    panel.classList.toggle('open');
    btn.classList.toggle('active');
  };

  /* Currency formatting for numeric inputs */
  function formatCurrency(val) {
    var n = parseInt(String(val).replace(/[^0-9]/g, ''), 10);
    if (isNaN(n)) return '$0';
    return '$' + n.toLocaleString('en-US');
  }

  function initCurrencyFormatting() {
    var selectors = 'input[name="purchase_price"], input[name="annual_gross_rents"], input[name="annual_noi_listing"], input[name="other_expenses"], input[name="monthly_rent"]';
    document.querySelectorAll(selectors).forEach(function(input) {
      if (input.dataset.fmtInit) return;
      input.dataset.fmtInit = '1';
      input.type = 'text';
      input.dataset.raw = input.value;
      input.value = formatCurrency(input.value);

      input.addEventListener('focus', function() {
        var raw = this.dataset.raw || this.value.replace(/[^0-9]/g, '');
        this.value = raw;
        this.select();
      });
      input.addEventListener('blur', function() {
        var raw = this.value.replace(/[^0-9]/g, '');
        this.dataset.raw = raw;
        this.value = formatCurrency(raw);
      });
      input.addEventListener('input', function() {
        this.dataset.raw = this.value.replace(/[^0-9]/g, '');
      });
    });
  }

  /* Re-init currency formatting after HTMX swaps sidebar */
  document.body.addEventListener('htmx:afterSwap', function(e) {
    if (e.detail.target && e.detail.target.id === 'sidebar-form') {
      initCurrencyFormatting();
    }
  });

  /* Strip currency formatting before HTMX sends form data */
  document.body.addEventListener('htmx:configRequest', function(e) {
    var fields = ['purchase_price', 'annual_gross_rents', 'annual_noi_listing', 'other_expenses', 'monthly_rent'];
    fields.forEach(function(f) {
      if (e.detail.parameters[f] !== undefined) {
        var input = document.querySelector('input[name="' + f + '"]');
        if (input && input.dataset.raw) {
          e.detail.parameters[f] = input.dataset.raw;
        } else {
          e.detail.parameters[f] = String(e.detail.parameters[f]).replace(/[^0-9.]/g, '');
        }
      }
    });
  });
})();
