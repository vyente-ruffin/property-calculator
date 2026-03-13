/* Listing parser — SSE consumer and form auto-population (T024).
 *
 * Ported from frontend/js/chat.js SSE pattern.
 * All user-supplied text is sanitized via escapeHtml() before DOM insertion.
 */

var lastParsedResult = null;

async function parseListing() {
  var input = document.getElementById("listingInput");
  var text = input.value.trim();
  if (!text) return;

  var parseBtn = document.getElementById("parseBtn");
  var feed = document.getElementById("chatFeed");

  // Disable button and show loading state
  parseBtn.disabled = true;
  parseBtn.textContent = "Analyzing...";
  parseBtn.classList.add("parsing");

  // Show loading overlay in results area
  var resultsContainer = document.getElementById("results");
  var extractedContainer = document.getElementById("extracted-data");
  if (resultsContainer) {
    resultsContainer.textContent = '';
    var overlay = document.createElement('div');
    overlay.className = 'analyzing-overlay';
    var spinner = document.createElement('div');
    spinner.className = 'analyzing-spinner';
    var title = document.createElement('div');
    title.className = 'analyzing-text';
    title.textContent = 'Analyzing Property';
    var sub = document.createElement('div');
    sub.className = 'analyzing-sub';
    sub.textContent = 'Scraping listing data and running investment analysis...';
    overlay.appendChild(spinner);
    overlay.appendChild(title);
    overlay.appendChild(sub);
    resultsContainer.appendChild(overlay);
  }
  if (extractedContainer) extractedContainer.textContent = '';

  // Clear input for next property
  input.value = "";

  // Ensure parser panel is visible
  var parserPanel = document.getElementById('parserPanel');
  if (parserPanel && parserPanel.classList.contains('closed')) {
    parserPanel.classList.remove('closed');
  }

  // Add user message (sanitized)
  var userMsg = document.createElement('div');
  userMsg.className = 'msg user';
  var userLabel = document.createElement('div');
  userLabel.className = 'msg-label';
  userLabel.textContent = 'You';
  var userBubble = document.createElement('div');
  userBubble.className = 'msg-bubble';
  userBubble.style.cssText = 'font-family:monospace;font-size:11px;word-break:break-all;';
  userBubble.textContent = text;
  userMsg.appendChild(userLabel);
  userMsg.appendChild(userBubble);
  feed.appendChild(userMsg);

  // Add pipeline container
  var pipelineId = "pipeline-" + Date.now();
  var pipeMsg = document.createElement('div');
  pipeMsg.className = 'msg system';
  var pipeEl = document.createElement('div');
  pipeEl.className = 'pipeline';
  pipeEl.id = pipelineId;
  var pipeToggle = document.createElement('div');
  pipeToggle.className = 'pipeline-toggle';
  pipeToggle.onclick = function() { pipeEl.classList.toggle('open'); };
  var checkSpan = document.createElement('span');
  checkSpan.className = 'check';
  checkSpan.textContent = '\u23F3';
  var labelSpan = document.createElement('span');
  labelSpan.textContent = 'Analyzing...';
  var chevSpan = document.createElement('span');
  chevSpan.className = 'chevron';
  chevSpan.textContent = '\u25BE';
  pipeToggle.appendChild(checkSpan);
  pipeToggle.appendChild(labelSpan);
  pipeToggle.appendChild(chevSpan);
  var stepsDiv = document.createElement('div');
  stepsDiv.className = 'pipeline-steps';
  stepsDiv.id = pipelineId + '-steps';
  pipeEl.appendChild(pipeToggle);
  pipeEl.appendChild(stepsDiv);
  pipeMsg.appendChild(pipeEl);
  feed.appendChild(pipeMsg);

  var steps = [
    "parse_input",
    "scrape_url",
    "extract_fields",
    "search_link",
    "rentcast",
    "reextract",
    "validate",
  ];
  // Use pipeline-scoped IDs to avoid collisions when running multiple analyses
  var stepPrefix = pipelineId + "-step-";
  for (var i = 0; i < steps.length; i++) {
    var stepEl = document.createElement('div');
    stepEl.className = 'step';
    stepEl.id = stepPrefix + steps[i];
    var statusSpan = document.createElement('span');
    statusSpan.className = 'step-status';
    statusSpan.textContent = '\u23F3';
    var nameSpan = document.createElement('span');
    nameSpan.className = 'step-name';
    nameSpan.textContent = steps[i].replace(/_/g, ' ');
    var detailSpan = document.createElement('span');
    detailSpan.className = 'step-detail';
    stepEl.appendChild(statusSpan);
    stepEl.appendChild(nameSpan);
    stepEl.appendChild(detailSpan);
    stepsDiv.appendChild(stepEl);
  }

  // Fetch SSE stream
  try {
    var resp = await fetch("/api/parse", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: text }),
    });

    var reader = resp.body.getReader();
    var decoder = new TextDecoder();
    var buffer = "";
    var finalResult = null;

    while (true) {
      var chunk = await reader.read();
      if (chunk.done) break;
      buffer += decoder.decode(chunk.value, { stream: true });

      var lines = buffer.split("\n");
      buffer = lines.pop();

      for (var j = 0; j < lines.length; j++) {
        var line = lines[j].trim();
        if (!line.startsWith("data: ")) continue;
        try {
          var event = JSON.parse(line.substring(6));
          updateStep(stepPrefix + event.step, event.status, event.data);
          if (
            event.step === "complete" &&
            event.data &&
            event.data.result
          ) {
            finalResult = event.data.result;
          }
        } catch (e) {
          // skip malformed SSE lines
        }
      }
    }

    // Flush any remaining data left in the buffer after stream ends
    if (buffer.trim().startsWith("data: ")) {
      try {
        var lastEvent = JSON.parse(buffer.trim().substring(6));
        updateStep(stepPrefix + lastEvent.step, lastEvent.status, lastEvent.data);
        if (lastEvent.step === "complete" && lastEvent.data && lastEvent.data.result) {
          finalResult = lastEvent.data.result;
        }
      } catch (e) {}
    }

    // Update pipeline header with address
    var pipeline = document.getElementById(pipelineId);
    pipeline.querySelector(".check").textContent = "\u2705";
    var addr = finalResult && finalResult["Address"] ? finalResult["Address"] : "";
    var statusText = addr ? addr + " \u2014 Analyzed" : "Analyzed \u2014 7/7 steps";
    pipeline.querySelector(
      ".pipeline-toggle span:nth-child(2)"
    ).textContent = statusText;

    // Show extracted data in results panel and populate calculator
    if (finalResult) {
      lastParsedResult = finalResult;
      showExtractedData(finalResult);
      populateCalculator(finalResult);

      // Auto-save to portfolio (SQLite)
      fetch('/api/portfolio', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({data: finalResult})
      }).then(function(r) { return r.json(); }).then(function(d) {
        var status = document.getElementById('saveStatus');
        if (status) status.textContent = '\u2705 Auto-saved #' + d.id;
      }).catch(function() {
        var status = document.getElementById('saveStatus');
        if (status) status.textContent = 'Auto-save failed';
      });
    }
  } catch (e) {
    var errMsg = document.createElement('div');
    errMsg.className = 'msg system';
    var errBubble = document.createElement('div');
    errBubble.className = 'msg-bubble';
    errBubble.style.color = 'var(--down)';
    errBubble.textContent = 'Error: ' + e.message;
    errMsg.appendChild(errBubble);
    feed.appendChild(errMsg);
  }

  // Reset button
  parseBtn.disabled = false;
  parseBtn.textContent = "Analyze";
  parseBtn.classList.remove("parsing");

  feed.scrollTop = feed.scrollHeight;
}

