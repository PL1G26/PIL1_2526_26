// ====================================================
// STATE GLOBAL
// ====================================================
const state = {
  posts: [],
  matches: [],
  conversations: [],
  currentConv: null,
  postFilter: 'all',
  matchFilter: 'all',
  searchFilter: 'all',
};

let currentUser = null;
let currentRating = 0;
let dashRating = 0;

// ====================================================
// NAVIGATION
// ====================================================
function showView(id) {
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  window.scrollTo(0, 0);
  // Mettre à jour le formulaire de témoignage selon l'état de connexion
  updateTestimonialForm();
}

function switchTab(tab) {
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.sidebar-item').forEach(b => b.classList.remove('active'));
  const tabEl = document.getElementById('tab-' + tab);
  if (tabEl) tabEl.classList.add('active');
  const btn = document.getElementById('tab-btn-' + tab);
  if (btn) btn.classList.add('active');
  if (tab === 'search') renderSearchResults();
}

function scrollToAbout() {
  document.getElementById('about').scrollIntoView({ behavior: 'smooth' });
}

function scrollToContact() {
  document.getElementById('contact').scrollIntoView({ behavior: 'smooth' });
}

function scrollToFeatures() {
  document.getElementById('features').scrollIntoView({ behavior: 'smooth' });
}

function scrollToTestimonials() {
  document.getElementById('testimonials').scrollIntoView({ behavior: 'smooth' });
}

// ====================================================
// MODE SOMBRE
// ====================================================
function toggleDarkMode() {
  document.body.classList.toggle('dark-mode');
  localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
  updateDarkIcons();
}

function updateDarkIcons() {
  const isDark = document.body.classList.contains('dark-mode');
  const sunSVG = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>`;
  const moonSVG = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>`;
  const icon = isDark ? sunSVG : moonSVG;
  ['dark-toggle-landing', 'dark-toggle-dash'].forEach(id => {
    const btn = document.getElementById(id);
    if (btn) btn.innerHTML = icon;
  });
}

// ====================================================
// COMPTES & AUTH
// ====================================================
const accounts = [
  {
    email: 'mona.ago@ifri-uac.bj',
    phone: '22996781151',
    password: 'ifri1234',
    prenom: 'Mona', nom: 'AGO', level: 'L2', field: 'IA'
  }
];

function showFieldError(inputEl, msg) {
  const existing = inputEl.parentElement.querySelector('.field-err');
  if (existing) existing.remove();
  inputEl.style.borderColor = '#e53e3e';
  const err = document.createElement('div');
  err.className = 'field-err';
  err.style.cssText = 'color:#e53e3e;font-size:12px;margin-top:4px;display:flex;align-items:center;gap:4px;';
  err.innerHTML = `<span>⚠️</span> ${msg}`;
  inputEl.parentElement.appendChild(err);
}

function clearFieldError(inputEl) {
  const existing = inputEl.parentElement.querySelector('.field-err');
  if (existing) existing.remove();
  inputEl.style.borderColor = '';
}

function clearAllErrors(ids) {
  ids.forEach(id => {
    const el = document.getElementById(id);
    if (el) clearFieldError(el);
  });
}

function doLogin() {
  const emailEl = document.getElementById('login-email');
  const passEl = document.getElementById('login-pass');
  const email = emailEl.value.trim();
  const pass = passEl.value;
  let hasError = false;

  clearAllErrors(['login-email', 'login-pass']);
  document.getElementById('login-alert').classList.add('hidden');

  if (!email) { showFieldError(emailEl, 'Ce champ est obligatoire.'); hasError = true; }
  if (!pass) { showFieldError(passEl, 'Ce champ est obligatoire.'); hasError = true; }
  if (hasError) return;

  const normalizePhone = v => v.replace(/[\s+\-()]/g, '');
  const account = accounts.find(a =>
    a.email === email || normalizePhone(a.phone) === normalizePhone(email)
  );

  if (!account) {
    showAlert('login-alert', 'error', '❌ Aucun compte trouvé avec cet email ou ce numéro.');
    showFieldError(emailEl, 'Identifiant inconnu.');
    return;
  }
  if (account.password !== pass) {
    showAlert('login-alert', 'error', '🔑 Mot de passe incorrect.');
    showFieldError(passEl, 'Mot de passe incorrect.');
    passEl.value = '';
    passEl.focus();
    return;
  }

  const isDemo = account.email === 'mona.ago@ifri-uac.bj';
  launchDashboard(account.prenom, account.nom, account.level, account.field, isDemo);
}

function doDemo() {
  document.getElementById('login-email').value = 'mona.ago@ifri-uac.bj';
  document.getElementById('login-pass').value = 'ifri1234';
  clearAllErrors(['login-email', 'login-pass']);
  document.getElementById('login-alert').classList.add('hidden');
  setTimeout(() => launchDashboard('Mona', 'AGO', 'L2', 'IA', true), 300);
}

