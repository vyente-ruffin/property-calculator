/* App initialization and calculator linking */

function openCalculator() {
  window.open("http://localhost:8501", "_blank");
}

function openCalculatorWithData(data) {
  var totalUnits = data["Total Units"];
  var params = new URLSearchParams();

  if (totalUnits !== null && totalUnits !== undefined && totalUnits > 4) {
    // Commercial (5+ units)
    params.set("property_type", "Commercial");

    var price = parseCurrency(data["Price"]);
    if (price) params.set("comm_purchase_price", String(price));

    var annualRent = parseCurrency(data["Annual Rent Income (Projected)"])
                  || parseCurrency(data["Annual Rent Income (Actual)"]);
    if (annualRent) params.set("comm_annual_gross_rents", String(annualRent));

    var noi = parseCurrency(data["NOI"]);
    if (noi) params.set("comm_annual_noi_listing", String(noi));

    if (data["Link"]) params.set("comm_property_url", data["Link"]);

    // Extract state from City
    var state = extractState(data["City"]);
    if (state) params.set("comm_state", state);
  } else {
    // Residential (<=4 units or unknown)
    params.set("property_type", "Residential");

    var price = parseCurrency(data["Price"]);
    if (price) params.set("purchase_price", String(price));

    var monthlyRent = parseCurrency(data["Monthly Rental Income (Projected)"])
                   || parseCurrency(data["Monthly Rental Income (Actual)"]);
    if (monthlyRent) params.set("monthly_rent", String(monthlyRent));

    if (data["Link"]) params.set("property_url", data["Link"]);

    var state = extractState(data["City"]);
    if (state) params.set("state", state);
  }

  window.open("http://localhost:8501?" + params.toString(), "_blank");
}

function parseCurrency(val) {
  if (!val || typeof val !== "string") return null;
  var cleaned = val.replace(/[$,]/g, "");
  var num = parseFloat(cleaned);
  return isNaN(num) ? null : Math.round(num);
}

function extractState(city) {
  if (!city) return null;
  // Match "City, ST ZIP" or "City, ST"
  var m = city.match(/,\s*([A-Z]{2})\s/);
  if (m) return m[1];
  m = city.match(/,\s*([A-Z]{2})$/);
  return m ? m[1] : null;
}
