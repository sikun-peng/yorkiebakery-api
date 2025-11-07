const chatToggle = document.getElementById("chat-toggle");
const chatBox = document.getElementById("chat-box");
const closeChat = document.getElementById("close-chat");
const chatMessages = document.getElementById("chat-messages");
const chatInput = document.getElementById("chat-input-text");
const chatSend = document.getElementById("chat-send");

chatToggle?.addEventListener("click", () => {
  chatBox.style.display = (chatBox.style.display === "flex") ? "none" : "flex";
});

closeChat?.addEventListener("click", () => {
  chatBox.style.display = "none";
});

function addMessage(text, sender="user") {
  const msg = document.createElement("div");
  msg.classList.add(sender === "user" ? "msg-user" : "msg-bot");
  msg.innerHTML = `<span>${text}</span>`;
  chatMessages.appendChild(msg);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function sendToAI(message) {
  const res = await fetch("/ai/chat", {
    method:"POST",
    headers:{ "Content-Type":"application/json" },
    body: JSON.stringify({ message })
  });
  try {
    const data = await res.json();
    return data.reply;
  } catch {
    return "🐶 Oops, I got distracted chasing a biscuit.";
  }
}

chatSend?.addEventListener("click", async () => {
  const text = chatInput.value.trim();
  if(!text) return;

  addMessage(text, "user");
  chatInput.value = "";
  addMessage("🐶 ...thinking...", "bot");

  const reply = await sendToAI(text);
  chatMessages.lastChild.innerHTML = `<span>${reply}</span>`;
});

chatInput?.addEventListener("keypress", e => {
  if (e.key === "Enter") chatSend.click();
});