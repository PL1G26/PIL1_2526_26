/**
 * IFRI MentorLink — Service de Notifications Temps Réel
 * Gère la connexion SSE, les toasts et la mise à jour du store.
 */

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

// ──── STATE INTERNE ────────────────────────────────────────────
let _eventSource = null
let _store = null
let _toastContainer = null
let _reconnectTimer = null
let _reconnectDelay = 2000   // ms, augmente exponentiellement
let _isIntentionalClose = false
let _onNewMessage = null     // callback externe optionnel

// ──── SONS (Web Audio API) ─────────────────────────────────────
let _audioCtx = null

function _playNotificationSound() {
  try {
    if (!_audioCtx) _audioCtx = new (window.AudioContext || window.webkitAudioContext)()
    const ctx = _audioCtx

    // Deux oscillateurs courts pour un son "ding" agréable
    const osc1 = ctx.createOscillator()
    const osc2 = ctx.createOscillator()
    const gain = ctx.createGain()

    osc1.connect(gain)
    osc2.connect(gain)
    gain.connect(ctx.destination)

    osc1.type = 'sine'
    osc2.type = 'sine'
    osc1.frequency.setValueAtTime(880, ctx.currentTime)
    osc2.frequency.setValueAtTime(1100, ctx.currentTime + 0.1)

    gain.gain.setValueAtTime(0.15, ctx.currentTime)
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.4)

    osc1.start(ctx.currentTime)
    osc1.stop(ctx.currentTime + 0.15)
    osc2.start(ctx.currentTime + 0.1)
    osc2.stop(ctx.currentTime + 0.35)
  } catch (_) {
    // Web Audio non dispo, on ignore silencieusement
  }
}