function doRegister() {
  const prenomEl = document.getElementById('reg-prenom');
  const nomEl = document.getElementById('reg-nom');
  const emailEl = document.getElementById('reg-email');
  const phoneEl = document.getElementById('reg-phone');
  const filiereEl = document.getElementById('reg-filiere');
  const niveauEl = document.getElementById('reg-niveau');
  const passEl = document.getElementById('reg-pass');
  const pass2El = document.getElementById('reg-pass2');

  const prenom = prenomEl.value.trim();
  const nom = nomEl.value.trim();
  const email = emailEl.value.trim();
  const phone = phoneEl.value.trim();
  const filiere = filiereEl.value;
  const niveau = niveauEl.value;
  const pass = passEl.value;
  const pass2 = pass2El.value;

  clearAllErrors(['reg-prenom', 'reg-nom', 'reg-email', 'reg-phone', 'reg-filiere', 'reg-niveau', 'reg-pass', 'reg-pass2']);
  document.getElementById('reg-alert').classList.add('hidden');

  let hasError = false;

  if (!prenom) { showFieldError(prenomEl, 'Le prénom est obligatoire.'); hasError = true; }
  if (!nom) { showFieldError(nomEl, 'Le nom est obligatoire.'); hasError = true; }

  if (!email) {
    showFieldError(emailEl, "L'adresse email est obligatoire."); hasError = true;
  } else if (!email.includes('@') || !email.includes('.') || email.indexOf('@') < 1) {
    showFieldError(emailEl, "Format d'email invalide (ex: nom@domaine.bj)."); hasError = true;
  } else if (accounts.find(a => a.email === email)) {
    showFieldError(emailEl, 'Cet email est déjà utilisé par un compte existant.'); hasError = true;
  }

  if (!phone) {
    showFieldError(phoneEl, 'Le numéro de téléphone est obligatoire.'); hasError = true;
  } else {
    const digits = phone.replace(/[\s+\-()]/g, '');
    if (!/^\d{8,15}$/.test(digits)) {
      showFieldError(phoneEl, 'Numéro invalide — chiffres uniquement (8 à 15 chiffres).'); hasError = true;
    } else if (accounts.find(a => a.phone.replace(/[\s+\-()]/g, '') === digits)) {
      showFieldError(phoneEl, 'Ce numéro est déjà associé à un compte.'); hasError = true;
    }
  }

  if (!filiere) { showFieldError(filiereEl, 'Choisis ta filière.'); hasError = true; }
  if (!niveau) { showFieldError(niveauEl, 'Choisis ton niveau.'); hasError = true; }

  if (!pass) {
    showFieldError(passEl, 'Le mot de passe est obligatoire.'); hasError = true;
  } else if (pass.length < 8) {
    showFieldError(passEl, 'Le mot de passe doit contenir au moins 8 caractères.'); hasError = true;
  }

  if (!pass2) {
    showFieldError(pass2El, 'Confirme ton mot de passe.'); hasError = true;
  } else if (pass && pass !== pass2) {
    showFieldError(pass2El, 'Les mots de passe ne correspondent pas.'); hasError = true;
    pass2El.value = '';
  }

  if (hasError) return;

  const newAccount = { email, phone: phone.replace(/[\s+\-()]/g, ''), password: pass, prenom, nom, level: niveau, field: filiere };
  accounts.push(newAccount);

  const al = document.getElementById('reg-alert');
  al.className = 'alert alert-success';
  al.textContent = `✅ Compte créé ! Bienvenue ${prenom} 🎉 Connexion en cours…`;
  al.classList.remove('hidden');

  setTimeout(() => launchDashboard(prenom, nom, niveau, filiere), 1200);
}

function doLogout() {
  currentUser = null;
  updateTestimonialForm();
  showView('view-landing');
}

