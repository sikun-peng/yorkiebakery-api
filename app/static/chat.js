// static/chat.js

// ===============================
// CHAT WIDGET ELEMENTS
// ===============================
const chatToggle = document.getElementById("chat-toggle");
const chatBox = document.getElementById("chat-box");
const closeChat = document.getElementById("close-chat");
const chatMessages = document.getElementById("chat-messages");
const chatInput = document.getElementById("chat-input-text");
const chatSend = document.getElementById("chat-send");

// ===============================
// OPEN / CLOSE WIDGET
// ===============================
chatToggle?.addEventListener("click", () => {
  if (!chatBox) return;
  chatBox.style.display = chatBox.style.display === "flex" ? "none" : "flex";
});

closeChat?.addEventListener("click", () => {
  if (!chatBox) return;
  chatBox.style.display = "none";
});

// ===============================
// RENDER A MESSAGE BUBBLE
// ===============================
function addMessage(text, sender = "user") {
  if (!chatMessages) return;

  const msg = document.createElement("div");
  msg.classList.add(sender === "user" ? "msg-user" : "msg-bot");
  msg.innerHTML = `<span>${text}</span>`;
  chatMessages.appendChild(msg);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// ===============================
// CALL BACKEND AI
// ===============================
async function sendToAI(message) {
  try {
    const res = await fetch("/ai/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });

    // Log everything so you can see what's going on
    console.log("[YorkieChat] HTTP status:", res.status);

    const rawText = await res.text();
    console.log("[YorkieChat] raw response text:", rawText);

    if (!res.ok) {
      console.error("[YorkieChat] Non-OK response:", res.status, rawText);
      return "🐶 Oops, the server had a little hiccup.";
    }

    let data;
    try {
      data = JSON.parse(rawText);
    } catch (jsonErr) {
      console.error("[YorkieChat] JSON parse error:", jsonErr);
      return "🐶 Oops, I couldn't understand the response.";
    }

    console.log("[YorkieChat] parsed JSON:", data);

    if (!data || typeof data.reply !== "string") {
      console.error("[YorkieChat] Missing reply field:", data);
      return "🐶 Oops, I got confused by the answer.";
    }

    return data.reply;
  } catch (err) {
    console.error("[YorkieChat] fetch error:", err);
    return "🐶 Oops, I got distracted chasing a biscuit.";
  }
}

// ===============================
// SEND BUTTON HANDLER
// ===============================
chatSend?.addEventListener("click", async () => {
  if (!chatInput || !chatMessages) return;

  const text = chatInput.value.trim();
  if (!text) return;

  // User message
  addMessage(text, "user");
  chatInput.value = "";

  // Temporary "thinking" bubble
  addMessage("🐶 ...thinking...", "bot");

  // Call backend
  const reply = await sendToAI(text);

  // Replace the last bot message (the thinking one)
  const lastChild = chatMessages.lastElementChild;
  if (lastChild) {
    lastChild.innerHTML = `<span>${reply}</span>`;
  } else {
    addMessage(reply, "bot");
  }
});

// ===============================
// ENTER KEY TO SEND
// ===============================
chatInput?.addEventListener("keypress", (e) => {
  if (e.key === "Enter") {
    e.preventDefault();
    chatSend?.click();
  }
});

// Optional: small greeting message on load
document.addEventListener("DOMContentLoaded", () => {
  if (chatMessages && chatMessages.children.length === 0) {
    addMessage("“Woof! I’m Oscar 🐶, CEO of YorkieBakery and your pastry guide!\n" +
        "What delicious treat are you craving today?”", "bot");
  }
});
