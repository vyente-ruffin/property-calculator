/* Chat and SSE streaming */

function addChatBubble(type, text) {
  var messages = document.getElementById("chatMessages");
  var bubble = document.createElement("div");
  bubble.className = type === "user" ? "user-bubble" : "system-bubble";
  bubble.textContent = text;
  messages.appendChild(bubble);
  messages.scrollTop = messages.scrollHeight;
}

function setParseButtonEnabled(enabled) {
  var btn = document.getElementById("parseBtn");
  btn.disabled = !enabled;
  btn.textContent = enabled ? "Parse Listing" : "Parsing...";
}

async function submitListing() {
  var input = document.getElementById("chatInput");
  var text = input.value.trim();
  if (!text) return;

  // Add user bubble
  addChatBubble("user", text.length > 200 ? text.substring(0, 197) + "..." : text);
  input.value = "";

  // Disable button
  setParseButtonEnabled(false);

  // Init pipeline steps
  initSteps();

  // Hide empty state
  document.getElementById("emptyState").style.display = "none";

  try {
    var response = await fetch("/api/parse", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: text }),
    });

    if (!response.ok) {
      addChatBubble("system", "Error: " + response.status + " " + response.statusText);
      setParseButtonEnabled(true);
      return;
    }

    var reader = response.body.getReader();
    var decoder = new TextDecoder();
    var buffer = "";
    var finalData = null;

    while (true) {
      var result = await reader.read();
      if (result.done) break;

      buffer += decoder.decode(result.value, { stream: true });

      // Process complete SSE lines
      var lines = buffer.split("\n");
      buffer = lines.pop(); // Keep incomplete line in buffer

      for (var i = 0; i < lines.length; i++) {
        var line = lines[i].trim();
        if (!line.startsWith("data: ")) continue;

        try {
          var event = JSON.parse(line.substring(6));
          updateStep(event.step, event.status, event.data);

          // Capture final result
          if (event.step === "complete" && event.status === "done" && event.data && event.data.result) {
            finalData = event.data.result;
          }
        } catch (e) {
          // Ignore malformed SSE lines
        }
      }
    }

    // Render property card with final data
    if (finalData) {
      renderPropertyCard(finalData);
      addChatBubble("system", "Property parsed successfully. See the card on the right.");
    } else {
      addChatBubble("system", "Parsing completed but no final data received. Check pipeline steps for errors.");
    }
  } catch (err) {
    addChatBubble("system", "Network error: " + err.message);
  }

  setParseButtonEnabled(true);
}

// Enter key submits, Shift+Enter adds newline
document.addEventListener("DOMContentLoaded", function () {
  var input = document.getElementById("chatInput");
  input.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submitListing();
    }
  });
});
