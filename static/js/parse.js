/* Listing parser — SSE consumer and form auto-population (T024).
 *
 * Ported from frontend/js/chat.js SSE pattern.
 */

var parsedProperties = [];

async function parseListing() {
  var input = document.getElementById("listingInput");
  var text = input.value.trim();
  if (!text) return;

  var parseBtn = document.getElementById("parseBtn");
  var feed = document.getElementById("chatFeed");

  // Disable button and show loading state
  parseBtn.disabled = true;
  parseBtn.textContent = "Parsing...";
  parseBtn.classList.add("parsing");

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
      showExtractedData(finalResult);
      populateCalculator(finalResult);
      parsedProperties.push({
        address: finalResult["Address"] || "Unknown",
        city: finalResult["City"] || "",
        price: finalResult["Price"] || "",
        units: finalResult["Total Units"] || "",
        noi: finalResult["NOI"] || "",
        capRate: finalResult["Cap Rate"] || "",
        annualRent: finalResult["Annual Rent Income (Projected)"] || finalResult["Annual Rent Income (Actual)"] || "",
        url: finalResult["Link"] || "",
        timestamp: new Date().toLocaleString("en-US", {timeZone: "America/Los_Angeles"})
      });
    }
  } catch (e) {
    feed.innerHTML +=
      '<div class="msg system"><div class="msg-bubble" style="color:var(--down);">Error: ' +
      e.message +
      "</div></div>";
  }

  // Reset button
  parseBtn.disabled = false;
  parseBtn.textContent = "Parse";
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
    ["Unit Mix Summary", "Unit Mix"],
  ];

  var cells = "";
  for (var i = 0; i < fields.length; i++) {
    var key = fields[i][0];
    var label = fields[i][1];
    var val = data[key] || "--";
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

  container.innerHTML =
    '<div class="sec-header">Parsed Listing Data</div>' +
    '<div class="extracted-section">' +
    '<div class="extracted-header">' +
    '<span class="extracted-label">Extracted Fields</span>' +
    '<span class="extracted-address">' + escapeHtml(displayAddr) + '</span>' +
    '</div>' +
    '<div class="extracted-grid">' +
    cells +
    '</div></div>';
}

function populateCalculator(data) {
  var annualRent = parseCurrency(data["Annual Rent Income (Projected)"])
    || parseCurrency(data["Annual Rent Income (Actual)"])
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
  for (var i = 0; i < keys.length; i++) {
    var name = keys[i];
    var val = mapping[name];
    if (!val) continue;
    var el = document.querySelector('[name="' + name + '"]');
    if (el) {
      el.value = val;
      el.dataset.raw = val;
    }
  }

  // Trigger HTMX recalculation
  var form = document.getElementById("calc-form");
  if (form && typeof htmx !== "undefined") {
    htmx.trigger(form, "change");
  }
}

function parseCurrency(str) {
  if (!str) return "";
  return str.replace(/[$,]/g, "");
}

function showPortfolio() {
  var container = document.getElementById('results');
  if (parsedProperties.length === 0) {
    container.innerHTML = '<div class="empty-state"><div style="font-size:48px;text-align:center;margin:60px 0 16px;">📊</div><p style="text-align:center;color:var(--text-dim);font-size:14px;">No properties parsed yet. Paste a listing URL to get started.</p></div>';
    return;
  }
  var html = '<div class="sec-header" style="margin-top:0;">Portfolio — Session Log</div>';
  html += '<div class="tbl-container"><table class="tbl"><thead><tr><th>Address</th><th>Price</th><th>Units</th><th>Cap Rate</th><th>NOI</th><th>Annual Rent</th><th>Parsed</th></tr></thead><tbody>';
  for (var i = parsedProperties.length - 1; i >= 0; i--) {
    var p = parsedProperties[i];
    html += '<tr><td>' + (p.address || '--') + '</td><td>' + (p.price || '--') + '</td><td>' + (p.units || '--') + '</td><td>' + (p.capRate || '--') + '</td><td>' + (p.noi || '--') + '</td><td>' + (p.annualRent || '--') + '</td><td style="font-size:11px;color:var(--text-dim);">' + p.timestamp + '</td></tr>';
  }
  html += '</tbody></table></div>';
  container.innerHTML = html;
}

function escapeHtml(str) {
  var div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
