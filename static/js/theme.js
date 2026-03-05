(function() {
  const html = document.documentElement;
  const saved = localStorage.getItem('theme') || 'dark';
  html.setAttribute('data-theme', saved);

  /* State rate data (matches backend/data/states.py and Streamlit app.py) */
  var STATE_RATES = {
    AZ: { tax: 0.62, insurance_comm: 0.5, insurance_resi: 1.0 },
    CA: { tax: 1.2, insurance_comm: 1.2, insurance_resi: 1.0 },
    IN: { tax: 1.4, insurance_comm: 0.5, insurance_resi: 1.0 },
    NV: { tax: 0.6, insurance_comm: 0.5, insurance_resi: 1.0 },
    TX: { tax: 1.7, insurance_comm: 0.5, insurance_resi: 1.0 },
    MI: { tax: 3.2, insurance_comm: 0.5, insurance_resi: 1.0 }
  };

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
    updateRateDisplay();
  });

  /* Chat panel toggle */
  window.toggleChat = function() {
    var panel = document.getElementById('chatPanel');
    var btn = document.getElementById('chatToggle');
    if (!panel || !btn) return;
    panel.classList.toggle('open');
    btn.classList.toggle('active');
    var arrow = panel.querySelector('.chat-collapse');
    if (arrow) arrow.textContent = panel.classList.contains('open') ? '◀' : '▶';
  };

  /* Update rate display boxes based on selected state */
  function updateRateDisplay() {
    var stateSelect = document.querySelector('select[name="state"]');
    if (!stateSelect) return;
    var st = stateSelect.value || 'CA';
    var rates = STATE_RATES[st];
    if (!rates) return;

    var taxEl = document.getElementById('taxRateDisplay');
    var insEl = document.getElementById('insuranceRateDisplay');
    if (!taxEl || !insEl) return;

    taxEl.textContent = rates.tax.toFixed(1) + '%';
    // Determine property type from hidden input
    var typeInput = document.querySelector('input[name="property_type"]');
    var isCommercial = typeInput && typeInput.value === 'Commercial';
    var insRate = isCommercial ? rates.insurance_comm : rates.insurance_resi;
    insEl.textContent = insRate.toFixed(1) + '%';
  }

  /* Listen for state changes */
  document.addEventListener('change', function(e) {
    if (e.target && e.target.name === 'state') {
      updateRateDisplay();
    }
  });

  /* Re-init after HTMX sidebar swaps */
  document.body.addEventListener('htmx:afterSwap', function(e) {
    if (e.detail.target && e.detail.target.id === 'sidebar-form') {
      initCurrencyFormatting();
      updateRateDisplay();
    }
  });

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
