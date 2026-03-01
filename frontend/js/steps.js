/* Pipeline step progress display */

const STEP_LABELS = {
  parse_input: "Parse Input",
  scrape_url: "Scrape URL",
  extract_fields: "Extract Fields",
  search_link: "Search Link",
  rentcast: "Rentcast",
  reextract: "Re-extract",
  validate: "Validate",
  complete: "Complete",
};

const STATUS_ICONS = {
  pending: "\u23F3",   // hourglass
  running: "\u23F3",
  done: "\u2705",      // green check
  skipped: "\u23ED",   // skip
  error: "\u274C",     // red X
};

function initSteps() {
  const container = document.getElementById("pipelineSteps");
  container.textContent = "";
  const section = document.getElementById("pipelineSection");
  section.style.display = "block";

  for (const [key, label] of Object.entries(STEP_LABELS)) {
    const row = document.createElement("div");
    row.className = "step-row pending";
    row.id = "step-" + key;

    const iconSpan = document.createElement("span");
    iconSpan.className = "step-icon";
    iconSpan.textContent = STATUS_ICONS.pending;

    const nameSpan = document.createElement("span");
    nameSpan.className = "step-name";
    nameSpan.textContent = label;

    const detailSpan = document.createElement("span");
    detailSpan.className = "step-detail";
    detailSpan.id = "step-detail-" + key;
    detailSpan.textContent = "Waiting...";

    row.appendChild(iconSpan);
    row.appendChild(nameSpan);
    row.appendChild(detailSpan);
    container.appendChild(row);
  }
}

function updateStep(step, status, data) {
  const row = document.getElementById("step-" + step);
  if (!row) return;

  row.className = "step-row " + status;
  const icon = row.querySelector(".step-icon");
  icon.textContent = STATUS_ICONS[status] || STATUS_ICONS.pending;

  const detail = document.getElementById("step-detail-" + step);

  if (status === "running") {
    detail.textContent = "Processing...";
  } else if (status === "done") {
    if (step === "parse_input" && data) {
      if (data.is_url_only) {
        detail.textContent = "URL detected — will scrape";
      } else {
        detail.textContent = "Text: " + data.text_length + " chars" + (data.has_url ? " + URL" : "");
      }
    } else if (step === "scrape_url" && data) {
      detail.textContent = "Scraped " + data.text_length + " chars";
    } else if (step === "extract_fields") {
      detail.textContent = "15 fields extracted";
    } else if (step === "search_link" && data) {
      detail.textContent = data.url ? "Found: " + data.url : "No URL found";
    } else if (step === "rentcast" && data) {
      if (data.rent) {
        detail.textContent = "Projected: " + data.rent.monthly_formatted + "/mo";
      } else {
        detail.textContent = data.message || "Done";
      }
    } else if (step === "reextract") {
      detail.textContent = "Enriched data merged";
    } else if (step === "validate" && data) {
      var nullCount = data.null_fields ? data.null_fields.length : 0;
      detail.textContent = data.valid ? "All 15 fields present (" + nullCount + " null)" : "Missing keys: " + (data.missing_keys || []).join(", ");
    } else if (step === "complete") {
      detail.textContent = "Done";
    } else {
      detail.textContent = "Done";
    }
  } else if (status === "skipped" && data) {
    detail.textContent = data.reason || "Skipped";
  } else if (status === "error" && data) {
    detail.textContent = "Error: " + (data.message || "Unknown error");
  }
}
