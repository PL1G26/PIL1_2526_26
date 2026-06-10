<template>
  <div id="view-register">
    <div class="auth-wrapper">
      <div class="auth-left">
        <div class="auth-left-brand">
          <span class="logo-dot"></span> IFRI MentorLink
        </div>
        <div class="auth-left-content">
          <h2>Commence ton parcours de mentorat.</h2>
          <p>Rejoins des centaines d'étudiants de l'IFRI qui s'entraident pour réussir leurs examens et approfondir leurs connaissances.</p>
          <div class="auth-left-features" style="margin-top:2rem;">
            <div class="auth-feature">
              <div class="auth-feature-icon"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg></div>
              <div>Inscription 100% gratuite pour tous les étudiants IFRI</div>
            </div>
            <div class="auth-feature">
              <div class="auth-feature-icon"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 1 1-9-9c2.52 0 4.93 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/></svg></div>
              <div>Soit mentor ET mentoré sur la même plateforme</div>
            </div>
            <div class="auth-feature">
              <div class="auth-feature-icon"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg></div>
              <div>Matching instantané dès ton profil complété</div>
            </div>
          </div>
        </div>
        <div style="color:rgba(255,255,255,0.4);font-size:12px;">© 2025-2026 IFRI / UAC</div>
      </div>
      <div class="auth-right" style="align-items:flex-start;padding-top:2rem;">
        <form class="auth-form-box" style="max-width:480px;" @submit.prevent="handleRegister">
          <h3>Créer un compte</h3>
          <p class="auth-subtitle">Déjà inscrit·e ? <a href="#" @click.prevent="$router.push('/login')">Se connecter</a></p>
          
          <div class="alert alert-success" v-if="successMessage">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 4px;"><path d="M20 6 9 17l-5-5"/></svg> {{ successMessage }}
          </div>
          <div class="alert alert-error" v-if="errorMessage">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 4px;"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg> {{ errorMessage }}
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Prénom *</label>
              <input v-model="formData.first_name" placeholder="Mona" type="text" required />
            </div>
            <div class="form-group">
              <label>Nom *</label>
              <input v-model="formData.last_name" placeholder="AGO" type="text" required />
            </div>
          </div>
          <div class="form-group">
            <label>Adresse email *</label>
            <input v-model="formData.email" placeholder="prenom.nom@ifri-uac.bj" type="email" required />
          </div>
          <div class="form-group">
            <label>Numéro de téléphone *</label>
            <input v-model="formData.phone_number" placeholder="+229 XXXXXXXX" type="tel" required />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Filière *</label>
              <select v-model="formData.field_of_study" required>
                <option value="">Choisir…</option>
                <option value="IA">IA</option>
                <option value="IM">IM</option>
                <option value="GL">GL</option>
                <option value="SE&IoT">SE&IoT</option>
                <option value="SI">SI</option>
              </select>
            </div>
            <div class="form-group">
              <label>Niveau *</label>
              <select v-model="formData.level" required>
                <option value="">Choisir…</option>
                <option value="L1">L1</option>
                <option value="L2">L2</option>
                <option value="L3">L3</option>
                <option value="M1">M1</option>
                <option value="M2">M2</option>
              </select>
            </div>
          </div>
          <div class="form-group">
            <label>Mot de passe *</label>
            <input v-model="formData.password" placeholder="Minimum 6 caractères" type="password" required minlength="6" />
          </div>
          <div class="form-group">
            <label>Confirmer le mot de passe *</label>
            <input v-model="passwordConfirm" placeholder="Répète le mot de passe" type="password" required />
          </div>
          <div class="form-group">
            <label>Bio (optionnel)</label>
            <textarea v-model="formData.bio" placeholder="Décris tes centres d'intérêt académiques…" style="min-height:60px;"></textarea>
          </div>
          <button type="submit" class="btn btn-primary" style="width:100%;justify-content:center;padding:12px;" :disabled="loading">
            {{ loading ? 'Création en cours...' : 'Créer mon compte →' }}
          </button>
          <div style="text-align:center;margin-top:1rem;">
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

const formData = ref({
  first_name: '',
  last_name: '',
  email: '',
  phone_number: '',
  password: '',
  field_of_study: '',
  level: '',
  bio: ''
})

const passwordConfirm = ref('')
const errorMessage = ref('')
const successMessage = ref('')
const loading = ref(false)

const handleRegister = async () => {
  errorMessage.value = ''
  
  const nameRegex = /^[A-ZÀ-Ÿ][A-Za-zÀ-ÿ\s\-']+$/
  if (!nameRegex.test(formData.value.first_name) || !nameRegex.test(formData.value.last_name)) {
    errorMessage.value = "Le prénom et le nom doivent commencer par une lettre majuscule, contenir au moins deux lettres, et ne pas avoir de caractères spéciaux."
    return
  }

  const phoneRegex = /^\+22901\d{8}$/
  if (!phoneRegex.test(formData.value.phone_number.replace(/\s+/g, ''))) {
    errorMessage.value = "Le numéro de téléphone doit être au format +22901XXXXXXXX."
    return
  }

  if (formData.value.password !== passwordConfirm.value) {
    errorMessage.value = "Les mots de passe ne correspondent pas."
    return
  }

  loading.value = true
  const res = await store.register(formData.value)
  loading.value = false
  
  if (res.success) {
    successMessage.value = "Compte créé avec succès ! Redirection..."
    setTimeout(() => {
      router.push('/dashboard')
    }, 1500)
  } else {
    errorMessage.value = res.message
  }
}
</script>