function updateStep(stepId, status, data) {
  var el = document.getElementById(stepId);
  if (!el) return;
  var icons = { running: "\u23F3", done: "\u2705", skipped: "\u23ED", error: "\u274C" };
  el.querySelector(".step-status").textContent = icons[status] || "\u23F3";
  el.className = "step " + status;
  if (data) {
    var detail = el.querySelector(".step-detail");
    if (data.text_length) detail.textContent = data.text_length + " chars";
    if (data.fields)
      detail.textContent = Object.keys(data.fields).length + "/15";
    if (data.rent) detail.textContent = data.rent.monthly_formatted;
    if (data.valid !== undefined)
      detail.textContent = data.valid ? "pass" : "fail";
  }
}

function showExtractedData(data) {
  var container = document.getElementById("extracted-data");
  if (!container) return;

  var address = data["Address"] || "";
  var city = data["City"] || "";
  var displayAddr = address + (city ? ", " + city : "");

  var fields = [
    ["Price", "Price"],
    ["Total Units", "Total Units"],
    ["Cap Rate", "Cap Rate"],
    ["NOI", "NOI"],
    ["Date On Market", "Date on Market"],
  ];

  var cellsHtml = "";
  for (var i = 0; i < fields.length; i++) {
    var key = fields[i][0];
    var label = fields[i][1];
    var val = data[key] || "--";
    if (typeof val === "string") {
      val = val.replace(/\.00\b/g, "");
    }
    cellsHtml +=
      '<div class="extracted-cell"><div class="ek">' +
      escapeHtml(label) +
      '</div><div class="ev">' +
      escapeHtml(String(val)) +
      "</div></div>";
  }

  // Rent fields: Actual drives calculations, Projected is display-only
  var actualMonthly = data["Monthly Rental Income (Actual)"] || "";
  var projectedMonthly = data["Monthly Rental Income (Projected)"] || "";
  var actualAnnual = data["Annual Rent Income (Actual)"] || "";
  var projectedAnnual = data["Annual Rent Income (Projected)"] || "";

  if (actualAnnual || actualMonthly) {
    var aVal = (actualAnnual || actualMonthly).replace(/\.00\b/g, "");
    cellsHtml += '<div class="extracted-cell"><div class="ek">Rent (Actual)</div><div class="ev">' + escapeHtml(aVal) + '</div></div>';
  }
  if (projectedAnnual || projectedMonthly) {
    var pVal = (projectedAnnual || projectedMonthly).replace(/\.00\b/g, "");
    cellsHtml += '<div class="extracted-cell"><div class="ek">Rent (Projected)</div><div class="ev">' + escapeHtml(pVal) + '</div></div>';
  }
  if (!actualAnnual && !actualMonthly && !projectedAnnual && !projectedMonthly) {
    cellsHtml += '<div class="extracted-cell"><div class="ek">Rent</div><div class="ev">--</div></div>';
  }

  // Price per unit — B14 fix: use parseFloat instead of parseInt
  var price = Math.round(parseFloat(String(data["Price"] || "0").replace(/[$,]/g, '')));
  var units = parseInt(data["Total Units"] || "0", 10);
  if (price && units) {
    cellsHtml += '<div class="extracted-cell"><div class="ek">Price/Unit</div><div class="ev">$' + Math.round(price / units).toLocaleString("en-US") + '</div></div>';
  }

  // Description
  var desc = data["Description"] || "";
  var descHtml = desc ? '<div class="extracted-desc">' + escapeHtml(desc) + '</div>' : '';

  // Unit Mix table
  var unitMixRaw = data["Unit Mix Summary"] || "";
  var unitMixHtml = buildUnitMixTable(unitMixRaw);

  // Clickable property link
  var link = data["Link"] || "";
  var linkHtml = link
    ? '<a href="' + escapeHtml(link) + '" target="_blank" rel="noopener" class="extracted-link">View Listing \u2197</a>'
    : '';

  // Build safe HTML — all dynamic values are escaped via escapeHtml()
  container.innerHTML =
    '<div class="sec-header">Parsed Listing Data</div>' +
    '<div class="extracted-section">' +
    '<div class="extracted-header">' +
    '<span class="extracted-label">Extracted Fields</span>' +
    '<span class="extracted-address">' + escapeHtml(displayAddr) + '</span>' +
    linkHtml +
    '</div>' +
    descHtml +
    '<div class="extracted-grid">' +
    cellsHtml +
    '</div>' +
    unitMixHtml +
    '</div>';
}