// ====================================================
// DASHBOARD
// ====================================================
function launchDashboard(prenom, nom, level, field, isDemo = false) {
  currentUser = { prenom, nom, level, field };

  if (isDemo) {
    state.posts = [
      { id: 1, type: 'offer', skill: 'Python', mode: 'online', desc: 'Sessions débutants, 2h par séance. Exercices pratiques.', day: 'Mercredi', start: '14:00', end: '16:00', active: true },
      { id: 2, type: 'offer', skill: 'SQL', mode: 'both', desc: 'Modélisation BDD, requêtes avancées.', day: 'Samedi', start: '10:00', end: '12:00', active: true },
      { id: 3, type: 'request', skill: 'Algorithmique', mode: 'both', desc: "Besoin d'aide pour les algo de tri et graphes.", day: 'Dimanche', start: '15:00', end: '17:00', active: true },
      { id: 4, type: 'request', skill: 'Réseaux', mode: 'online', desc: 'Cours sur TCP/IP et les protocoles.', day: 'Samedi', start: '14:00', end: '16:00', active: true },
    ];
    state.matches = [
      { id: 1, name: 'Adorée', initials: 'AD', color: 'av-pink', field: 'GL', level: 'L3', skill: 'Algorithmique', score: 85, days: 'Samedi, Dimanche', mode: 'En ligne', status: 'pending' },
      { id: 2, name: 'Jody', initials: 'JD', color: 'av-blue', field: 'IA', level: 'L2', skill: 'Réseaux', score: 70, days: 'Dimanche', mode: 'Présentiel', status: 'pending' },
      { id: 3, name: 'Jean De Dieu', initials: 'JD', color: 'av-amber', field: 'IM', level: 'L1', skill: 'Algorithmique', score: 55, days: 'Samedi', mode: 'Les deux', status: 'pending' },
      { id: 4, name: 'Dels Marcel', initials: 'DM', color: 'av-green', field: 'GL', level: 'L2', skill: 'Python', score: 92, days: 'Mercredi', mode: 'En ligne', status: 'accepted' },
      { id: 5, name: 'Estebania', initials: 'ET', color: 'av-blue', field: 'SI', level: 'L3', skill: 'Python', score: 60, days: 'Vendredi', mode: 'En ligne', status: 'rejected' },
    ];
    state.conversations = [
      {
        id: 1, matchId: 4, name: 'Dels Marcel', initials: 'DM', color: 'av-green', preview: 'Super, à mercredi !', time: '14:32', unread: 0,
        messages: [
          { sent: false, text: 'Salut ! Je suis disponible mercredi pour la session Python.', time: '14:28' },
          { sent: true, text: 'Parfait ! On se retrouve à 14h en ligne alors ?', time: '14:30' },
          { sent: false, text: 'Super, à mercredi !', time: '14:32' },
        ]
      },
      {
        id: 2, matchId: 4, name: 'Adorée', initials: 'AD', color: 'av-pink', preview: "Tu peux m'expliquer les arbres binaires ?", time: 'Hier', unread: 2,
        messages: [
          { sent: false, text: 'Bonjour ! Notre match a été accepté, super 🎉', time: 'Hier 09:15' },
          { sent: true, text: "Oui, contente de t'avoir comme mentor ! On commence quand ?", time: 'Hier 10:00' },
          { sent: false, text: "Tu peux m'expliquer les arbres binaires ?", time: 'Hier 10:05' },
        ]
      },
    ];
  } else {
    state.posts = [];
    state.matches = [];
    state.conversations = [];
  }

  state.currentConv = null;
  state.postFilter = 'all';
  state.matchFilter = 'all';

  const initials = (prenom[0] || '') + (nom[0] || '');
  document.getElementById('nav-username').textContent = prenom;
  document.getElementById('sidebar-name').textContent = prenom + ' ' + nom;
  document.getElementById('sidebar-meta').textContent = level + ' · ' + field;
  document.getElementById('sidebar-avatar').textContent = initials;
  document.getElementById('profile-photo-big').textContent = initials;

  const welcomeTitle = document.getElementById('welcome-title');
  const welcomeSub = document.getElementById('welcome-subtitle');
  if (welcomeTitle) welcomeTitle.textContent = `Bonjour, ${prenom} ! 👋`;
  if (welcomeSub) {
    if (isDemo) {
      const pending = state.matches.filter(m => m.status === 'pending').length;
      const unread = state.conversations.reduce((s, c) => s + c.unread, 0);
      welcomeSub.innerHTML = `Tu as <strong>${pending} nouvelles correspondances</strong> et <strong>${unread} message${unread > 1 ? 's' : ''}</strong> non lu${unread > 1 ? 's' : ''}.`;
    } else {
      welcomeSub.textContent = `Bienvenue sur IFRI MentorLink, ${prenom} ! Crée tes premières offres et trouve ton mentor.`;
    }
  }

  const mPending = document.getElementById('metric-pending');
  const mAccepted = document.getElementById('metric-accepted');
  const mPosts = document.getElementById('metric-posts');
  if (mPending) mPending.textContent = state.matches.filter(m => m.status === 'pending').length;
  if (mAccepted) mAccepted.textContent = state.matches.filter(m => m.status === 'accepted').length;
  if (mPosts) mPosts.textContent = state.posts.filter(p => p.active).length;

  const pfPrenom = document.getElementById('pf-prenom');
  const pfNom = document.getElementById('pf-nom');
  if (pfPrenom) pfPrenom.value = prenom;
  if (pfNom) pfNom.value = nom;

  const chatArea = document.getElementById('chat-area');
  if (chatArea) chatArea.innerHTML = `
    <div class="chat-placeholder">
      <div class="chat-placeholder-icon">💬</div>
      <h4>Sélectionne une conversation</h4>
      <p style="font-size:13px;margin-top:0.5rem;">Tes conversations actives s'affichent à gauche.<br>La messagerie est disponible pour les matches acceptés.</p>
    </div>`;

  const badges = document.querySelectorAll('.sidebar-item .badge-count');
  if (badges[0]) badges[0].textContent = state.matches.filter(m => m.status === 'pending').length;
  if (badges[1]) badges[1].textContent = 0;

  renderPosts();
  renderMatches();
  renderHomeMatchPreview();
  renderConversations();
  showView('view-dashboard');
  switchTab('home');

  // Mettre à jour le formulaire de témoignages
  updateTestimonialForm();

  ['reg-prenom', 'reg-nom', 'reg-email', 'reg-phone', 'reg-filiere', 'reg-niveau', 'reg-pass', 'reg-pass2', 'reg-bio'].forEach(id => {
    const el = document.getElementById(id);
    if (!el) return;
    el.tagName === 'SELECT' ? el.selectedIndex = 0 : el.value = '';
    clearFieldError(el);
  });
  const regAlert = document.getElementById('reg-alert');
  if (regAlert) regAlert.classList.add('hidden');
}

// ====================================================
// PROFIL
// ====================================================
function saveProfile() {
  const al = document.getElementById('profile-alert');
  al.className = 'alert alert-success'; al.textContent = '✅ Profil mis à jour avec succès !';
  al.classList.remove('hidden');
  setTimeout(() => al.classList.add('hidden'), 3000);
}

function addSkill() {
  const name = document.getElementById('skill-to-add').value;
  const type = document.getElementById('skill-type').value;
  if (!name) return;
  const container = document.getElementById(type + '-skills');
  const chip = document.createElement('div');
  chip.className = 'skill-chip';
  chip.style.borderColor = type === 'weak' ? '#F4C0D1' : '';
  chip.innerHTML = `<span>${name}</span><button class="skill-chip-remove" onclick="removeSkill(this,'${type}','${name}')">×</button>`;
  container.appendChild(chip);
  document.getElementById('skill-to-add').value = '';
}

function removeSkill(btn) { btn.parentElement.remove(); }

