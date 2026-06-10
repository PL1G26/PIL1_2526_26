import { reactive, watch } from 'vue'
import api from '../services/api'
import notificationService from '../services/notificationService'

const loadCache = (key, defaultVal) => {
  try {
    const cached = localStorage.getItem(key)
    return cached ? JSON.parse(cached) : defaultVal
  } catch(e) {
    return defaultVal
  }
}

export const store = reactive({
  user: loadCache('user_cache', null),
  posts: loadCache('posts_cache', []),
  matches: loadCache('matches_cache', []),
  conversations: loadCache('conversations_cache', []),
  activeConversationId: null,
  postFilter: 'all',
  matchFilter: 'all',
  theme: localStorage.getItem('theme') || 'light',
  token: localStorage.getItem('token') || null,
  skills: loadCache('skills_cache', []), // List of available skills from DB
  
  // Tab management
  activeTab: 'home',

  async initAuth() {
    if (this.token) {
      try {
        const [userResponse] = await Promise.all([
          api.get('/users/me'),
          this.fetchDashboardData()
        ])
        this.user = userResponse.data
        // Démarrer le service de notifications en temps réel
        notificationService.start(this)
      } catch (error) {
        console.error("Auth init error:", error)
        this.logout()
      }
    }
  },

  async login(email, password) {
    try {
      const response = await api.post('/auth/login', { email, password })
      if (response.data && response.data.access_token) {
        this.token = response.data.access_token
        localStorage.setItem('token', this.token)
        // Fetch user profile and dashboard data concurrently
        const [userRes] = await Promise.all([
          api.get('/users/me'),
          this.fetchDashboardData()
        ])
        this.user = userRes.data
        // Démarrer le service de notifications en temps réel
        notificationService.start(this)
        return { success: true }
      }
      return { success: false, message: 'Invalid response from server' }
    } catch (error) {
      return { success: false, message: error.response?.data?.detail || 'Identifiants incorrects' }
    }
  },

  async register(userData) {
    try {
      await api.post('/auth/register', userData)
      // Automatically login after successful registration
      return await this.login(userData.email, userData.password)
    } catch (error) {
      return { success: false, message: Array.isArray(error.response?.data?.detail) ? JSON.stringify(error.response.data.detail) : error.response?.data?.detail || 'Erreur lors de l\'inscription' }
    }
  },

  logout() {
    // Arrêter le service SSE avant de vider l'état
    notificationService.stop()
    this.user = null
    this.token = null
    this.posts = []
    this.matches = []
    this.conversations = []
    localStorage.removeItem('token')
    localStorage.removeItem('user_cache')
    localStorage.removeItem('posts_cache')
    localStorage.removeItem('matches_cache')
    localStorage.removeItem('conversations_cache')
  },

  async fetchDashboardData() {
    try {
      const [postsRes, matchesRes, convsRes, skillsRes] = await Promise.all([
        api.get('/posts/'),
        api.get('/matches/'),
        api.get('/conversations'),
        api.get('/skills/')
      ])
      this.posts = postsRes.data
      this.matches = matchesRes.data.matches || []
      this.conversations = convsRes.data.conversations || []
      this.skills = skillsRes.data
    } catch (error) {
      console.error("Error fetching dashboard data:", error)
    }
  },
  
  async createPost(postData) {
    const skill = this.skills.find(s => s.id === postData.skill_id)
    const tempPost = {
      id: 'temp-' + Date.now(),
      user_id: this.user?.id,
      ...postData,
      skill: skill,
      created_at: new Date().toISOString()
    }
    this.posts.unshift(tempPost) // Optimistic update
    try {
      await api.post('/posts/', postData)
      this.fetchDashboardData() // refresh lists in background
      return { success: true }
    } catch (error) {
      this.posts = this.posts.filter(p => p.id !== tempPost.id) // Revert
      let msg = error.response?.data?.detail || 'Erreur création post'
      if (Array.isArray(msg)) msg = msg.map(e => `${e.loc?.join('.')} : ${e.msg}`).join(' | ')
      return { success: false, message: msg }
    }
  },

  async deletePost(postId) {
    const postIndex = this.posts.findIndex(p => p.id === postId)
    const backupPost = this.posts[postIndex]
    if (postIndex !== -1) this.posts.splice(postIndex, 1) // Optimistic delete
    try {
      await api.delete(`/posts/${postId}`)
      this.fetchDashboardData()
      return { success: true }
    } catch (error) {
      if (backupPost) this.posts.splice(postIndex, 0, backupPost) // Revert
      console.error("Error deleting post:", error)
      return { success: false }
    }
  },
  
  async acceptMatch(matchId) {
    try {
      await api.put(`/matches/${matchId}/accept`)
      const match = this.matches.find(m => m.id === matchId)
      if (match) match.status = 'accepted'
      this.fetchDashboardData()
      return { success: true }
    } catch (error) {
      return { success: false }
    }
  },

  async rejectMatch(matchId) {
    try {
      await api.put(`/matches/${matchId}/reject`)
      const match = this.matches.find(m => m.id === matchId)
      if (match) match.status = 'rejected'
      this.fetchDashboardData()
      return { success: true }
    } catch (error) {
      return { success: false }
    }
  },
  
  async selectConversation(convId) {
    this.activeConversationId = convId
    try {
      const res = await api.get(`/conversations/${convId}/messages`)
      const convIndex = this.conversations.findIndex(c => c.id === convId)
      if (convIndex !== -1) {
        this.conversations[convIndex].messages = res.data.messages
        // Marquer comme lu automatiquement
        notificationService.markConversationRead(convId)
        this.conversations[convIndex].unread_count = 0
      }
    } catch(e) {
      console.error("Error fetching messages", e)
    }
  },

  async sendMessage(conversationId, content) {
    const convIndex = this.conversations.findIndex(c => c.id === conversationId)
    const tempMsg = {
      id: 'temp-' + Date.now(),
      conversation_id: conversationId,
      sender_id: this.user?.id,
      content: content,
      created_at: new Date().toISOString()
    }
    if (convIndex !== -1) {
      if (!this.conversations[convIndex].messages) this.conversations[convIndex].messages = []
      this.conversations[convIndex].messages.push(tempMsg)
    }

    try {
      const res = await api.post(`/conversations/${conversationId}/messages`, { content })
      if (convIndex !== -1) {
        const msgIndex = this.conversations[convIndex].messages.findIndex(m => m.id === tempMsg.id)
        if (msgIndex !== -1) this.conversations[convIndex].messages[msgIndex] = res.data
      }
    } catch(error) {
      if (convIndex !== -1) {
        this.conversations[convIndex].messages = this.conversations[convIndex].messages.filter(m => m.id !== tempMsg.id)
      }
      console.error(error)
    }
  },
  
  async sendDirectMessage(targetUserId, content, skillId = null) {
    try {
      const res = await api.post('/conversations/direct', {
        target_user_id: targetUserId,
        content: content,
        skill_id: skillId
      })
      this.fetchDashboardData() // Refresh conversations
      return { success: true, data: res.data }
    } catch(error) {
      console.error("Error sending direct message", error)
      return { success: false, message: error.response?.data?.detail || "Erreur lors de l'envoi" }
    }
  },
  
  async fetchUserProfile(userId) {
    try {
      const res = await api.get(`/users/${userId}`)
      return { success: true, data: res.data }
    } catch(e) {
      console.error(e)
      return { success: false }
    }
  },

  async updateProfile(updates) {
    const backupUser = { ...this.user }
    Object.assign(this.user, updates) // Optimistic update
    try {
      await api.put('/users/me', updates)
      api.get('/users/me').then(userRes => {
        this.user = userRes.data
      })
      return { success: true }
    } catch(e) {
      this.user = backupUser // Revert
      console.error(e)
      return { success: false }
    }
  },

  async addSkill(skillId, type) {
    const skillName = this.skills.find(s => s.id === skillId)?.name || '...'
    const tempSkill = { skill_id: skillId, proficiency: type, skill: { id: skillId, name: skillName } }
    const existingIndex = this.user.skills.findIndex(s => s.skill_id === skillId)
    if (existingIndex !== -1) this.user.skills[existingIndex].proficiency = type
    else this.user.skills.push(tempSkill) // Optimistic update

    try {
      await api.post('/users/me/skills', { skill_id: skillId, proficiency: type })
      api.get('/users/me').then(userRes => this.user = userRes.data)
    } catch (e) {
      api.get('/users/me').then(userRes => this.user = userRes.data)
      console.error(e)
    }
  },

  async removeSkill(skillId) {
    const backupSkills = [...this.user.skills]
    this.user.skills = this.user.skills.filter(s => s.skill_id !== skillId) // Optimistic delete
    try {
      await api.delete(`/users/me/skills/${skillId}`)
      api.get('/users/me').then(userRes => this.user = userRes.data)
    } catch (e) {
      this.user.skills = backupSkills // Revert
      console.error(e)
    }
  },

  async addAvailability(avail) {
    const tempAvail = { id: 'temp-' + Date.now(), ...avail }
    if (!this.user.availabilities) this.user.availabilities = []
    this.user.availabilities.push(tempAvail) // Optimistic update
    try {
      await api.post('/users/me/availabilities', avail)
      api.get('/users/me').then(userRes => this.user = userRes.data)
    } catch (e) {
      this.user.availabilities = this.user.availabilities.filter(a => a.id !== tempAvail.id)
      console.error(e)
    }
  },

  async removeAvailability(availId) {
    const backupAvails = [...this.user.availabilities]
    this.user.availabilities = this.user.availabilities.filter(a => a.id !== availId) // Optimistic delete
    try {
      await api.delete(`/users/me/availabilities/${availId}`)
      api.get('/users/me').then(userRes => this.user = userRes.data)
    } catch (e) {
      this.user.availabilities = backupAvails // Revert
      console.error(e)
    }
  },

  toggleTheme() {
    this.theme = this.theme === 'light' ? 'dark' : 'light'
    localStorage.setItem('theme', this.theme)
    document.body.setAttribute('data-theme', this.theme)
  }
})

// Auto-sync reactive state to localStorage
watch(() => store.user, (val) => localStorage.setItem('user_cache', JSON.stringify(val)), { deep: true })
watch(() => store.posts, (val) => localStorage.setItem('posts_cache', JSON.stringify(val)), { deep: true })
watch(() => store.matches, (val) => localStorage.setItem('matches_cache', JSON.stringify(val)), { deep: true })
watch(() => store.conversations, (val) => localStorage.setItem('conversations_cache', JSON.stringify(val)), { deep: true })
watch(() => store.skills, (val) => localStorage.setItem('skills_cache', JSON.stringify(val)), { deep: true })