function buildUnitMixTable(raw) {
  if (!raw) return '';
  // Parse "2x2BD/1BA@$2030 | 2x3BD/2BA@$2960" format
  var entries = raw.split('|').map(function(s) { return s.trim(); }).filter(Boolean);
  var rows = [];
  var totalUnits = 0;
  var totalRent = 0;

  for (var i = 0; i < entries.length; i++) {
    var m = entries[i].match(/(\d+)x(\d+)(?:BD)?\/(\d+)(?:BA)?@\$?([\d,]+)/i);
    if (!m) {
      m = entries[i].match(/(\d+)x(\d+)\/(\d+)@\$?([\d,]+)/i);
    }
    if (m) {
      var count = parseInt(m[1], 10);
      var beds = parseInt(m[2], 10);
      var baths = parseInt(m[3], 10);
      var rent = parseInt(m[4].replace(/,/g, ''), 10);
      var typeName = beds === 0 ? 'Studio' : beds + ' BD';
      typeName += ' / ' + baths + ' BA';
      totalUnits += count;
      totalRent += count * rent;
      rows.push({ type: typeName, count: count, rent: rent, subtotal: count * rent });
    }
  }

  if (rows.length === 0) return '';

  // Unit mix values come from regex-validated data, safe for display
  var html = '<div class="unit-mix-section">';
  html += '<div class="unit-mix-header">';
  html += '<span class="unit-mix-title">Unit Mix</span>';
  html += '<span class="unit-mix-total">' + totalUnits + ' units \u00B7 <strong>$' + totalRent.toLocaleString('en-US') + '/mo</strong></span>';
  html += '</div>';
  html += '<table class="unit-mix-table"><thead><tr><th>Type</th><th>Count</th><th>Rent</th><th>Subtotal</th></tr></thead><tbody>';
  for (var j = 0; j < rows.length; j++) {
    var r = rows[j];
    html += '<tr><td class="unit-type">' + escapeHtml(r.type) + '</td>';
    html += '<td class="count">' + r.count + '</td>';
    html += '<td class="rent">$' + r.rent.toLocaleString('en-US') + '</td>';
    html += '<td>$' + r.subtotal.toLocaleString('en-US') + '</td></tr>';
  }
  html += '</tbody></table></div>';
  return html;
}