function addAvail() {
  const day = document.getElementById('avail-day').value;
  const start = document.getElementById('avail-start').value;
  const end = document.getElementById('avail-end').value;
  if (!day || !start || !end) return;
  const list = document.getElementById('avail-list');
  const item = document.createElement('div');
  item.className = 'avail-item';
  item.innerHTML = `<span class="day">${day}</span><span class="time">${start} — ${end}</span><button class="btn btn-ghost btn-sm" onclick="removeAvail(this)">×</button>`;
  list.appendChild(item);
}

function removeAvail(btn) { btn.parentElement.remove(); }

// ====================================================
// POSTS
// ====================================================
function renderPosts() {
  const container = document.getElementById('posts-list');
  const filtered = state.postFilter === 'all' ? state.posts : state.posts.filter(p => p.type === state.postFilter);
  if (filtered.length === 0) {
    container.innerHTML = `<div class="empty-state"><div class="empty-state-icon">📝</div><h4>Aucun post</h4><p>Crée ton premier post pour commencer.</p></div>`;
    return;
  }
  container.innerHTML = filtered.map(p => `
    <div class="post-card">
      <div class="post-card-header">
        <div>
          <span class="post-type-badge ${p.type === 'offer' ? 'post-offer' : 'post-request'}">${p.type === 'offer' ? 'Offre' : 'Demande'}</span>
          <div class="post-card-skill" style="margin-top:6px;">${p.skill}</div>
        </div>
        <div class="post-card-actions">
          <button class="btn btn-outline btn-sm">✏️ Modifier</button>
          <button class="btn btn-danger btn-sm" onclick="deletePost(${p.id})">🗑 Supprimer</button>
        </div>
      </div>
      ${p.desc ? `<div class="post-card-desc">${p.desc}</div>` : ''}
      <div class="post-card-meta">
        <span>📅 ${p.day} · ${p.start}–${p.end}</span>
        <span>📍 ${p.mode === 'online' ? 'En ligne' : p.mode === 'offline' ? 'Présentiel' : 'En ligne / Présentiel'}</span>
        <span style="color:var(--brand);font-weight:500;">● Actif</span>
      </div>
    </div>
  `).join('');
}

function filterPosts(type, el) {
  state.postFilter = type;
  document.querySelectorAll('#tab-posts .filter-chip').forEach(c => c.classList.remove('active'));
  el.classList.add('active');
  renderPosts();
}

function deletePost(id) {
  state.posts = state.posts.filter(p => p.id !== id);
  renderPosts();
}

function openPostForm() { document.getElementById('post-form-modal').classList.remove('hidden'); }
function closePostForm() { document.getElementById('post-form-modal').classList.add('hidden'); }

function submitPost() {
  const type = document.getElementById('post-type').value;
  const skill = document.getElementById('post-skill').value;
  const mode = document.getElementById('post-mode').value;
  const desc = document.getElementById('post-desc').value;
  const day = document.getElementById('pm-day').value;
  const start = document.getElementById('pm-start').value;
  const end = document.getElementById('pm-end').value;
  if (!skill) { alert('Choisis une matière.'); return; }
  state.posts.push({ id: Date.now(), type, skill, mode, desc, day, start, end, active: true });
  closePostForm();
  renderPosts();
  updateMetrics();
}

// ====================================================
// MATCHES
// ====================================================
function renderMatches(filterStatus) {
  const status = filterStatus || state.matchFilter;
  const container = document.getElementById('matches-list');
  const filtered = status === 'all' ? state.matches : state.matches.filter(m => m.status === status);
  if (filtered.length === 0) {
    container.innerHTML = `<div class="empty-state"><div class="empty-state-icon">🔗</div><h4>Aucune correspondance</h4><p>L'algorithme de matching calculera tes correspondances automatiquement.</p></div>`;
    return;
  }
  container.innerHTML = filtered.map(m => {
    const pct = m.score;
    const actions = m.status === 'pending'
      ? `<button class="btn btn-primary btn-sm" onclick="acceptMatch(${m.id})">✅ Accepter</button>
         <button class="btn btn-danger btn-sm" onclick="rejectMatch(${m.id})">✕ Refuser</button>`
      : m.status === 'accepted'
        ? `<span class="match-accepted-badge">✅ Accepté</span>
         <button class="btn btn-outline btn-sm" onclick="switchTab('chat')">💬 Message</button>`
        : `<span class="match-rejected-badge">✕ Refusé</span>`;
    return `
    <div class="match-card" id="match-card-${m.id}">
      <div class="match-card-header">
        <div class="avatar ${m.color}" style="width:48px;height:48px;font-size:16px;">${m.initials}</div>
        <div class="match-card-info">
          <div class="match-user-name">${m.name}</div>
          <div class="match-user-meta">${m.level} · ${m.field} · Mentor pour <strong>${m.skill}</strong></div>
        </div>
        <div class="match-score-ring" style="--score:${pct}">
          <div class="match-score-inner">${m.score}</div>
        </div>
      </div>
      <div class="match-details">
        <div class="match-detail-item">
          <div class="match-detail-label">Matière</div>
          <div class="match-detail-value">📚 ${m.skill}</div>
        </div>
        <div class="match-detail-item">
          <div class="match-detail-label">Disponibilités communes</div>
          <div class="match-detail-value">📅 ${m.days}</div>
        </div>
        <div class="match-detail-item">
          <div class="match-detail-label">Format</div>
          <div class="match-detail-value">📍 ${m.mode}</div>
        </div>
      </div>
      <div class="match-actions">${actions}</div>
    </div>`;
  }).join('');
}

