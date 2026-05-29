const $ = id => document.getElementById(id);

// Sidebar tab switching
document.querySelectorAll('.nav-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab-content').forEach(t => t.style.display = 'none');
    const activeTab = document.querySelector(`#${tab.dataset.tab}`);
    if (activeTab) activeTab.style.display = 'flex';

    document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');

    if (tab.dataset.tab === 'chatbot') {
      switchToBot();
    } else if (tab.dataset.tab === 'admin') {
      switchToAdmin();
    }
  });
});

document.getElementById("goBot").onclick = () => {
  document.querySelector('[data-tab="chatbot"]').click();
};
document.getElementById("goAdmin").onclick = () => {
  document.querySelector('[data-tab="admin"]').click();
};

// Add chat message to UI
function addMessage(text, senderType, box = $('chatBotBox')) {
  const div = document.createElement('div');
  let prefix = '';
  if (senderType === 'user') {
    div.className = 'chat-message user-message';
    prefix = 'YOU: ';
  } else if (senderType === 'admin') {
    div.className = 'chat-message bot-message';
    prefix = 'ADMIN: ';
  } else {
    div.className = 'chat-message bot-message';
    prefix = 'BOT: ';
  }

  const cleanText = text.replace(/^🧑‍🎓 You: |^🤖 Bot: |^🛡️ Admin: /, '');
  div.textContent = prefix + cleanText;
  box.appendChild(div);
  box.scrollTop = box.scrollHeight;
}

// Send message to chatbot
async function sendMessage() {
  const msg = $('userInput').value.trim();
  if (!msg) return;

  addMessage(msg, 'user', $('chatBotBox'));
  saveChatMessage('user', msg);
  $('userInput').value = '';

  const typing = document.createElement('div');
  typing.className = 'chat-message bot-message typing';
  typing.textContent = 'Bot is typing...';
  typing.id = 'typing-indicator';
  $('chatBotBox').appendChild(typing);

  try {
    const res = await fetch('/rasa_webhook', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: msg })
    });
    const data = await res.json();
    $('typing-indicator')?.remove();

    if (data.responses?.length) {
      data.responses.forEach(r => {
        addMessage(r.text, 'bot', $('chatBotBox'));
        saveChatMessage('bot', r.text);
      });
    } else {
      addMessage("Sorry, I couldn't connect to the bot.", 'bot', $('chatBotBox'));
    }
  } catch (e) {
    $('typing-indicator')?.remove();
    addMessage("Sorry, I couldn't connect to the bot.", 'bot', $('chatBotBox'));
  }
}

// Save chat to DB
async function saveChatMessage(sender, message) {
  const cleanMsg = message.replace(/^🧑‍🎓 You: |^🤖 Bot: /, '');
  const senderForDB = sender === 'user' ? 'student' : 'bot';
  await fetch('/save_chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      student_id,
      message_from: senderForDB,
      message: cleanMsg
    })
  });
}

// Load chatbot chat history
function loadBotChatHistory() {
  fetch('/view_chatbot_data')
    .then(res => res.json())
    .then(data => {
      console.log("Bot history:", data);  // ✅ Add this
      $('chatBotBox').innerHTML = '';
      data.forEach(m => {
        const sender = (m.sender || '').toLowerCase();
        const type = sender === 'student' ? 'user' : 'bot';
        addMessage(m.message, type, $('chatBotBox'));
      });
    })
    .catch(err => console.error("Error loading bot history", err));
}


// Send message to admin
async function sendAdminMessage() {
  const input = $('adminMsgInput');
  const msg = input.value.trim();
  if (!msg) return;

  addMessage(msg, 'user', $('adminChatBox'));
  input.value = '';

  await fetch('/send_admin_chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      student_id,
      message: msg,
      message_from: 'student'
    })
  });

  socket.emit('send_message', {
    student_id,
    message: msg,
    message_from: 'student'
  });
}

// Load admin chat history
function loadAdminHistory() {
  fetch('/view_escalation_data')
    .then(r => r.json())
    .then(msgs => {
      $('adminChatBox').innerHTML = '';
      msgs.forEach(m => {
        const senderType = m.sender === 'student' ? 'user' : 'admin';
        addMessage(m.message, senderType, $('adminChatBox'));
      });
    });
}

// Switch to bot chat view
function switchToBot() {
  $('chatHeader').textContent = "CampusBot 🤖";
  $('chatBotBox').style.display = 'flex';
  $('chatBotInput').style.display = 'flex';
  $('adminChatBox').style.display = 'none';
  $('adminChatInput').style.display = 'none';
  loadBotChatHistory();
}

// Switch to admin chat view
function switchToAdmin() {
  $('chatHeader').textContent = "Chat with Admin";
  $('chatBotBox').style.display = 'none';
  $('chatBotInput').style.display = 'none';
  $('adminChatBox').style.display = 'flex';
  $('adminChatInput').style.display = 'flex';
  loadAdminHistory();
}

$('userInput').addEventListener('keypress', e => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});


// Socket setup
const socket = io({
    transports: ['polling'] ం
,upgrade:false});
socket.emit('join_room', { room: `room_${student_id}` });
socket.on('receive_message', data => {
  if (data.student_id == student_id && data.message_from === 'admin') {
    addMessage(data.message, 'admin', $('adminChatBox'));
  }
});

document.addEventListener('DOMContentLoaded', () => {
  $('sendMessageBtn').addEventListener('click', sendMessage);
  $('sendAdminMessageBtn').addEventListener('click', sendAdminMessage);
  $('userInput').addEventListener('keypress', e => { if (e.key === 'Enter') sendMessage(); });
  $('adminMsgInput').addEventListener('keypress', e => { if (e.key === 'Enter') sendAdminMessage(); });

  document.querySelector('[data-tab="home"]').click(); // Default tab

  
  loadBotChatHistory();
  loadAdminHistory();
});