function populateCalculator(data) {
  var units = parseInt(data["Total Units"], 10) || 0;
  var isResidential = units > 0 && units <= 4;
  var currentType = document.querySelector('input[name="property_type"]');
  var needsSwap = currentType && (
    (isResidential && currentType.value === 'Commercial') ||
    (!isResidential && currentType.value === 'Residential')
  );

  var annualRent = parseCurrency(data["Annual Rent Income (Actual)"])
    || parseCurrency(data["Annual Rent Income (Projected)"])
    || parseCurrency(data["Annual Rent Income"]);

  // For residential, derive monthly rent from annual
  var monthlyRent = parseCurrency(data["Monthly Rental Income (Actual)"])
    || parseCurrency(data["Monthly Rental Income (Projected)"]);
  if (!monthlyRent && annualRent) {
    monthlyRent = String(Math.round(parseFloat(annualRent) / 12));
  }

  function fillForm() {
    var mapping = {
      purchase_price: parseCurrency(data["Price"]),
      total_units: data["Total Units"] || "",
      property_url: data["Link"] || "",
    };

    // Residential uses monthly_rent; commercial uses annual_gross_rents
    var typeInput = document.querySelector('input[name="property_type"]');
    if (typeInput && typeInput.value === 'Residential') {
      mapping.monthly_rent = monthlyRent || "";
    } else {
      mapping.annual_gross_rents = annualRent;
      mapping.annual_noi_listing = parseCurrency(data["NOI"]);
    }

    // Extract state from "City, ST ZIP"
    var city = data["City"] || "";
    var stMatch = city.match(/,\s*([A-Z]{2})(?:\s|$)/);
    if (stMatch) mapping["state"] = stMatch[1];

    var currencyFields = ['purchase_price', 'annual_gross_rents', 'annual_noi_listing', 'other_expenses', 'monthly_rent'];

    var keys = Object.keys(mapping);
    var populated = {};
    for (var i = 0; i < keys.length; i++) {
      var name = keys[i];
      var val = mapping[name];
      if (!val) continue;
      var el = document.querySelector('[name="' + name + '"]');
      if (el) {
        el.dataset.raw = val;
        if (currencyFields.indexOf(name) >= 0) {
          // B14 fix: use parseFloat + round instead of parseInt to handle decimals correctly
          var n = Math.round(parseFloat(String(val).replace(/[$,]/g, '')));
          el.value = isNaN(n) ? '$0' : '$' + n.toLocaleString('en-US');
        } else {
          el.value = val;
        }
        populated[name] = val;
      }
    }

    fetch('/api/log', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({event: 'form_populated', data: populated})
    }).catch(function() {});

    var form = document.getElementById("calc-form");
    if (form && typeof htmx !== "undefined") {
      htmx.trigger(form, "change");
    }
  }

  if (needsSwap && typeof htmx !== "undefined") {
    var target = isResidential ? '/sidebar/residential' : '/sidebar/commercial';
    htmx.ajax('GET', target, {target: '#sidebar-form', swap: 'innerHTML'}).then(function() {
      // After swap, htmx needs a tick to process new elements before triggers work
      setTimeout(fillForm, 50);
    });
  } else {
    fillForm();
  }
}

function parseCurrency(str) {
  if (!str) return "";
  var num = parseFloat(str.replace(/[$,]/g, ""));
  if (isNaN(num)) return "";
  return String(Math.round(num));
}

function saveToGoogleSheet() {
  if (!lastParsedResult) {
    var status = document.getElementById("saveStatus");
    if (status) status.textContent = "\u274C No property analyzed yet";
    return;
  }

  var btn = document.getElementById("saveBtn");
  if (btn) btn.textContent = "Saving...";

  fetch("/api/properties", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({data: lastParsedResult})
  }).then(function(r) {
    if (!r.ok) throw new Error(r.status === 503 ? "Google Sheets not configured" : "Save failed");
    return r.json();
  }).then(function(d) {
    var status = document.getElementById("saveStatus");
    if (status) status.textContent = "\u2705 Saved to Google Sheet (row " + d.row + ")";
    if (btn) btn.textContent = "\u2705 Saved";
    fetch('/api/log', { method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({event: 'google_sheet_saved', data: {row: d.row, address: lastParsedResult.Address, price: lastParsedResult.Price}})
    }).catch(function() {});
  }).catch(function(e) {
    var status = document.getElementById("saveStatus");
    if (status) status.textContent = "\u274C " + e.message;
    if (btn) btn.textContent = "Save to Google Sheet";
    fetch('/api/log', { method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({event: 'google_sheet_error', data: {error: e.message}})
    }).catch(function() {});
  });
}

function escapeHtml(str) {
  var div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