function renderHomeMatchPreview() {
  const container = document.getElementById('home-matches-preview');
  const top3 = state.matches.filter(m => m.status === 'pending').slice(0, 3);
  if (top3.length === 0) { container.innerHTML = '<p style="color:var(--text3);font-size:13px;">Aucune correspondance en attente.</p>'; return; }
  container.innerHTML = top3.map(m => `
    <div style="display:flex;align-items:center;gap:10px;padding:10px 0;border-bottom:1px solid var(--border);">
      <div class="avatar ${m.color}" style="width:36px;height:36px;font-size:13px;">${m.initials}</div>
      <div style="flex:1;"><div style="font-weight:600;font-size:14px;">${m.name}</div><div style="font-size:12px;color:var(--text3);">Mentor pour ${m.skill}</div></div>
      <div style="font-family:'Syne',sans-serif;font-weight:800;color:var(--brand-dark);font-size:14px;">${m.score} pts</div>
      <button class="btn btn-outline btn-sm" onclick="switchTab('matches')">Voir →</button>
    </div>
  `).join('');
}

function filterMatches(status, el) {
  state.matchFilter = status;
  document.querySelectorAll('#tab-matches .filter-chip').forEach(c => c.classList.remove('active'));
  el.classList.add('active');
  renderMatches(status);
}

function acceptMatch(id) {
  const match = state.matches.find(m => m.id === id);
  match.status = 'accepted';
  const alreadyExists = state.conversations.find(c => c.matchId === id);
  if (!alreadyExists) {
    const now = new Date();
    const time = `${now.getHours()}:${String(now.getMinutes()).padStart(2, '0')}`;
    state.conversations.unshift({
      id: Date.now(),
      matchId: id,
      name: match.name,
      initials: match.initials,
      color: match.color,
      preview: `Bonjour ! Notre match pour ${match.skill} a été accepté 🎉`,
      time: time,
      unread: 1,
      messages: [
        { sent: false, text: `Bonjour ! Notre match pour ${match.skill} a été accepté 🎉 Je suis disponible ${match.days}. On commence quand ?`, time }
      ]
    });
  }
  const pending = state.matches.filter(m => m.status === 'pending').length;
  const badgeEl = document.querySelectorAll('.sidebar-item .badge-count')[0];
  if (badgeEl) badgeEl.textContent = pending;
  const totalUnread = state.conversations.reduce((sum, c) => sum + c.unread, 0);
  const msgBadge = document.querySelectorAll('.sidebar-item .badge-count')[1];
  if (msgBadge) msgBadge.textContent = totalUnread || 0;
  renderMatches();
  renderHomeMatchPreview();
  renderConversations();
  updateMetrics();
  showToast(`✅ Match avec ${match.name} accepté ! Un message a été envoyé.`, 'success');
}

function rejectMatch(id) {
  const card = document.getElementById('match-card-' + id);
  if (card) {
    card.style.transition = 'all 0.35s ease';
    card.style.opacity = '0';
    card.style.transform = 'translateX(40px) scale(0.95)';
    setTimeout(() => {
      state.matches = state.matches.filter(m => m.id !== id);
      renderMatches();
      renderHomeMatchPreview();
      updateMetrics();
      const pending = state.matches.filter(m => m.status === 'pending').length;
      const badgeEl = document.querySelectorAll('.sidebar-item .badge-count')[0];
      if (badgeEl) badgeEl.textContent = pending;
    }, 350);
  } else {
    state.matches = state.matches.filter(m => m.id !== id);
    renderMatches();
    renderHomeMatchPreview();
  }
}

// ====================================================
// MESSAGERIE
// ====================================================
function renderConversations() {
  const container = document.getElementById('conv-list-items');
  container.innerHTML = state.conversations.map(c => `
    <div class="conv-item ${state.currentConv === c.id ? 'active' : ''}" onclick="openConv(${c.id})">
      <div class="avatar ${c.color}" style="width:36px;height:36px;font-size:13px;">${c.initials}</div>
      <div class="conv-item-info">
        <div class="conv-item-name">${c.name}</div>
        <div class="conv-item-preview">${c.preview}</div>
      </div>
      <div style="display:flex;flex-direction:column;align-items:flex-end;gap:4px;">
        <div class="conv-item-time">${c.time}</div>
        ${c.unread > 0 ? `<div class="unread-dot"></div>` : ''}
      </div>
    </div>
  `).join('');
}

function openConv(id) {
  state.currentConv = id;
  const conv = state.conversations.find(c => c.id === id);
  conv.unread = 0;
  renderConversations();
  const area = document.getElementById('chat-area');
  area.style.display = 'flex';
  area.style.flexDirection = 'column';
  area.style.overflow = 'hidden';
  area.innerHTML = `
    <div class="chat-header" style="flex-shrink:0;">
      <div class="avatar ${conv.color}" style="width:38px;height:38px;font-size:13px;">${conv.initials}</div>
      <div class="chat-header-info">
        <div class="chat-header-name">${conv.name}</div>
        <div class="chat-header-sub"><span class="chat-online-dot"></span>En ligne · Match accepté</div>
      </div>
    </div>
    <div class="chat-messages" id="chat-msgs" style="flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:12px;">
      ${conv.messages.map(m => `
        <div class="msg ${m.sent ? 'sent' : 'received'}">
          ${!m.sent ? `<div class="avatar ${conv.color}" style="width:28px;height:28px;font-size:10px;flex-shrink:0;">${conv.initials}</div>` : ''}
          <div>
            <div class="msg-time" style="text-align:${m.sent ? 'right' : 'left'}">${m.time}</div>
            <div class="msg-bubble">${m.text}</div>
          </div>
        </div>
      `).join('')}
    </div>
    <div class="chat-input-area" style="flex-shrink:0;">
      <textarea id="chat-input" placeholder="Écris ton message…" rows="1" onkeydown="handleEnter(event,${id})"></textarea>
      <button class="chat-send-btn" onclick="sendMsg(${id})">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
      </button>
    </div>
  `;
  const totalUnread = state.conversations.reduce((sum, c) => sum + c.unread, 0);
  const msgBadge = document.querySelectorAll('.sidebar-item .badge-count')[1];
  if (msgBadge) msgBadge.textContent = totalUnread || 0;
  scrollToBottom();
}

