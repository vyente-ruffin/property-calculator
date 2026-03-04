/* Listing parser — SSE consumer and form auto-population (T024).
 *
 * Ported from frontend/js/chat.js SSE pattern.
 */

async function parseListing() {
  var input = document.getElementById("listingInput");
  var text = input.value.trim();
  if (!text) return;

  var feed = document.getElementById("chatFeed");

  // Add user message
  feed.innerHTML +=
    '<div class="msg user"><div class="msg-label">You</div>' +
    '<div class="msg-bubble" style="font-family:\'JetBrains Mono\',monospace;font-size:12px;white-space:pre-line;">' +
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

    // Update pipeline header
    var pipeline = document.getElementById(pipelineId);
    pipeline.querySelector(".check").textContent = "✅";
    pipeline.querySelector(
      ".pipeline-toggle span:nth-child(2)"
    ).textContent = "Analyzed — 7/7 steps";

    // Show extracted data and populate calculator
    if (finalResult) {
      showExtractedData(finalResult, feed);
      populateCalculator(finalResult);
    }
  } catch (e) {
    feed.innerHTML +=
      '<div class="msg system"><div class="msg-bubble" style="color:var(--down);">Error: ' +
      e.message +
      "</div></div>";
  }

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

function showExtractedData(data, feed) {
  var fields = [
    "Price",
    "Address",
    "City",
    "Total Units",
    "Cap Rate",
    "NOI",
    "Annual Rent Income (Projected)",
    "Monthly Rental Income (Projected)",
    "Unit Mix Summary",
  ];
  var grid = "";
  for (var i = 0; i < fields.length; i++) {
    var f = fields[i];
    var val = data[f] || "--";
    var label = f.replace(/\(.*\)/, "").trim();
    grid +=
      '<span class="extract-key">' +
      label +
      '</span><span class="extract-val">' +
      val +
      "</span>";
  }
  feed.innerHTML +=
    '<div class="msg system"><div class="msg-bubble">' +
    '<strong style="color:var(--text-white);font-size:11px;text-transform:uppercase;letter-spacing:0.5px;">Extracted Data</strong>' +
    '<div class="extract-grid">' +
    grid +
    "</div>" +
    '<div class="extract-populated">Calculator populated →</div>' +
    "</div></div>";
}

function populateCalculator(data) {
  var mapping = {
    purchase_price: parseCurrency(data["Price"]),
    annual_gross_rents: parseCurrency(
      data["Annual Rent Income (Projected)"]
    ),
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

function escapeHtml(str) {
  var div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
