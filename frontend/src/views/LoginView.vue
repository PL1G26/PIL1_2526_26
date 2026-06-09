<template>
  <div id="view-login">
    <div class="auth-wrapper">
      <div class="auth-left">
        <div class="auth-left-brand">
          <span class="logo-dot"></span> IFRI MentorLink
        </div>
        <div class="auth-left-content">
          <h2>Bienvenue de retour.</h2>
          <p>Connecte-toi pour accéder à tes sessions de mentorat, tes correspondances et ta messagerie.</p>
          <div class="auth-left-features">
            <div class="auth-feature">
              <div class="auth-feature-icon"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg></div>
              <div>Matching automatique selon tes compétences et disponibilités</div>
            </div>
            <div class="auth-feature">
              <div class="auth-feature-icon"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 21 1.9-5.7a8.5 8.5 0 1 1 3.8 3.8z"/></svg></div>
              <div>Chat en temps réel avec tes mentors et mentorés</div>
            </div>
            <div class="auth-feature">
              <div class="auth-feature-icon"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg></div>
              <div>Suivi de ta progression académique</div>
            </div>
          </div>
        </div>
        <div style="color:rgba(255,255,255,0.4);font-size:12px;">© 2025-2026 IFRI / UAC</div>
      </div>
      <div class="auth-right">
        <form class="auth-form-box" @submit.prevent="handleLogin">
          <h3>Se connecter</h3>
          <p class="auth-subtitle">Pas encore de compte ? <a href="#" @click.prevent="$router.push('/register')">S'inscrire gratuitement</a></p>
          
          <div class="alert alert-error" v-if="errorMessage">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 4px;"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg> {{ errorMessage }}
          </div>

          <div class="form-group">
            <label>Email</label>
            <input v-model="email" placeholder="prenom.nom@ifri-uac.bj" type="email" required />
          </div>
          <div class="form-group">
            <label>Mot de passe</label>
            <input v-model="password" placeholder="••••••••" type="password" required />
          </div>
          <div style="text-align:right;margin-bottom:1.5rem;">
            <a href="#" style="font-size:13px;color:var(--brand);text-decoration:none;">Mot de passe oublié ?</a>
          </div>
          <button type="submit" class="btn btn-primary" style="width:100%;justify-content:center;padding:12px;" :disabled="loading">
            {{ loading ? 'Connexion...' : 'Se connecter →' }}
          </button>

          <div style="text-align:center;margin-top:1.5rem;">
            <button type="button" class="btn btn-ghost btn-sm" @click="$router.push('/')">← Retour à l'accueil</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { store } from '../store'

const router = useRouter()
const email = ref('')
const password = ref('')
const errorMessage = ref('')
const loading = ref(false)

const handleLogin = async () => {
  errorMessage.value = ''
  loading.value = true
  const res = await store.login(email.value, password.value)
  loading.value = false
  if (res.success) {
    router.push('/dashboard')
  } else {
    errorMessage.value = res.message
  }
}
</script>