function sendMsg(convId) {
  const input = document.getElementById('chat-input');
  const text = input.value.trim();
  if (!text) return;
  const conv = state.conversations.find(c => c.id === convId);
  const now = new Date();
  const time = `${now.getHours()}:${String(now.getMinutes()).padStart(2, '0')}`;
  conv.messages.push({ sent: true, text, time });
  conv.preview = text;
  conv.time = time;
  input.value = '';
  const msgs = document.getElementById('chat-msgs');
  const div = document.createElement('div');
  div.className = 'msg sent';
  div.innerHTML = `<div><div class="msg-time" style="text-align:right">${time}</div><div class="msg-bubble">${text}</div></div>`;
  msgs.appendChild(div);
  scrollToBottom();
  setTimeout(() => simulateReply(convId, conv), 1200);
}

function simulateReply(convId, conv) {
  const replies = [
    'Super ! Ça marche pour moi 👍',
    "D'accord, on se retrouve à cet horaire !",
    "Parfait, j'ai noté ça dans mon agenda.",
    'Merci beaucoup ! À bientôt 😊',
    'Je prépare les exercices de mon côté.',
  ];
  const text = replies[Math.floor(Math.random() * replies.length)];
  const now = new Date();
  const time = `${now.getHours()}:${String(now.getMinutes()).padStart(2, '0')}`;
  conv.messages.push({ sent: false, text, time });
  conv.preview = text;
  const msgs = document.getElementById('chat-msgs');
  if (msgs) {
    const div = document.createElement('div');
    div.className = 'msg received';
    div.innerHTML = `
      <div class="avatar ${conv.color}" style="width:28px;height:28px;font-size:10px;flex-shrink:0;">${conv.initials}</div>
      <div><div class="msg-time">${time}</div><div class="msg-bubble">${text}</div></div>`;
    msgs.appendChild(div);
    scrollToBottom();
  }
  renderConversations();
}

function handleEnter(e, convId) {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMsg(convId); }
}

function scrollToBottom() {
  const msgs = document.getElementById('chat-msgs');
  if (msgs) msgs.scrollTop = msgs.scrollHeight;
}

// ====================================================
// MÉTRIQUES
// ====================================================
function updateMetrics() {
  const mPending = document.getElementById('metric-pending');
  const mAccepted = document.getElementById('metric-accepted');
  const mPosts = document.getElementById('metric-posts');
  if (mPending) mPending.textContent = state.matches.filter(m => m.status === 'pending').length;
  if (mAccepted) mAccepted.textContent = state.matches.filter(m => m.status === 'accepted').length;
  if (mPosts) mPosts.textContent = state.posts.filter(p => p.active).length;
}

// ====================================================
// TÉMOIGNAGES
// ====================================================
const defaultTestimonials = [
  { name: 'Adorée · L3 GL', text: "Grâce à MentorLink, j'ai trouvé en 2 jours un mentor en Algorithmique. Mes notes ont vraiment progressé !", rating: 5, avatar: 'AD', color: 'av-pink', date: 'Il y a 3 jours' },
  { name: 'Jean De Dieu · L1 IM', text: 'Super plateforme ! Le matching automatique est vraiment bien fait. Mon mentor m\'explique avec patience.', rating: 5, avatar: 'JD', color: 'av-amber', date: 'Il y a 1 semaine' },
  { name: 'Dels Marcel · L2 GL', text: "J'aide maintenant des L1 en Python grâce à la plateforme. Ça me permet aussi de consolider mes propres connaissances.", rating: 4, avatar: 'DM', color: 'av-green', date: 'Il y a 2 semaines' },
];
let publishedTestimonials = [];

function updateTestimonialForm() {
  const notice = document.getElementById('testi-login-notice');
  const fields = document.getElementById('testi-form-fields');
  const avatarIcon = document.getElementById('testi-avatar-icon');
  if (!notice || !fields) return;

  if (currentUser) {
    notice.style.display = 'none';
    fields.style.display = 'block';
    const initials = currentUser.prenom[0].toUpperCase() + currentUser.nom[0].toUpperCase();
    if (avatarIcon) avatarIcon.textContent = initials;
  } else {
    notice.style.display = 'block';
    fields.style.display = 'none';
    if (avatarIcon) avatarIcon.textContent = '?';
  }
}

function setRating(val) {
  currentRating = val;
  document.querySelectorAll('#star-rating .star').forEach((s, i) => {
    s.style.color = i < val ? '#f59e0b' : '#d1d5db';
  });
}

function setDashRating(val) {
  dashRating = val;
  document.querySelectorAll('#dash-star-rating .dash-star').forEach((s, i) => {
    s.style.color = i < val ? '#f59e0b' : '#d1d5db';
  });
}

