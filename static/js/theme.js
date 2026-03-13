(function() {
  var html = document.documentElement;
  var saved = localStorage.getItem('theme') || 'dark';
  html.setAttribute('data-theme', saved);

  /* State rate data (matches backend/data/states.py and Streamlit app.py) */
  var STATE_RATES = {
    AZ: { tax: 0.62, insurance_comm: 0.5, insurance_resi: 1.0 },
    CA: { tax: 1.25, insurance_comm: 1.25, insurance_resi: 1.0 },
    IN: { tax: 1.37, insurance_comm: 0.5, insurance_resi: 1.0 },
    NV: { tax: 0.65, insurance_comm: 0.5, insurance_resi: 1.0 },
    TX: { tax: 1.7, insurance_comm: 0.5, insurance_resi: 1.0 },
    MI: { tax: 3.21, insurance_comm: 0.5, insurance_resi: 1.0 }
  };

  /* Theme toggle with icon */
  window.toggleTheme = function() {
    var current = html.getAttribute('data-theme');
    var next = current === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
    var btn = document.getElementById('themeBtn');
    if (btn) btn.textContent = next === 'dark' ? '\u2600\uFE0F' : '\uD83C\uDF19';
  };

  /* Restore theme icon on load */
  document.addEventListener('DOMContentLoaded', function() {
    var btn = document.getElementById('themeBtn');
    if (btn) btn.textContent = html.getAttribute('data-theme') === 'dark' ? '\u2600\uFE0F' : '\uD83C\uDF19';
    initCurrencyFormatting();
    updateRateDisplay();
    initCollapseState();
    bindDrawerKeyboard();
  });

  /* ════════════════════════════════════════════════
     PARSER PANEL TOGGLE
     ════════════════════════════════════════════════ */

  window.toggleParser = function() {
    var panel = document.getElementById('parserPanel');
    var btn = document.getElementById('parserToggleBtn');
    if (!panel) return;
    var isClosed = panel.classList.contains('closed');
    panel.classList.toggle('closed', !isClosed);
    if (btn) btn.setAttribute('aria-expanded', isClosed ? 'true' : 'false');
  };

  /* Mobile parser as full-screen modal */
  window.toggleParserMobile = function() {
    var panel = document.getElementById('parserPanel');
    if (!panel) return;
    panel.classList.toggle('mobile-open');
  };

  /* ════════════════════════════════════════════════
     DRAWER COLLAPSE STATE (URL persistence)
     ════════════════════════════════════════════════ */

  function initCollapseState() {
    var params = new URLSearchParams(location.search);
    var hideParam = params.get('hide');

    if (hideParam !== null) {
      var hidden = hideParam.split(',').filter(Boolean);
      document.querySelectorAll('[data-section]').forEach(function(el) {
        var key = el.dataset.section;
        if (hidden.indexOf(key) !== -1) {
          el.classList.remove('open');
          var hdr = el.querySelector('.drawer-hdr');
          if (hdr) hdr.setAttribute('aria-expanded', 'false');
        } else {
          el.classList.add('open');
          var hdr2 = el.querySelector('.drawer-hdr');
          if (hdr2) hdr2.setAttribute('aria-expanded', 'true');
        }
      });
    }
  }

  window.toggleSection = function(el) {
    el.classList.toggle('open');
    var hdr = el.querySelector('.drawer-hdr');
    if (hdr) {
      hdr.setAttribute('aria-expanded', el.classList.contains('open') ? 'true' : 'false');
    }
    updateCollapseUrl();
  };

  function updateCollapseUrl() {
    var hidden = [];
    document.querySelectorAll('[data-section]').forEach(function(el) {
      if (!el.classList.contains('open')) {
        hidden.push(el.dataset.section);
      }
    });
    var params = new URLSearchParams(location.search);
    if (hidden.length) {
      params.set('hide', hidden.join(','));
    } else {
      params.delete('hide');
    }
    var qs = params.toString();
    history.replaceState(null, '', location.pathname + (qs ? '?' + qs : ''));
  }

  /* Keyboard: Enter/Space toggle drawers */
  function bindDrawerKeyboard() {
    document.querySelectorAll('.drawer-hdr').forEach(function(hdr) {
      hdr.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          window.toggleSection(hdr.parentElement);
        }
      });
    });
  }

  /* ════════════════════════════════════════════════
     RATE DISPLAY
     ════════════════════════════════════════════════ */

  function updateRateDisplay() {
    var stateSelect = document.querySelector('select[name="state"]');
    if (!stateSelect) return;
    var st = stateSelect.value || 'CA';
    var rates = STATE_RATES[st];
    if (!rates) return;

    var taxEl = document.getElementById('taxRateDisplay');
    var insEl = document.getElementById('insuranceRateDisplay');
    if (!taxEl || !insEl) return;

    taxEl.textContent = rates.tax.toFixed(2) + '%';
    var typeInput = document.querySelector('input[name="property_type"]');
    var isCommercial = typeInput && typeInput.value === 'Commercial';
    var insRate = isCommercial ? rates.insurance_comm : rates.insurance_resi;
    insEl.textContent = insRate.toFixed(2) + '%';
  }

  /* ════════════════════════════════════════════════
     DOWN PAYMENT LIVE UPDATE
     ════════════════════════════════════════════════ */

  function updateDownPayment() {
    var ppInput = document.querySelector('input[name="purchase_price"]');
    var dpInput = document.querySelector('input[name="down_payment_pct"]');
    var downEl = document.querySelector('.down-amount');
    if (!ppInput || !dpInput || !downEl) return;

    var pp = parseInt((ppInput.dataset.raw || ppInput.value).replace(/[^0-9]/g, ''), 10) || 0;
    var pct = parseFloat(dpInput.value) || 0;
    var amt = Math.round(pp * pct / 100);

    downEl.textContent = '$' + amt.toLocaleString('en-US');
    downEl.className = 'down-amount ' + (amt <= 500000 ? 'up' : amt <= 750000 ? 'caution' : 'down');
  }

  /* Listen for input changes on price and down payment */
  document.addEventListener('input', function(e) {
    if (e.target && (e.target.name === 'purchase_price' || e.target.name === 'down_payment_pct')) {
      updateDownPayment();
    }
  });
  document.addEventListener('change', function(e) {
    if (e.target && (e.target.name === 'purchase_price' || e.target.name === 'down_payment_pct')) {
      updateDownPayment();
    }
  });

  /* Listen for state changes */
  document.addEventListener('change', function(e) {
    if (e.target && e.target.name === 'state') {
      updateRateDisplay();
    }
  });

  /* Re-init after HTMX swaps */
  document.body.addEventListener('htmx:afterSwap', function(e) {
    if (e.detail.target && e.detail.target.id === 'sidebar-form') {
      initCurrencyFormatting();
      updateRateDisplay();
      updateDownPayment();
    }
    if (e.detail.target && e.detail.target.id === 'results') {
      /* Re-apply collapse state and keyboard bindings after results swap */
      initCollapseState();
      bindDrawerKeyboard();
    }
  });

  /* ════════════════════════════════════════════════
     CURRENCY FORMATTING
     ════════════════════════════════════════════════ */

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
