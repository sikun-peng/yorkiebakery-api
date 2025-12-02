// static/chat.js
//
// Yorkie Bakery Chat Widget with Session Memory
// - Remembers conversation history (last 10 turns)
// - Tracks user preferences (flavors, dietary needs, etc.)
// - Session stored in localStorage + PostgreSQL
// - Auto-expires after 24 hours
//

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
// SESSION MANAGEMENT
// ===============================
let chatSessionId = null;

// Generate or retrieve session ID from localStorage
function getSessionId() {
  if (!chatSessionId) {
    // Try to get from localStorage first
    chatSessionId = localStorage.getItem('yorkie_chat_session_id');

    // If not found, generate new one
    if (!chatSessionId) {
      chatSessionId = crypto.randomUUID();
      localStorage.setItem('yorkie_chat_session_id', chatSessionId);
    }
  }
  return chatSessionId;
}

// Clear session (useful for testing or starting fresh)
function clearChatSession() {
  chatSessionId = null;
  localStorage.removeItem('yorkie_chat_session_id');
  console.log("[YorkieChat] Session cleared - next message will start new conversation");
}

// Make it globally accessible for testing in console
window.clearChatSession = clearChatSession;

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

  const userAvatar = chatBox?.dataset.userAvatar || "/static/images/default_user_profile.jpg";
  const botAvatar = chatBox?.dataset.botAvatar || "/static/images/logo_black.jpg";
  const avatarUrl = sender === "user" ? userAvatar : botAvatar;

  const msg = document.createElement("div");
  msg.classList.add(sender === "user" ? "msg-user" : "msg-bot");

  const avatar = document.createElement("div");
  avatar.classList.add("msg-avatar");
  avatar.style.backgroundImage = `url('${avatarUrl}')`;

  const bubble = document.createElement("div");
  bubble.classList.add("msg-bubble");
  bubble.innerHTML = text;

  if (sender === "user") {
    msg.appendChild(bubble);
    msg.appendChild(avatar);
  } else {
    msg.appendChild(avatar);
    msg.appendChild(bubble);
  }

  chatMessages.appendChild(msg);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// ===============================
// UPDATE MEMORY PANEL
// ===============================
function updateMemoryPanel(preferences) {
  const memoryPanel = document.getElementById("chat-memory");
  const memoryContent = document.getElementById("chat-memory-content");

  if (!memoryPanel || !memoryContent) return;

  // Build memory text
  const parts = [];

  if (preferences.flavors && preferences.flavors.length > 0) {
    parts.push(`Likes: ${preferences.flavors.join(", ")}`);
  }

  if (preferences.dietary && preferences.dietary.length > 0) {
    parts.push(`Dietary: ${preferences.dietary.join(", ")}`);
  }

  if (preferences.avoid && preferences.avoid.length > 0) {
    parts.push(`Avoids: ${preferences.avoid.join(", ")}`);
  }

  if (preferences.last_viewed && preferences.last_viewed.length > 0) {
    const recent = preferences.last_viewed.slice(-3).join(", ");
    parts.push(`Recently viewed: ${recent}`);
  }

  // Show panel if there are preferences
  if (parts.length > 0) {
    memoryContent.textContent = parts.join(" • ");
    memoryPanel.style.display = "block";
  } else {
    memoryPanel.style.display = "none";
  }
}

// ===============================
// CALL BACKEND AI (WITH SESSION MEMORY)
// ===============================
async function sendToAI(message) {
  try {
    // Get or create session ID
    const sessionId = getSessionId();

    const res = await fetch("/ai/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: message,
        session_id: sessionId
      }),
    });

    // Log everything so you can see what's going on
    console.log("[YorkieChat] HTTP status:", res.status);
    console.log("[YorkieChat] Session ID:", sessionId);

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

    // Update session ID if server returned a new one
    if (data.session_id) {
      chatSessionId = data.session_id;
      localStorage.setItem('yorkie_chat_session_id', data.session_id);
      console.log("[YorkieChat] Updated session ID:", data.session_id);
    }

    // Log preferences for debugging
    if (data.preferences) {
      console.log("[YorkieChat] User preferences:", data.preferences);
      updateMemoryPanel(data.preferences);
    }

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