function publishTestimonial() {
  const alertBox = document.getElementById('testi-alert');

  if (!currentUser) {
    alertBox.className = 'alert alert-error';
    alertBox.textContent = '🔒 Connecte-toi pour publier un témoignage.';
    alertBox.classList.remove('hidden');
    setTimeout(() => alertBox.classList.add('hidden'), 3000);
    showView('view-login');
    return;
  }

  const text = document.getElementById('testi-text').value.trim();
  if (!text) {
    alertBox.className = 'alert alert-error';
    alertBox.textContent = '⚠️ Veuillez saisir un témoignage.';
    alertBox.classList.remove('hidden');
    setTimeout(() => alertBox.classList.add('hidden'), 3000);
    return;
  }

  const name = `${currentUser.prenom} · ${currentUser.level} ${currentUser.field}`;
  const initials = currentUser.prenom[0].toUpperCase() + currentUser.nom[0].toUpperCase();
  const colors = ['av-green', 'av-blue', 'av-pink', 'av-amber'];
  const color = colors[Math.floor(Math.random() * colors.length)];

  publishedTestimonials.unshift({ name, text, rating: currentRating || 5, avatar: initials, color, date: "À l'instant" });

  document.getElementById('testi-text').value = '';
  setRating(0);

  alertBox.className = 'alert alert-success';
  alertBox.textContent = '✅ Témoignage publié avec succès !';
  alertBox.classList.remove('hidden');
  setTimeout(() => alertBox.classList.add('hidden'), 3000);

  renderTestimonials();
}

function publishDashTestimonial() {
  if (!currentUser) return;
  
  const text = document.getElementById('dash-testi-text').value.trim();
  if (!text) {
    showToast("⚠️ Veuillez écrire un petit mot avant de publier.", "error");
    return;
  }

  const name = `${currentUser.prenom} · ${currentUser.level} ${currentUser.field}`;
  const initials = currentUser.prenom[0].toUpperCase() + currentUser.nom[0].toUpperCase();
  const colors = ['av-green', 'av-blue', 'av-pink', 'av-amber'];
  const color = colors[Math.floor(Math.random() * colors.length)];

  publishedTestimonials.unshift({ 
    name, 
    text, 
    rating: dashRating || 5, 
    avatar: initials, 
    color, 
    date: "À l'instant" 
  });

  document.getElementById('dash-testi-text').value = '';
  setDashRating(0);
  
  showToast("✅ Témoignage publié ! Merci pour ta contribution.", "success");
  renderTestimonials();
}

function renderTestimonials() {
  const all = [...publishedTestimonials, ...defaultTestimonials];
  const container = document.getElementById('testimonials-list');
  if (!container) return;
  container.innerHTML = all.map(t => `
    <div class="testimonial-card">
      <div class="testi-header">
        <div class="avatar ${t.color}" style="width:38px;height:38px;font-size:13px;flex-shrink:0;">${t.avatar}</div>
        <div>
          <div style="font-weight:600;font-size:14px;">${t.name}</div>
          <div style="font-size:11px;color:var(--text3);">${t.date}</div>
        </div>
        <div style="margin-left:auto;color:#f59e0b;font-size:16px;">${'★'.repeat(t.rating)}${'☆'.repeat(5 - t.rating)}</div>
      </div>
      <p class="testi-text">"${t.text}"</p>
    </div>
  `).join('');
}

// ====================================================
// RECHERCHE DE MATIÈRES
// ====================================================
const allSubjects = [
  { name: 'Algorithmique', icon: '🧠', mentors: 5, mentores: 8, category: 'CS Fondamental' },
  { name: 'Structures de données', icon: '🌲', mentors: 4, mentores: 6, category: 'CS Fondamental' },
  { name: 'Programmation Python', icon: '🐍', mentors: 12, mentores: 15, category: 'Programmation' },
  { name: 'Développement Web', icon: '🌐', mentors: 8, mentores: 10, category: 'Programmation' },
  { name: 'JavaScript', icon: '⚡', mentors: 7, mentores: 9, category: 'Programmation' },
  { name: 'Vue.js', icon: '💚', mentors: 3, mentores: 5, category: 'Programmation' },
  { name: 'Bases de données SQL', icon: '🗄️', mentors: 9, mentores: 11, category: 'Base de données' },
  { name: 'Algèbre relationnelle', icon: '📐', mentors: 2, mentores: 7, category: 'Base de données' },
  { name: 'Réseaux informatiques', icon: '📡', mentors: 4, mentores: 9, category: 'Réseaux' },
  { name: 'Linux', icon: '🐧', mentors: 6, mentores: 8, category: 'Systèmes' },
  { name: 'Mathématiques discrètes', icon: '∑', mentors: 3, mentores: 10, category: 'Mathématiques' },
  { name: 'Intelligence Artificielle', icon: '🤖', mentors: 5, mentores: 14, category: 'IA' },
  { name: 'FastAPI / Flask', icon: '🚀', mentors: 4, mentores: 6, category: 'Programmation' },
  { name: 'Analyse numérique', icon: '📊', mentors: 2, mentores: 8, category: 'Mathématiques' },
  { name: 'Probabilités & Stats', icon: '🎲', mentors: 3, mentores: 9, category: 'Mathématiques' },
];

function setSearchFilter(filter, el) {
  state.searchFilter = filter;
  document.querySelectorAll('#tab-search .filter-chip').forEach(c => c.classList.remove('active'));
  el.classList.add('active');
  renderSearchResults();
}

