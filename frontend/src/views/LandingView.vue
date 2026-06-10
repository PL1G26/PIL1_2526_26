<template>
<div id="view-landing">
<!-- Barre de navigation -->
<nav class="navbar">
<div class="navbar-brand" @click="$router.push('/')">
<span class="logo-dot"></span> IFRI MentorLink
    </div>
<button class="navbar-hamburger" @click="mobileMenuOpen = !mobileMenuOpen" aria-label="Menu" aria-expanded="mobileMenuOpen">
  <span></span><span></span><span></span>
</button>
<div class="navbar-links" :class="{ open: mobileMenuOpen }">
<button class="btn btn-ghost" @click="scrollToSection('features'); mobileMenuOpen=false">Fonctionnalités</button>
<button class="btn btn-ghost" @click="scrollToSection('about'); mobileMenuOpen=false">À propos</button>
<button class="btn btn-ghost" @click="scrollToSection('contact'); mobileMenuOpen=false">Contact</button>
<button aria-label="Basculer mode sombre/clair" class="theme-toggle" id="theme-btn" @click="store.toggleTheme()" title="Changer le thème">
<span id="theme-icon" style="display:flex;"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg></span>
</button>
<button class="btn btn-outline" @click="$router.push('/login')">Connexion</button>
<button class="btn btn-primary" @click="$router.push('/register')">S'inscrire</button>
</div>
</nav>
<!-- Section héros —— accroche principale -->
<section class="landing-hero">
<div>
<div class="hero-tag">
<span class="logo-dot" style="width:7px;height:7px"></span>
        Plateforme de mentorat IFRI · UAC
      </div>
<h1 class="hero-title">
        Apprends mieux,<br/>
<span class="accent">ensemble.</span>
</h1>
<p class="hero-desc">
        IFRI MentorLink connecte intelligemment les étudiants : ceux qui maîtrisent une matière avec ceux qui en ont besoin. Un matching automatique, un chat en temps réel, et une progression académique boostée.
      </p>
<div class="hero-cta">
<button class="btn btn-primary btn-lg" @click="$router.push('/register')">Rejoindre la plateforme →</button>
<button class="btn btn-outline btn-lg" @click="$router.push('/login')">Se connecter</button>
</div>
<div class="hero-stats">
<div class="stat-item">
<div class="stat-num">5</div>
<div class="stat-label">Filières connectées</div>
</div>
<div class="stat-item">
<div class="stat-num">15+</div>
<div class="stat-label">Matières disponibles</div>
</div>
<div class="stat-item">
<div class="stat-num">100</div>
<div class="stat-label">Score max de compatibilité</div>
</div>
</div>
</div>
<div class="hero-visual">
<div class="hero-card-stack">
<div class="demo-card">
<div class="demo-card-header">
<div class="avatar av-green">AM</div>
<div>
<div class="demo-name">Mona</div>
<div class="demo-role">L2 · IA — Mentor Python</div>
</div>
<div class="score-badge">92 pts</div>
</div>
<div class="tag-row">
<span class="tag tag-green" style="display:flex;align-items:center;gap:4px;"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/></svg> Python</span>
<span class="tag tag-green">SQL</span>
<span class="tag tag-blue">Mercredi 15h–17h</span>
<span class="tag tag-amber">En ligne</span>
</div>
</div>
<div class="demo-card" style="padding:0;overflow:hidden;">
<div style="padding:12px 16px;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:8px;background:var(--bg);">
<div class="avatar av-pink" style="width:30px;height:30px;font-size:11px;">AD</div>
<div style="font-weight:600;font-size:13px;">Adorée</div>
<span style="margin-left:auto;font-size:11px;color:var(--brand);">● En ligne</span>
</div>
<div style="padding:12px 16px;display:flex;flex-direction:column;gap:8px;">
<div style="background:var(--bg);border:1px solid var(--border);border-radius:12px 12px 12px 3px;padding:8px 12px;font-size:13px;max-width:80%;">
              Salut ! Tu es disponible samedi pour Python ?
            </div>
<div style="background:var(--brand);color:white;border-radius:12px 12px 3px 12px;padding:8px 12px;font-size:13px;max-width:80%;align-self:flex-end;">
              Oui, 14h ça te va ? <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;"><circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><line x1="9" x2="9.01" y1="9" y2="9"/><line x1="15" x2="15.01" y1="9" y2="9"/></svg>
            </div>
