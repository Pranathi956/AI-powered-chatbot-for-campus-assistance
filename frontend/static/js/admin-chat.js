const socket = io();  // Connects to Flask-SocketIO server

const chatBox = document.getElementById("chatBox");
const msgInput = document.getElementById("adminMsgInput");

// ✅ JOIN ROOM
socket.emit("join_room", { room: `room_${student_id}` });

// ✅ LOAD CHAT HISTORY
fetch(`/view_escalation_data`)
  .then(res => res.json())
  .then(data => {
    data.forEach(msg => {
      const sender = msg.sender;
      const message = msg.message;
      const className = sender === "student" ? "user-message" : "bot-message";
      const label = sender === "student" ? "🧑‍🎓 You" : "👨‍🏫 Admin";
      addMessage(`${label}: ${message}`, className);
    });
  });

// ✅ SEND MESSAGE
function sendAdminMessage() {
  const msg = msgInput.value.trim();
  if (!msg) return;

  addMessage(`🧑‍🎓 You: ${msg}`, "user-message");
  socket.emit("send_message", {
    student_id: student_id,
    message: msg,
    message_from: "student"
  });
  msgInput.value = "";
}

// ✅ RECEIVE MESSAGE
socket.on("receive_message", (data) => {
  if (parseInt(data.student_id) === parseInt(student_id)) {
    if (data.message_from === "admin") {
      addMessage(`👨‍🏫 Admin: ${data.message}`, "bot-message");
    }
  }
});

// ✅ ADD MESSAGE TO CHATBOX
function addMessage(text, className) {
  const div = document.createElement("div");
  div.className = "chat-message " + className;
  div.textContent = text;
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
}