function renderSearchResults() {
  const query = (document.getElementById('search-input')?.value || '').toLowerCase().trim();
  const filter = state.searchFilter;
  const container = document.getElementById('search-results');
  if (!container) return;

  let results = allSubjects.filter(s => {
    const matchQuery = !query || s.name.toLowerCase().includes(query) || s.category.toLowerCase().includes(query);
    return matchQuery;
  });

  if (filter === 'mentor') {
    results = results.sort((a, b) => b.mentores - a.mentores);
  } else if (filter === 'mentoré') {
    results = results.sort((a, b) => b.mentors - a.mentors);
  }

  if (results.length === 0) {
    container.innerHTML = `<div class="empty-state"><div class="empty-state-icon">🔍</div><h4>Aucune matière trouvée</h4><p>Essaie un autre terme de recherche.</p></div>`;
    return;
  }

  container.innerHTML = results.map(s => {
    const roleInfo = filter === 'mentor'
      ? `<span class="search-role-badge role-mentor">🎓 ${s.mentores} étudiant${s.mentores > 1 ? 's' : ''} cherche${s.mentores > 1 ? 'nt' : ''} un mentor</span>`
      : filter === 'mentoré'
        ? `<span class="search-role-badge role-mentore">📚 ${s.mentors} mentor${s.mentors > 1 ? 's' : ''} disponible${s.mentors > 1 ? 's' : ''}</span>`
        : `<span class="search-role-badge role-mentor">🎓 ${s.mentors} mentor${s.mentors > 1 ? 's' : ''}</span>
           <span class="search-role-badge role-mentore">📚 ${s.mentores} mentoré${s.mentores > 1 ? 's' : ''}</span>`;
    return `
      <div class="subject-card">
        <div class="subject-icon">${s.icon}</div>
        <div class="subject-info">
          <div class="subject-name">${s.name}</div>
          <div class="subject-category">${s.category}</div>
          <div class="subject-roles">${roleInfo}</div>
        </div>
        <div class="subject-actions">
          <button class="btn btn-primary btn-sm" onclick="createPostFromSearch('offer','${s.name}')">🎓 Proposer</button>
          <button class="btn btn-outline btn-sm" onclick="createPostFromSearch('request','${s.name}')">📚 Demander</button>
        </div>
      </div>
    `;
  }).join('');
}

function createPostFromSearch(type, skill) {
  switchTab('posts');
  setTimeout(() => {
    openPostForm();
    const typeEl = document.getElementById('post-type');
    const skillEl = document.getElementById('post-skill');
    if (typeEl) typeEl.value = type;
    if (skillEl) {
      const opts = skillEl.options;
      for (let i = 0; i < opts.length; i++) {
        if (opts[i].text.toLowerCase().includes(skill.toLowerCase().split(' ')[0])) {
          skillEl.selectedIndex = i;
          break;
        }
      }
    }
  }, 100);
}

// ====================================================
// UTILITAIRES
// ====================================================
function showAlert(id, type, msg) {
  const el = document.getElementById(id);
  el.className = `alert alert-${type}`;
  el.textContent = msg;
  el.classList.remove('hidden');
  setTimeout(() => el.classList.add('hidden'), 4000);
}

function showToast(msg, type = 'success') {
  let toast = document.getElementById('global-toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'global-toast';
    toast.style.cssText = 'position:fixed;bottom:24px;right:24px;z-index:9999;padding:12px 20px;border-radius:12px;font-size:14px;font-weight:500;box-shadow:0 8px 30px rgba(0,0,0,0.15);transition:all 0.4s ease;opacity:0;transform:translateY(20px);max-width:340px;';
    document.body.appendChild(toast);
  }
  toast.textContent = msg;
  toast.style.background = type === 'success' ? '#16a34a' : '#dc2626';
  toast.style.color = 'white';
  setTimeout(() => { toast.style.opacity = '1'; toast.style.transform = 'translateY(0)'; }, 10);
  setTimeout(() => { toast.style.opacity = '0'; toast.style.transform = 'translateY(20px)'; }, 3500);
}

// ====================================================
// INITIALISATION
// ====================================================
document.addEventListener('DOMContentLoaded', function () {
  if (localStorage.getItem('darkMode') === 'true') {
    document.body.classList.add('dark-mode');
  }
  updateDarkIcons();

  document.querySelectorAll('#star-rating .star').forEach(s => {
    s.style.color = '#d1d5db';
    s.style.cursor = 'pointer';
    s.style.fontSize = '22px';
    s.style.transition = 'color 0.15s';
    s.onmouseover = () => {
      document.querySelectorAll('#star-rating .star').forEach((ss, ii) => {
        ss.style.color = ii <= parseInt(s.dataset.val) - 1 ? '#fbbf24' : '#d1d5db';
      });
    };
    s.onmouseleave = () => {
      document.querySelectorAll('#star-rating .star').forEach((ss, ii) => {
        ss.style.color = ii < currentRating ? '#f59e0b' : '#d1d5db';
      });
    };
  });

  document.querySelectorAll('#dash-star-rating .dash-star').forEach(s => {
    s.style.transition = 'color 0.15s';
    s.onmouseover = () => {
      document.querySelectorAll('#dash-star-rating .dash-star').forEach((ss, ii) => {
        ss.style.color = ii <= parseInt(s.dataset.val) - 1 ? '#fbbf24' : '#d1d5db';
      });
    };
    s.onmouseleave = () => {
      document.querySelectorAll('#dash-star-rating .dash-star').forEach((ss, ii) => {
        ss.style.color = ii < dashRating ? '#f59e0b' : '#d1d5db';
      });
    };
  });

  renderTestimonials();
  updateTestimonialForm();
});