</div>
</div>
<div class="demo-card">
<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
<span class="tag tag-pink" style="font-size:12px;">Demande</span>
<span style="font-weight:700;font-size:14px;">Besoin d'aide en Algorithmique</span>
</div>
<div class="tag-row">
<span class="tag tag-blue">Samedi matin</span>
<span class="tag tag-amber">Présentiel ou en ligne</span>
</div>
</div>
</div>
</div>
</section>
<!-- Section fonctionnalités -->
<section class="features-section" id="features">
<div class="section-label">Modules</div>
<div class="grid-2" style="align-items:start">
<div>
<h2 class="section-title">Tout ce dont tu as besoin pour progresser</h2>
<p class="section-desc">Une plateforme pensée pour les étudiants de l'IFRI, avec tous les outils pour organiser, trouver et gérer ses sessions de mentorat.</p>
</div>
<div class="features-grid">
<div class="feature-card">
<div class="feature-icon"><svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg></div>
<div class="feature-title">Profil riche</div>
<div class="feature-desc">Déclare tes compétences maîtrisées et tes lacunes, indique ta filière et tes disponibilités.</div>
</div>
<div class="feature-card">
<div class="feature-icon"><svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg></div>
<div class="feature-title">Matching intelligent</div>
<div class="feature-desc">Un algorithme calcule un score de compatibilité sur 100 pour chaque paire mentor-mentoré.</div>
</div>
<div class="feature-card">
<div class="feature-icon"><svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 21 1.9-5.7a8.5 8.5 0 1 1 3.8 3.8z"/></svg></div>
<div class="feature-title">Chat temps réel</div>
<div class="feature-desc">Messagerie instantanée entre mentors et mentorés, avec historique et notifications.</div>
</div>
<div class="feature-card">
<div class="feature-icon"><svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg></div>
<div class="feature-title">Offres &amp; demandes</div>
<div class="feature-desc">Publie tes offres ou demandes de mentorat par matière, format et créneaux horaires.</div>
</div>
<div class="feature-card">
<div class="feature-icon"><svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/></svg></div>
<div class="feature-title">Bi-rôle</div>
<div class="feature-desc">Sois mentor en Python et mentoré en Algèbre simultanément — chaque étudiant a les deux rôles.</div>
</div>
<div class="feature-card">
<div class="feature-icon"><svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg></div>
<div class="feature-title">Sécurisé</div>
<div class="feature-desc">Authentification JWT, mots de passe hachés bcrypt, messagerie réservée aux matches acceptés.</div>
</div>
</div>
</div>
</section>
<!-- Section témoignages — formulaire + grille -->
<section class="testimonials-section" id="testimonials">
<div class="section-label">Témoignages</div>
<h2 class="section-title" style="text-align:center;margin-bottom:0.5rem;">Ce que disent nos étudiants</h2>
<p style="text-align:center;color:var(--text2);margin-bottom:2.5rem;font-size:15px;">Partage ton expérience avec la communauté IFRI MentorLink</p>
<!-- Invitation à se connecter pour publier un témoignage -->
<div class="testi-login-prompt">
<div class="testi-prompt-icon"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg></div>
<div>
<div style="font-weight:700;font-size:15px;margin-bottom:4px;">Partage ton expérience</div>
<div style="font-size:13px;color:var(--text2);">Connecte-toi ou crée un compte pour publier ton témoignage.</div>
</div>
<div style="display:flex;gap:8px;margin-left:auto;flex-shrink:0;">
<button class="btn btn-outline btn-sm" @click="$router.push('/login')">Se connecter</button>
<button class="btn btn-primary btn-sm" @click="$router.push('/register')">S'inscrire →</button>
</div>
</div>
<div class="testimonials-grid" id="testimonials-list">
</div>
</section>
<!-- Section À propos -->
<section class="about-section" id="about">
<div class="section-label">À propos</div>
<div class="about-grid">
<div class="about-text">
<h2 class="section-title">Née à l'IFRI, pour les étudiants de l'IFRI</h2>
<p style="color:var(--text2);font-size:15px;line-height:1.8;margin-bottom:1.25rem;">
          IFRI MentorLink est une plateforme de mentorat académique développée dans le cadre du projet intégrateur PIL1 2025-2026 à l'Institut de Formation et de Recherche en Informatique (IFRI) de l'Université d'Abomey-Calavi.
        </p>
<p style="color:var(--text2);font-size:15px;line-height:1.8;margin-bottom:1.25rem;">
          Notre mission : créer des ponts entre les étudiants qui maîtrisent une matière et ceux qui ont besoin d'aide, dans un environnement bienveillant et structuré.
        </p>
