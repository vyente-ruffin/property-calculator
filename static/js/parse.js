/* Listing parser — SSE consumer and form auto-population (T024).
 *
 * Ported from frontend/js/chat.js SSE pattern.
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
    resultsContainer.innerHTML =
      '<div class="analyzing-overlay">' +
      '<div class="analyzing-spinner"></div>' +
      '<div class="analyzing-text">Analyzing Property</div>' +
      '<div class="analyzing-sub">Scraping listing data and running investment analysis...</div>' +
      '</div>';
  }
  if (extractedContainer) extractedContainer.innerHTML = '';

  // Clear input for next property
  input.value = "";

  // Add user message
  feed.innerHTML +=
    '<div class="msg user"><div class="msg-label">You</div>' +
    '<div class="msg-bubble" style="font-family:\'JetBrains Mono\',monospace;font-size:12px;white-space:pre-wrap;word-break:break-all;">' +
    escapeHtml(text) +
    "</div></div>";

  // Add pipeline container
  var pipelineId = "pipeline-" + Date.now();
  feed.innerHTML +=
    '<div class="msg system"><div class="pipeline" id="' +
    pipelineId +
    '">' +
    '<div class="pipeline-toggle" onclick="this.parentElement.classList.toggle(\'open\')">' +
    '<span class="check">⏳</span><span>Analyzing...</span><span class="chevron">▾</span>' +
    "</div>" +
    '<div class="pipeline-steps" id="' +
    pipelineId +
    '-steps"></div></div></div>';

  var steps = [
    "parse_input",
    "scrape_url",
    "extract_fields",
    "search_link",
    "rentcast",
    "reextract",
    "validate",
  ];
  var stepsEl = document.getElementById(pipelineId + "-steps");
  for (var i = 0; i < steps.length; i++) {
    stepsEl.innerHTML +=
      '<div class="step" id="step-' +
      steps[i] +
      '">' +
      '<span class="step-status">⏳</span>' +
      '<span class="step-name">' +
      steps[i].replace(/_/g, " ") +
      "</span>" +
      '<span class="step-detail"></span></div>';
  }

  // Fetch SSE stream (same pattern as frontend/js/chat.js)
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
          updateStep(event.step, event.status, event.data);
          if (
            event.step === "complete" &&
            event.data &&
            event.data.result
          ) {
            finalResult = event.data.result;
          }
        } catch (e) {
          // Ignore malformed SSE lines
        }
      }
    }

    // Update pipeline header with address
    var pipeline = document.getElementById(pipelineId);
    pipeline.querySelector(".check").textContent = "✅";
    var addr = finalResult && finalResult["Address"] ? finalResult["Address"] : "";
    var statusText = addr ? addr + " — Analyzed" : "Analyzed — 7/7 steps";
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
        if (status) status.textContent = '✅ Auto-saved #' + d.id;
      }).catch(function() {});
    }
  } catch (e) {
    feed.innerHTML +=
      '<div class="msg system"><div class="msg-bubble" style="color:var(--down);">Error: ' +
      e.message +
      "</div></div>";
  }

  // Reset button
  parseBtn.disabled = false;
  parseBtn.textContent = "Analyze Property";
  parseBtn.classList.remove("parsing");

  feed.scrollTop = feed.scrollHeight;
}

function updateStep(name, status, data) {
  var el = document.getElementById("step-" + name);
  if (!el) return;
  var icons = { running: "⏳", done: "✅", skipped: "⏭", error: "❌" };
  el.querySelector(".step-status").textContent = icons[status] || "⏳";
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
    ["Annual Rent Income (Projected)", "Annual Rent"],
    ["Monthly Rental Income (Projected)", "Monthly Rent"],
    ["Date On Market", "Date on Market"],
  ];

  var cells = "";
  for (var i = 0; i < fields.length; i++) {
    var key = fields[i][0];
    var label = fields[i][1];
    var val = data[key] || data[key.replace("(Projected)", "(Actual)")] || "--";
    if (typeof val === "string") {
      val = val.replace(/\.00\b/g, "");
    }
    cells +=
      '<div class="extracted-cell"><div class="ek">' +
      label +
      '</div><div class="ev">' +
      val +
      "</div></div>";
  }

  // Price per unit
  var price = parseInt(String(data["Price"] || "0").replace(/[^0-9]/g, ""), 10);
  var units = parseInt(data["Total Units"] || "0", 10);
  if (price && units) {
    cells += '<div class="extracted-cell"><div class="ek">Price/Unit</div><div class="ev">$' + Math.round(price / units).toLocaleString("en-US") + '</div></div>';
  }

  // Description
  var desc = data["Description"] || "";
  var descHtml = desc ? '<div class="extracted-desc">' + escapeHtml(desc) + '</div>' : '';

  // Unit Mix table
  var unitMixRaw = data["Unit Mix Summary"] || "";
  var unitMixHtml = buildUnitMixTable(unitMixRaw);

  container.innerHTML =
    '<div class="sec-header">Parsed Listing Data</div>' +
    '<div class="extracted-section">' +
    '<div class="extracted-header">' +
    '<span class="extracted-label">Extracted Fields</span>' +
    '<span class="extracted-address">' + escapeHtml(displayAddr) + '</span>' +
    '</div>' +
    descHtml +
    '<div class="extracted-grid">' +
    cells +
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
      // Try alternate format like "1x0/1@$764"
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

  var html = '<div class="unit-mix-section">';
  html += '<div class="unit-mix-header">';
  html += '<span class="unit-mix-title">Unit Mix</span>';
  html += '<span class="unit-mix-total">' + totalUnits + ' units · <strong>$' + totalRent.toLocaleString('en-US') + '/mo</strong></span>';
  html += '</div>';
  html += '<table class="unit-mix-table"><thead><tr><th>Type</th><th>Count</th><th>Rent</th><th>Subtotal</th></tr></thead><tbody>';
  for (var j = 0; j < rows.length; j++) {
    var r = rows[j];
    html += '<tr><td class="unit-type">' + r.type + '</td>';
    html += '<td class="count">' + r.count + '</td>';
    html += '<td class="rent">$' + r.rent.toLocaleString('en-US') + '</td>';
    html += '<td>$' + r.subtotal.toLocaleString('en-US') + '</td></tr>';
  }
  html += '</tbody></table></div>';
  return html;
}

function populateCalculator(data) {
  var annualRent = parseCurrency(data["Annual Rent Income (Actual)"])
    || parseCurrency(data["Annual Rent Income (Projected)"])
    || parseCurrency(data["Annual Rent Income"]);

  var mapping = {
    purchase_price: parseCurrency(data["Price"]),
    annual_gross_rents: annualRent,
    annual_noi_listing: parseCurrency(data["NOI"]),
    total_units: data["Total Units"] || "",
    property_url: data["Link"] || "",
  };

  // Extract state from "City, ST ZIP"
  var city = data["City"] || "";
  var stMatch = city.match(/,\s*([A-Z]{2})\s/);
  if (stMatch) mapping["state"] = stMatch[1];

  var keys = Object.keys(mapping);
  var populated = {};
  for (var i = 0; i < keys.length; i++) {
    var name = keys[i];
    var val = mapping[name];
    if (!val) continue;
    var el = document.querySelector('[name="' + name + '"]');
    if (el) {
      el.value = val;
      el.dataset.raw = val;
      populated[name] = val;
    }
  }

  // Log which fields were populated
  fetch('/api/log', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({event: 'form_populated', data: populated})
  }).catch(function() {});

  // Trigger HTMX recalculation
  var form = document.getElementById("calc-form");
  if (form && typeof htmx !== "undefined") {
    htmx.trigger(form, "change");
  }
}

function parseCurrency(str) {
  if (!str) return "";
  return str.replace(/[$,]/g, "").replace(/\.00$/, "");
}

function saveToGoogleSheet() {
  if (!lastParsedResult) {
    var status = document.getElementById("saveStatus");
    if (status) status.textContent = "❌ No property analyzed yet";
    return;
  }

  var btn = document.getElementById("saveBtn");
  if (btn) btn.querySelector("span").textContent = "Saving...";

  fetch("/api/properties", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({data: lastParsedResult})
  }).then(function(r) {
    if (!r.ok) throw new Error(r.status === 503 ? "Google Sheets not configured" : "Save failed");
    return r.json();
  }).then(function(d) {
    var status = document.getElementById("saveStatus");
    if (status) status.textContent = "✅ Saved to Google Sheet (row " + d.row + ")";
    if (btn) btn.querySelector("span").textContent = "✅ Saved";
    fetch('/api/log', { method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({event: 'google_sheet_saved', data: {row: d.row, address: lastParsedResult.Address, price: lastParsedResult.Price}})
    }).catch(function() {});
  }).catch(function(e) {
    var status = document.getElementById("saveStatus");
    if (status) status.textContent = "❌ " + e.message;
    if (btn) btn.querySelector("span").textContent = "Save to Google Sheet";
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
