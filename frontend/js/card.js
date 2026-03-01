/* Property card renderer */

const FIELD_ORDER = [
  "Price",
  "Address",
  "City",
  "Cap Rate",
  "Date On Market",
  "Monthly Rental Income (Projected)",
  "Monthly Rental Income (Actual)",
  "Annual Rent Income (Projected)",
  "Annual Rent Income (Actual)",
  "NOI",
  "Lot / building size",
  "Total Units",
  "Unit Mix Summary",
  "Link",
  "Description",
];

function renderPropertyCard(data) {
  var container = document.getElementById("propertyCard");
  container.textContent = "";
  container.style.display = "block";
  document.getElementById("emptyState").style.display = "none";

  var card = document.createElement("div");
  card.className = "property-card";

  // Header
  var header = document.createElement("div");
  header.className = "card-header";

  var title = document.createElement("div");
  title.className = "card-title";
  title.textContent = data["Address"] || "Unknown Property";

  var subtitle = document.createElement("div");
  subtitle.className = "card-subtitle";
  subtitle.textContent = data["City"] || "";

  header.appendChild(title);
  header.appendChild(subtitle);
  card.appendChild(header);

  // Body with fields
  var body = document.createElement("div");
  body.className = "card-body";

  for (var i = 0; i < FIELD_ORDER.length; i++) {
    var field = FIELD_ORDER[i];
    // Skip Address and City since they're in the header
    if (field === "Address" || field === "City") continue;

    var row = document.createElement("div");
    row.className = "field-row";

    var label = document.createElement("span");
    label.className = "field-label";
    label.textContent = field;

    var value = document.createElement("span");
    value.className = "field-value";

    var val = data[field];
    if (val === null || val === undefined) {
      value.className = "field-value field-null";
      value.textContent = "--";
    } else if (field === "Link" && typeof val === "string" && val.startsWith("http")) {
      var link = document.createElement("a");
      link.href = val;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      link.textContent = val.length > 60 ? val.substring(0, 57) + "..." : val;
      value.appendChild(link);
    } else {
      value.textContent = String(val);
    }

    row.appendChild(label);
    row.appendChild(value);
    body.appendChild(row);
  }

  card.appendChild(body);

  // Actions
  var actions = document.createElement("div");
  actions.className = "card-actions";

  var calcBtn = document.createElement("button");
  calcBtn.className = "btn-primary";
  calcBtn.textContent = "Open in Calculator";
  calcBtn.addEventListener("click", function () {
    openCalculatorWithData(data);
  });

  actions.appendChild(calcBtn);
  card.appendChild(actions);
  container.appendChild(card);

  // Store last parsed data globally
  window._lastParsedData = data;
}