<div class="about-values">
<div class="about-value-item">
<div class="about-value-icon"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg></div>
<div><strong>Entraide</strong> — Chaque étudiant peut être mentor ET mentoré selon les matières.</div>
</div>
<div class="about-value-item">
<div class="about-value-icon"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 14V2"/><path d="M9 18.12 10 14H4.17a2 2 0 0 1-1.92-2.56l2.33-8A2 2 0 0 1 6.5 2H20a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-2.76a2 2 0 0 0-1.79 1.11L12 22h0a3.13 3.13 0 0 1-3-3.88Z"/></svg></div>
<div><strong>Communauté</strong> — Bâtir un réseau solide au sein de l'IFRI-UAC.</div>
</div>
<div class="about-value-item">
<div class="about-value-icon"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg></div>
<div><strong>Progression</strong> — Des sessions ciblées sur les vrais besoins académiques.</div>
</div>
</div>
</div>
<div class="about-stats-box">
<div class="about-stat">
<div class="about-stat-num">5</div>
<div class="about-stat-label">Filières couvertes</div>
<div class="about-stat-sub">IA · GL · IM · SE&amp;IoT · SI</div>
</div>
<div class="about-stat">
<div class="about-stat-num">15+</div>
<div class="about-stat-label">Matières disponibles</div>
<div class="about-stat-sub">Python, SQL, Algo, Réseaux…</div>
</div>
<div class="about-stat">
<div class="about-stat-num">100</div>
<div class="about-stat-label">Score de compatibilité max</div>
<div class="about-stat-sub">Algorithme de matching automatique</div>
</div>
<div class="about-stat">
<div class="about-stat-num">L1–M2</div>
<div class="about-stat-label">Tous niveaux</div>
<div class="about-stat-sub">Du premier cycle au master</div>
</div>
</div>
</div>
</section>
<!-- Section Contact -->
<section class="contact-section" id="contact">
<div class="section-label">Contact</div>
<h2 class="section-title" style="text-align:center;margin-bottom:0.5rem;">Nous contacter</h2>
<p style="text-align:center;color:var(--text2);margin-bottom:2.5rem;font-size:15px;">Une question, une suggestion ou un bug ? Écris-nous directement.</p>
<div class="contact-grid">
<div class="contact-info-col">
<div class="contact-info-card">
<div class="contact-info-icon"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg></div>
<div>
<div class="contact-info-title">Adresse</div>
<div class="contact-info-value">IFRI / Université d'Abomey-Calavi<br/>Cotonou, Bénin</div>
</div>
</div>
<div class="contact-info-card">
<div class="contact-info-icon"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg></div>
<div>
<div class="contact-info-title">Email</div>
<div class="contact-info-value">mentorlink@ifri-uac.bj</div>
</div>
</div>
<div class="contact-info-card">
<div class="contact-info-icon"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg></div>
<div>
<div class="contact-info-title">Disponibilité</div>
<div class="contact-info-value">Lundi – Vendredi<br/>08h00 – 17h00</div>
</div>
</div>
</div>
<div class="contact-form-col">
<div class="contact-form-box">
<div class="form-row">
<div class="form-group">
<label>Prénom</label>
<input id="contact-prenom" v-model="contactForm.prenom" placeholder="Ton prénom" type="text"/>
</div>
<div class="form-group">
<label>Nom</label>
<input id="contact-nom" v-model="contactForm.nom" placeholder="Ton nom" type="text"/>
</div>
</div>
<div class="form-group">
<label>Email</label>
<input id="contact-email" v-model="contactForm.email" placeholder="ton@email.bj" type="email"/>
</div>
<div class="form-group">
<label>Sujet</label>
<select id="contact-sujet" v-model="contactForm.sujet">
<option value="">Choisir un sujet…</option>
<option>Question générale</option>
<option>Problème technique</option>
<option>Suggestion d'amélioration</option>
<option>Signaler un bug</option>
<option>Partenariat</option>
</select>
</div>
<div class="form-group">
<label>Message</label>
<textarea id="contact-message" v-model="contactForm.message" placeholder="Décris ta question ou ton problème…" style="min-height:120px;resize:vertical;"></textarea>
</div>
<div class="alert alert-success" v-if="contactSuccess">Message envoyé avec succès !</div>
<button class="btn btn-primary" @click="sendContactMessage" style="width:100%;justify-content:center;padding:12px;">
            Envoyer le message →
          </button>
</div>
</div>
</div>
</section>
<!-- Section CTA (appel à l'action) -->
<section class="cta-section">
<div class="section-label">Prêt·e ?</div>
<h2 class="section-title">Rejoins IFRI MentorLink aujourd'hui</h2>
<p>Inscription gratuite. Commence à apprendre ou à enseigner dès maintenant.</p>
<button class="btn btn-white btn-lg" @click="$router.push('/register')">Créer mon compte →</button>
</section>
<!-- Pied de page -->
<footer>
<div>
<strong>IFRI MentorLink</strong> — Projet intégrateur PIL1 2025-2026
    </div>
<div>IFRI / Université d'Abomey-Calavi · Cotonou</div>
</footer>
</div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { store } from '../store'

const mobileMenuOpen = ref(false)

const router = useRouter()

const scrollToSection = (id) => {
  const el = document.getElementById(id)
  if (el) {
    el.scrollIntoView({ behavior: 'smooth' })
  }
}

const contactForm = ref({
  prenom: '',
  nom: '',
  email: '',
  sujet: '',
  message: ''
})
const contactSuccess = ref(false)

const sendContactMessage = () => {
  if (!contactForm.value.prenom || !contactForm.value.email || !contactForm.value.message) {
    alert("Veuillez remplir les champs obligatoires (Prénom, Email, Message).")
    return
  }
  contactSuccess.value = true
  setTimeout(() => {
    contactSuccess.value = false
    contactForm.value = {
      prenom: '',
      nom: '',
      email: '',
      sujet: '',
      message: ''
    }
  }, 3000)
}
</script>