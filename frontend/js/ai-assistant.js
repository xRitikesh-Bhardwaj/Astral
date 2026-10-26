/* ==========================================================================
   ASTRAL AI ASSISTANT JAVASCRIPT - Conversational AI Interface
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
  const chatHistory = document.getElementById("chat-history");
  const chatInput = document.getElementById("chat-input");
  const sendBtn = document.getElementById("send-btn");
  const presetBtns = document.querySelectorAll(".preset-prompt-btn");

  if (!chatHistory) return;

  // Handle Preset Question Clicks
  presetBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      const q = btn.textContent.trim().replace(/^"|"$/g, '');
      submitQuestion(q);
    });
  });

  // Handle Send Button Click
  if (sendBtn) {
    sendBtn.addEventListener("click", () => {
      const q = chatInput.value.trim();
      if (q) {
        submitQuestion(q);
        chatInput.value = "";
      }
    });
  }

  // Handle Enter Key
  if (chatInput) {
    chatInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        const q = chatInput.value.trim();
        if (q) {
          submitQuestion(q);
          chatInput.value = "";
        }
      }
    });
  }

  async function submitQuestion(question) {
    // 1. Append User Message Bubble
    appendMessage(question, "user");

    // 2. Append Loading Placeholder for AI
    const loadingId = "loading-" + Date.now();
    appendLoadingBubble(loadingId);

    // 3. Fetch Answer from Backend API
    const response = await fetch("/api/ai/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question })
    });

    removeLoadingBubble(loadingId);

    if (response.ok) {
      const data = await response.json();
      appendAIMessage(data);
    } else {
      appendMessage("Sorry, I encountered an error analyzing your business data. Please try again.", "ai");
    }
  }

  function appendMessage(text, sender) {
    const bubble = document.createElement("div");
    bubble.className = `msg-bubble ${sender === "user" ? "msg-user" : "msg-ai"}`;
    bubble.textContent = text;
    chatHistory.appendChild(bubble);
    chatHistory.scrollTop = chatHistory.scrollHeight;
  }

  function appendLoadingBubble(id) {
    const bubble = document.createElement("div");
    bubble.className = "msg-bubble msg-ai";
    bubble.id = id;
    bubble.style.fontStyle = "italic";
    bubble.style.color = "var(--color-navy-subtle)";
    bubble.textContent = "Analyzing business metrics & historical dataset...";
    chatHistory.appendChild(bubble);
    chatHistory.scrollTop = chatHistory.scrollHeight;
  }

  function removeLoadingBubble(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
  }

  function appendAIMessage(data) {
    const bubble = document.createElement("div");
    bubble.className = "msg-bubble msg-ai";

    let metricsHtml = "";
    if (data.metrics && data.metrics.length > 0) {
      metricsHtml = `
        <div style="display: flex; gap: 10px; margin: 12px 0; flex-wrap: wrap;">
          ${data.metrics.map(m => `
            <div style="background: var(--color-bg-white); border: 1px solid var(--color-border-subtle); padding: 8px 12px; border-radius: 8px;">
              <div style="font-size: 0.75rem; color: var(--color-navy-subtle); font-weight: 600;">${m.label}</div>
              <div style="font-size: 1rem; font-weight: 700; color: var(--color-green-primary);">${m.value}</div>
            </div>
          `).join("")}
        </div>
      `;
    }

    let takeawayHtml = "";
    if (data.actionable_takeaway) {
      takeawayHtml = `
        <div style="background: var(--color-green-light); border-left: 3px solid var(--color-green-primary); padding: 10px 14px; border-radius: 6px; margin-top: 10px; font-size: 0.875rem;">
          <strong style="color: var(--color-green-primary);">Recommendation:</strong> ${data.actionable_takeaway}
        </div>
      `;
    }

    bubble.innerHTML = `
      <div style="margin-bottom: 6px; font-weight: 600; font-size: 0.85rem; color: var(--color-green-primary);">ASTRAL AI Assistant</div>
      <div>${data.answer}</div>
      ${metricsHtml}
      ${takeawayHtml}
    `;

    chatHistory.appendChild(bubble);
    chatHistory.scrollTop = chatHistory.scrollHeight;
  }
});
