// ==================== MODULE MESSAGERIE ====================
// Chargement des conversations, affichage du chat et envoi de messages

function loadMessengerContent() {
    const convList = document.getElementById('conversationsList');
    if (!convList) return;

    convList.innerHTML = `
        <div style="padding:1rem; border-bottom:1px solid var(--border); font-weight:600;">
            💬 Messages <span style="color:var(--accent)">(2 non lus)</span>
        </div>
        <div class="conv-item active" onclick="loadChat('Aïcha')">
            <div class="avatar">AK</div>
            <div class="conv-info">
                <div class="conv-name">Aïcha Kpènou</div>
                <div class="conv-preview">Ok, lundi 19h ça me va !</div>
            </div>
            <div class="notif-dot"></div>
        </div>
        <div class="conv-item" onclick="loadChat('Moussa')">
            <div class="avatar">MB</div>
            <div class="conv-info">
                <div class="conv-name">Moussa Bello</div>
                <div class="conv-preview">Je suis dispo samedi matin</div>
            </div>
        </div>
    `;

    loadChat('Aïcha');
}

function loadChat(name) {
    const chatWindow = document.getElementById('chatWindow');
    if (!chatWindow) return;

    const initials = name === 'Aïcha' ? 'AK' : 'MB';
    const status   = name === 'Aïcha' ? 'Mentor · En ligne' : 'Mentor · Hors ligne';

    chatWindow.innerHTML = `
        <div class="chat-header">
            <div class="avatar">${initials}</div>
            <div>
                <h4>${name}</h4>
                <span class="match-meta">${status}</span>
            </div>
        </div>
        <div class="chat-messages" id="chatMessages">
            <div class="message received">
                <div class="message-bubble">Salut ! J'ai vu ta demande, je peux t'aider pour l'algo 😊</div>
                <div class="msg-time">14:20</div>
            </div>
            <div class="message sent">
                <div class="message-bubble">Super ! Je galère sur les arbres binaires</div>
                <div class="msg-time">14:25</div>
            </div>
            <div class="message received">
                <div class="message-bubble">On peut se faire une session lundi 19h ?</div>
                <div class="msg-time">14:28</div>
            </div>
        </div>
        <div class="chat-input-area">
            <input type="text" class="chat-input" placeholder="Écrire un message..." id="msgInput">
            <button class="btn btn-accent" onclick="sendMessage()">Envoyer</button>
        </div>
    `;

    window.currentChat = name;
}

function sendMessage() {
    const input = document.getElementById('msgInput');
    if (!input || !input.value.trim()) return;

    const messagesDiv = document.getElementById('chatMessages');

    // Message envoyé
    const newMsg = document.createElement('div');
    newMsg.className = 'message sent';
    newMsg.innerHTML = `
        <div class="message-bubble">${input.value}</div>
        <div class="msg-time">Maintenant</div>
    `;
    messagesDiv.appendChild(newMsg);
    input.value = '';
    messagesDiv.scrollTop = messagesDiv.scrollHeight;

    // Réponse automatique simulée
    setTimeout(() => {
        const reply = document.createElement('div');
        reply.className = 'message received';
        reply.innerHTML = `
            <div class="message-bubble">Merci ! Je te réponds dans quelques minutes</div>
            <div class="msg-time">à l'instant</div>
        `;
        messagesDiv.appendChild(reply);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }, 1000);
}