// ──── TOAST UI ─────────────────────────────────────────────────
function _ensureToastContainer() {
  if (_toastContainer && document.body.contains(_toastContainer)) return _toastContainer

  const container = document.createElement('div')
  container.id = 'notif-toast-container'
  container.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 99999;
    display: flex;
    flex-direction: column;
    gap: 10px;
    pointer-events: none;
    max-width: 360px;
    width: 100%;
  `
  document.body.appendChild(container)
  _toastContainer = container
  return container
}

function _showToast({ senderName, senderPhoto, content, conversationId, onClick }) {
  const container = _ensureToastContainer()

  const toast = document.createElement('div')
  toast.style.cssText = `
    background: var(--surface, #ffffff);
    border: 1px solid var(--border, #e2e8f0);
    border-left: 4px solid var(--primary, #6366f1);
    border-radius: 12px;
    padding: 14px 16px;
    display: flex;
    align-items: flex-start;
    gap: 12px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.15), 0 2px 8px rgba(0,0,0,0.08);
    pointer-events: all;
    cursor: pointer;
    opacity: 0;
    transform: translateX(120%);
    transition: opacity 0.35s cubic-bezier(.4,0,.2,1), transform 0.35s cubic-bezier(.4,0,.2,1);
    backdrop-filter: blur(8px);
  `
  toast.setAttribute('role', 'alert')
  toast.setAttribute('aria-live', 'polite')

  // Avatar
  const avatarEl = document.createElement('div')
  if (senderPhoto) {
    const img = document.createElement('img')
    img.src = senderPhoto
    img.style.cssText = 'width:40px;height:40px;border-radius:50%;object-fit:cover;flex-shrink:0;'
    img.onerror = () => { img.replaceWith(avatarEl) }
    toast.appendChild(img)
  } else {
    avatarEl.style.cssText = `
      width: 40px; height: 40px; border-radius: 50%; flex-shrink: 0;
      background: linear-gradient(135deg, var(--primary, #6366f1), #818cf8);
      display: flex; align-items: center; justify-content: center;
      color: white; font-weight: 700; font-size: 16px;
    `
    avatarEl.textContent = (senderName || '?')[0].toUpperCase()
    toast.appendChild(avatarEl)
  }

  // Contenu
  const body = document.createElement('div')
  body.style.cssText = 'flex:1; min-width:0;'

  const header = document.createElement('div')
  header.style.cssText = 'display:flex; align-items:center; justify-content:space-between; margin-bottom:4px;'

  const nameEl = document.createElement('span')
  nameEl.style.cssText = 'font-weight:700; font-size:14px; color: var(--text, #1e293b);'
  nameEl.textContent = senderName || 'Nouveau message'

  const badge = document.createElement('span')
  badge.style.cssText = `
    background: var(--primary, #6366f1); color: white;
    font-size: 10px; padding: 2px 7px; border-radius: 999px;
    font-weight: 600; letter-spacing: 0.5px;
  `
  badge.textContent = 'Nouveau'

  header.appendChild(nameEl)
  header.appendChild(badge)

  const msgEl = document.createElement('div')
  msgEl.style.cssText = 'font-size:13px; color: var(--text2, #64748b); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:260px;'
  msgEl.textContent = content || '...'

  body.appendChild(header)
  body.appendChild(msgEl)
  toast.appendChild(body)

  // Bouton fermer
  const closeBtn = document.createElement('button')
  closeBtn.style.cssText = `
    background: none; border: none; cursor: pointer; color: var(--text3, #94a3b8);
    font-size: 16px; padding: 0; line-height: 1; flex-shrink:0; align-self:center;
    pointer-events: all;
  `
  closeBtn.textContent = '×'
  closeBtn.title = 'Fermer'
  closeBtn.addEventListener('click', (e) => {
    e.stopPropagation()
    _removeToast(toast)
  })
  toast.appendChild(closeBtn)

  // Clic → ouvrir la conversation
  if (onClick) {
    toast.addEventListener('click', () => {
      onClick(conversationId)
      _removeToast(toast)
    })
  }

  container.appendChild(toast)

  // Animation d'entrée
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      toast.style.opacity = '1'
      toast.style.transform = 'translateX(0)'
    })
  })

  // Auto-dismiss après 5 secondes
  const timer = setTimeout(() => _removeToast(toast), 5000)
  toast._dismissTimer = timer

  return toast
}

function _removeToast(toast) {
  if (!toast || !toast.parentNode) return
  clearTimeout(toast._dismissTimer)
  toast.style.opacity = '0'
  toast.style.transform = 'translateX(120%)'
  setTimeout(() => toast.parentNode?.removeChild(toast), 380)
}

// ──── NOTIFICATIONS NATIVES (OS) ───────────────────────────────
function _showNativeNotification(title, options, onClick) {
  if (!('Notification' in window)) return
  
  if (Notification.permission === 'granted') {
    const notification = new Notification(title, options)
    if (onClick) {
      notification.onclick = function() {
        window.focus()
        onClick()
        notification.close()
      }
    }
  }
}

// ──── CONNEXION SSE ────────────────────────────────────────────
function _connect() {
  const token = localStorage.getItem('token')
  if (!token) return

  // Fermer l'ancienne connexion proprement
  if (_eventSource) {
    _eventSource.close()
    _eventSource = null
  }

  const url = `${API_URL}/notifications/stream?token=${encodeURIComponent(token)}`

  // L'EventSource standard ne supporte pas les headers Auth.
  // On passe le token en query param — le backend FastAPI doit l'accepter.
  // (On patch get_current_user pour lire aussi le query param 'token')
  _eventSource = new EventSource(url)

  _eventSource.onopen = () => {
    _reconnectDelay = 2000 // reset
    console.debug('[SSE] Connexion établie')
    window.dispatchEvent(new CustomEvent('sse-connected'))
  }

  _eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      _handleEvent(data)
    } catch (e) {
      console.warn('[SSE] Données invalides:', event.data)
    }
  }

  _eventSource.onerror = () => {
    if (_isIntentionalClose) return
    _eventSource?.close()
    _eventSource = null
    console.debug(`[SSE] Connexion perdue — reconnexion dans ${_reconnectDelay}ms`)
    window.dispatchEvent(new CustomEvent('sse-disconnected'))
    _scheduleReconnect()
  }
}

function _scheduleReconnect() {
  clearTimeout(_reconnectTimer)
  _reconnectTimer = setTimeout(() => {
    _reconnectDelay = Math.min(_reconnectDelay * 1.5, 30000) // cap à 30s
    _connect()
  }, _reconnectDelay)
}

function _handleEvent(data) {
  if (!data || !data.type) return

  if (data.type === 'ping' || data.type === 'connected') return

  if (data.type === 'new_message') {
    _onNewMessageReceived(data)
  }
}

async function _onNewMessageReceived(data) {
  const { conversation_id, message_id, sender_id, sender_name, sender_photo, content, created_at } = data

  // Ne pas notifier si l'utilisateur est déjà dans cette conversation
  const isCurrentConv = _store && _store.activeConversationId === conversation_id
  const isInChat = _store && _store.activeTab === 'chat'

  // Mettre à jour le store : injecter le message et incrémenter le unread_count
  if (_store) {
    const convIndex = _store.conversations.findIndex(c => c.id === conversation_id)
    if (convIndex !== -1) {
      const conv = _store.conversations[convIndex]

      // Ajouter le message dans les messages de la conversation si elle est sélectionnée
      if (isCurrentConv && conv.messages) {
        // Vérifier que le message n'est pas déjà présent (éviter les doublons)
        if (!conv.messages.find(m => m.id === message_id)) {
          conv.messages.push({
            id: message_id,
            conversation_id,
            sender_id,
            content,
            is_read: false,
            created_at,
            sender: { id: sender_id, first_name: sender_name.split(' ')[0], last_name: sender_name.split(' ').slice(1).join(' '), profile_photo: sender_photo }
          })
        }
        // Marquer comme lu automatiquement si dans la conversation active
        try {
          const { default: api } = await import('./api.js')
          api.put(`/conversations/${conversation_id}/read`)
        } catch (_) {}
      } else {
        // Incrémenter le compteur de non-lus
        conv.unread_count = (conv.unread_count || 0) + 1
      }

      // Mettre à jour le dernier message dans la liste
      conv.last_message = {
        id: message_id, conversation_id, sender_id, content,
        is_read: isCurrentConv, created_at
      }

      // Remonter la conversation en haut de la liste
      _store.conversations.splice(convIndex, 1)
      _store.conversations.unshift(conv)
    } else {
      // Conversation inconnue → recharger la liste complète en arrière-plan
      _store.fetchDashboardData?.()
    }
  }

  // Afficher le toast si l'utilisateur n'est pas dans cette conversation
  if (!isCurrentConv || !isInChat) {
    _playNotificationSound()

    // Mettre à jour le titre de la page
    const previousTitle = document.title.replace(/^\(\d+\) /, '')
    const totalUnread = _store
      ? _store.conversations.reduce((t, c) => t + (c.unread_count || 0), 0)
      : 1
    document.title = totalUnread > 0 ? `(${totalUnread}) ${previousTitle}` : previousTitle

    const onClickAction = (convId) => {
      if (_store) {
        _store.activeTab = 'chat'
        _store.selectConversation?.(convId)
      }
    }

    _showToast({
      senderName: sender_name,
      senderPhoto: sender_photo,
      content,
      conversationId: conversation_id,
      onClick: onClickAction
    })

    // Notification native si l'onglet n'est pas actif
    if (!document.hasFocus()) {
      _showNativeNotification(
        `Nouveau message de ${sender_name}`,
        { body: content, icon: sender_photo },
        () => onClickAction(conversation_id)
      )
    }
  }

  // Callback externe
  if (_onNewMessage) _onNewMessage(data)
}

// ──── API PUBLIQUE ──────────────────────────────────────────────
const notificationService = {
  /**
   * Démarre le service SSE.
   * Si déjà actif avec le même store, met juste à jour le callback.
   * @param {object} store  Le store réactif Vue
   * @param {function} [onNewMessage]  Callback optionnel sur nouveau message
   */
  start(store, onNewMessage = null) {
    // Demander la permission pour les notifications natives au démarrage
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission()
    }

    const alreadyRunning = _eventSource !== null && _store === store
    _store = store
    _onNewMessage = onNewMessage
    if (alreadyRunning) return // ne pas réouvrir la connexion
    _isIntentionalClose = false
    _connect()
  },

  /** Ferme proprement la connexion SSE et annule les timers. */
  stop() {
    _isIntentionalClose = true
    clearTimeout(_reconnectTimer)
    _eventSource?.close()
    _eventSource = null
    _store = null
    // Nettoyer le titre de page
    document.title = document.title.replace(/^\(\d+\) /, '')
  },

  /** Force une reconnexion (utile après un re-login). */
  reconnect() {
    _isIntentionalClose = false
    _reconnectDelay = 2000
    _connect()
  },

  /** Marque tous les messages d'une conversation comme lus. */
  async markConversationRead(conversationId) {
    try {
      const { default: api } = await import('./api.js')
      await api.put(`/conversations/${conversationId}/read`)
      if (_store) {
        const conv = _store.conversations.find(c => c.id === conversationId)
        if (conv) conv.unread_count = 0
      }
      // Nettoyer le titre
      const totalUnread = _store
        ? _store.conversations.reduce((t, c) => t + (c.unread_count || 0), 0)
        : 0
      const baseTitle = document.title.replace(/^\(\d+\) /, '')
      document.title = totalUnread > 0 ? `(${totalUnread}) ${baseTitle}` : baseTitle
    } catch (e) {
      console.warn('[Notif] Erreur markRead:', e)
    }
  },

  /** Affiche manuellement un toast (usage interne/test). */
  showToast: _showToast,
}

export default notificationService
