<template>
<div id="view-dashboard" v-if="store.user">
  <nav class="navbar">
    <div class="navbar-brand" @click="store.activeTab = 'home'">
      <span class="logo-dot"></span> IFRI MentorLink
    </div>
    <div class="navbar-links">
      <span style="font-size:13px;color:var(--text2);display:flex;align-items:center;gap:4px;">Bonjour, <strong>{{ store.user.first_name }}</strong> <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 11V6a2 2 0 0 0-4 0v4"/><path d="M14 10V5a2 2 0 0 0-4 0v5"/><path d="M10 10.5V4a2 2 0 0 0-4 0v10.5"/><path d="M6 14.5V11a2 2 0 0 0-4 0v5a8 8 0 0 0 16 0V11a2 2 0 0 0-4 0v-1"/></svg></span>
      <button aria-label="Basculer mode sombre/clair" class="theme-toggle" @click="store.toggleTheme()" title="Changer le thème">
        <span class="theme-icon-sync"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg></span>
      </button>
      <button class="btn btn-ghost btn-sm" @click="handleLogout">Déconnexion</button>
    </div>
  </nav>

  <div class="dashboard-layout">
    <aside class="sidebar">
      <div class="sidebar-user">
        <div class="avatar av-green" v-if="!photoOk('sidebar-user', store.user?.profile_photo)">{{ getInitials(store.user) }}</div>
        <img v-else :src="store.user.profile_photo" style="width:40px; height:40px; border-radius:50%; object-fit:cover;" @error="onPhotoError('sidebar-user')" />
        <div>
          <div class="sidebar-user-name">{{ store.user.first_name }} {{ store.user.last_name }}</div>
          <div class="sidebar-user-role">{{ store.user.field_of_study }} - {{ store.user.level }}</div>
        </div>
      </div>
      <nav class="sidebar-nav">
        <button class="sidebar-item" :class="{active: store.activeTab === 'home'}" @click="store.activeTab = 'home'">
          <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>
          Tableau de bord
        </button>
        <div class="sidebar-section-label">Mon Profil</div>
        <button class="sidebar-item" :class="{active: store.activeTab === 'profile'}" @click="store.activeTab = 'profile'">
          <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
          Profil & Compétences
        </button>
        <div class="sidebar-section-label">Mentorat</div>
        <button class="sidebar-item" :class="{active: store.activeTab === 'posts'}" @click="store.activeTab = 'posts'">
          <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" x2="8" y1="13" y2="13"></line><line x1="16" x2="8" y1="17" y2="17"></line></svg>
          Mes Posts
        </button>
        <button class="sidebar-item" :class="{active: store.activeTab === 'matches'}" @click="store.activeTab = 'matches'">
          <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="18" cy="5" r="3"></circle><circle cx="6" cy="12" r="3"></circle><circle cx="18" cy="19" r="3"></circle><line x1="8.59" x2="15.42" y1="13.51" y2="17.49"></line><line x1="15.41" x2="8.59" y1="6.51" y2="10.49"></line></svg>
          Correspondances
          <span class="badge-count" v-if="pendingMatchesCount > 0">{{ pendingMatchesCount }}</span>
        </button>
        <button class="sidebar-item" :class="{active: store.activeTab === 'chat'}" @click="store.activeTab = 'chat'">
          <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"></path></svg>
          Messagerie
          <span class="badge-count" v-if="totalUnreadMessages > 0">{{ totalUnreadMessages }}</span>
        </button>
        <div class="sidebar-section-label">Explorer</div>
        <button class="sidebar-item" :class="{active: store.activeTab === 'explore'}" @click="store.activeTab = 'explore'">
          <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"></circle><line x1="21" x2="16.65" y1="21" y2="16.65"></line></svg>
          Rechercher
        </button>
        <button class="sidebar-item" :class="{active: store.activeTab === 'history'}" @click="store.activeTab = 'history'">
          <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
          Historique
        </button>
      </nav>
    </aside>

    <main class="dash-content">
      <!-- HOME TAB -->
      <div class="tab-content" :class="{active: store.activeTab === 'home'}">
        <div class="welcome-banner">
          <h2 style="display:flex;align-items:center;gap:8px;">Bonjour ! <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 11V6a2 2 0 0 0-4 0v4"/><path d="M14 10V5a2 2 0 0 0-4 0v5"/><path d="M10 10.5V4a2 2 0 0 0-4 0v10.5"/><path d="M6 14.5V11a2 2 0 0 0-4 0v5a8 8 0 0 0 16 0V11a2 2 0 0 0-4 0v-1"/></svg></h2>
          <p>Bienvenue sur IFRI MentorLink.</p>
          <div class="welcome-actions">
            <button class="btn btn-white btn-sm" @click="store.activeTab = 'matches'">Voir mes correspondances →</button>
            <button class="btn btn-white-outline btn-sm" @click="store.activeTab = 'chat'">Ouvrir la messagerie</button>
          </div>
        </div>
        <div class="grid-3" style="margin-bottom:1.5rem;">
          <div class="metric-card">
            <div class="metric-num">{{ pendingMatchesCount }}</div>
            <div class="metric-label">Correspondances en attente</div>
          </div>
          <div class="metric-card">
            <div class="metric-num">{{ acceptedMatchesCount }}</div>
            <div class="metric-label">Sessions acceptées</div>
          </div>
          <div class="metric-card">
            <div class="metric-num">{{ myPosts.length }}</div>
            <div class="metric-label">Mes Posts actifs</div>
          </div>
        </div>
        <div class="grid-2">
          <div class="card">
            <div class="card-title" style="display:flex;align-items:center;gap:8px;"><svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 17v5"/><path d="M9 10.76a2 2 0 0 1-1.11 1.79l-1.78.9A2 2 0 0 0 5 15.24V16a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-.76a2 2 0 0 0-1.11-1.79l-1.78-.9A2 2 0 0 1 15 10.76V7a1 1 0 0 1 1-1 2 2 0 0 0 0-4H8a2 2 0 0 0 0 4 1 1 0 0 1 1 1z"/></svg> Mes compétences</div>
            <div style="margin-bottom:0.75rem;">
              <div class="skills-group-title" style="display:flex;align-items:center;gap:6px;"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg> Points forts</div>
              <div class="tag-row">
                <span class="tag tag-green" v-for="skill in userStrongSkills" :key="skill.skill_id">{{ skill.skill.name }}</span>
              </div>
            </div>
            <div>
              <div class="skills-group-title" style="display:flex;align-items:center;gap:6px;"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/></svg> À améliorer</div>
              <div class="tag-row">
                <span class="tag tag-red" v-for="skill in userWeakSkills" :key="skill.skill_id">{{ skill.skill.name }}</span>
              </div>
            </div>
            <button class="btn btn-outline btn-sm" style="margin-top:1rem;" @click="store.activeTab = 'profile'">Modifier le profil →</button>
          </div>
          <div class="card">
            <div class="card-title" style="display:flex;align-items:center;gap:8px;"><svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg> Prochaines disponibilités</div>
            <div style="display:flex;flex-direction:column;gap:8px;">
              <div class="avail-item" v-for="av in store.user.availabilities" :key="av.id">
                <span class="day">{{ formatDay(av.day_of_week) }}</span>
                <span class="time">{{ av.start_time.slice(0,5) }} — {{ av.end_time.slice(0,5) }}</span>
              </div>
              <div v-if="!store.user.availabilities?.length" style="color:var(--text3);font-size:13px;">Aucune disponibilité renseignée.</div>
            </div>
          </div>
        </div>
      </div>

      <!-- PROFILE TAB -->
      <div class="tab-content" :class="{active: store.activeTab === 'profile'}">
        <div class="page-header">
          <div>
            <div class="page-title">Mon Profil</div>
            <div class="page-subtitle">Infos personnelles, compétences et disponibilités</div>
          </div>
          <div style="display:flex;gap:8px;">
            <button class="btn btn-outline btn-sm" v-if="!isEditingProfile" @click="startEditProfile">Éditer le profil</button>
            <button class="btn btn-primary btn-sm" @click="store.fetchDashboardData()" v-if="!isEditingProfile">Rafraîchir</button>
            <button class="btn btn-primary btn-sm" v-if="isEditingProfile" :class="{'is-loading': isSavingProfile}" :disabled="isSavingProfile" @click="saveProfile">Sauvegarder</button>
            <button class="btn btn-ghost btn-sm" v-if="isEditingProfile" :disabled="isSavingProfile" @click="cancelEditProfile">Annuler</button>
          </div>
        </div>
        
        <div class="grid-2">
          <div class="card">
            <div class="card-title">Informations personnelles</div>
            
            <div v-if="isEditingProfile" style="margin-bottom: 1rem; display: flex; align-items: center; gap: 1rem;">
              <div class="avatar av-green" v-if="!photoOk('edit-profile', editProfileForm.profile_photo)" style="width:60px; height:60px; font-size:24px; display:flex; align-items:center; justify-content:center;">{{ getInitials(store.user) }}</div>
              <img v-else :src="editProfileForm.profile_photo" style="width:60px; height:60px; border-radius:50%; object-fit:cover;" @error="onPhotoError('edit-profile')" />
              <div>
                <label class="btn btn-outline btn-sm" style="cursor:pointer;">
                  Changer de photo
                  <input type="file" accept="image/*" style="display:none" @change="onProfilePhotoChange" />
                </label>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group"><label>Prénom</label><input type="text" :disabled="!isEditingProfile" v-model="editProfileForm.first_name" v-if="isEditingProfile"/><input type="text" disabled :value="store.user.first_name" v-else/></div>
              <div class="form-group"><label>Nom</label><input type="text" :disabled="!isEditingProfile" v-model="editProfileForm.last_name" v-if="isEditingProfile"/><input type="text" disabled :value="store.user.last_name" v-else/></div>
            </div>
            <div class="form-group"><label>Email</label><input type="email" disabled :value="store.user.email"/></div>
            <div class="form-group"><label>Téléphone</label><input type="tel" disabled :value="store.user.phone_number"/></div>
            <div class="form-group"><label>Filière</label>
              <select v-if="isEditingProfile" v-model="editProfileForm.field_of_study">
                <option value="IA">IA</option>
                <option value="IM">IM</option>
                <option value="GL">GL</option>
                <option value="SE&IoT">SE&IoT</option>
                <option value="SI">SI</option>
              </select>
              <input v-else type="text" disabled :value="store.user.field_of_study"/>
            </div>
            <div class="form-group"><label>Niveau</label>
              <select v-if="isEditingProfile" v-model="editProfileForm.level">
                <option value="L1">L1</option>
                <option value="L2">L2</option>
                <option value="L3">L3</option>
                <option value="M1">M1</option>
                <option value="M2">M2</option>
              </select>
              <input v-else type="text" disabled :value="store.user.level"/>
            </div>
            <div class="form-group"><label>Bio</label><textarea :disabled="!isEditingProfile" v-model="editProfileForm.bio" v-if="isEditingProfile"></textarea><textarea disabled :value="store.user.bio" v-else></textarea></div>
          </div>

          <div style="display:flex;flex-direction:column;gap:1.5rem;">
            <!-- COMPETENCES -->
            <div class="card">
              <div class="card-title" style="display:flex;align-items:center;gap:8px;"><svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/></svg> Compétences</div>
              <div class="skills-group">
                <div class="skills-group-title" style="display:flex;align-items:center;gap:6px;"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg> Points forts — je peux enseigner</div>
                <div class="skills-grid">
                  <div class="skill-chip" v-for="skill in userStrongSkills" :key="skill.skill_id">
                    <span>{{ skill.skill.name }}</span>
                    <button class="skill-chip-remove" @click="store.removeSkill(skill.skill_id)">×</button>
                  </div>
                </div>
              </div>
              <div class="skills-group">
                <div class="skills-group-title" style="color:#7A5200;display:flex;align-items:center;gap:6px;"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/></svg> Lacunes — j'ai besoin d'aide</div>
                <div class="skills-grid">
                  <div class="skill-chip" style="border-color:#FFC72C;" v-for="skill in userWeakSkills" :key="skill.skill_id">
                    <span>{{ skill.skill.name }}</span>
                    <button class="skill-chip-remove" @click="store.removeSkill(skill.skill_id)">×</button>
                  </div>
                </div>
              </div>
              <div class="add-skill-row">
                <select v-model="newSkill.id">
                  <option value="">Choisir une matière…</option>
                  <option v-for="s in store.skills" :key="s.id" :value="s.id">{{ s.name }}</option>
                </select>
                <select v-model="newSkill.type" class="type-select">
                  <option value="strong">Point fort</option>
                  <option value="weak">Lacune</option>
                </select>
                <button class="btn btn-primary btn-sm" :class="{'is-loading': isAddingSkill}" @click="handleAddSkill" :disabled="!newSkill.id">+ Ajouter</button>
              </div>
            </div>

            <!-- DISPONIBILITÉS -->
            <div class="card">
              <div class="card-title" style="display:flex;align-items:center;gap:8px;"><svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg> Disponibilités</div>
              <div class="avail-list">
                <div class="avail-item" v-for="av in store.user.availabilities" :key="av.id">
                  <span class="day">{{ formatDay(av.day_of_week) }}</span>
                  <span class="time">{{ av.start_time.slice(0,5) }} — {{ av.end_time.slice(0,5) }}</span>
                  <button class="btn btn-ghost btn-sm" @click="store.removeAvailability(av.id)">×</button>
                </div>
              </div>
              <div class="avail-add-form">
                <div>
                  <label style="font-size:11px;">Jour</label>
                  <select v-model="newAvail.day_of_week" style="border-radius:var(--radius);">
                    <option value="Monday">Lundi</option>
                    <option value="Tuesday">Mardi</option>
                    <option value="Wednesday">Mercredi</option>
                    <option value="Thursday">Jeudi</option>
                    <option value="Friday">Vendredi</option>
                    <option value="Saturday">Samedi</option>
                    <option value="Sunday">Dimanche</option>
                  </select>
                </div>
                <div>
                  <label style="font-size:11px;">Début</label>
                  <input type="time" v-model="newAvail.start_time" style="border-radius:var(--radius);">
                </div>
                <div>
                  <label style="font-size:11px;">Fin</label>
                  <input type="time" v-model="newAvail.end_time" style="border-radius:var(--radius);">
                </div>
                <button class="btn btn-primary btn-sm" :class="{'is-loading': isAddingAvail}" @click="handleAddAvailability" style="align-self:flex-end;" :disabled="!newAvail.start_time || !newAvail.end_time">+ Ajouter</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- POSTS TAB -->
      <div class="tab-content" :class="{active: store.activeTab === 'posts'}">
        <div class="page-header">
          <div>
            <div class="page-title">Mes Posts</div>
            <div class="page-subtitle">Offres et demandes de mentorat publiées</div>
          </div>
          <button class="btn btn-primary" @click="showPostModal = true">+ Nouveau post</button>
        </div>
        <div class="filter-bar">
          <span style="font-size:13px;font-weight:500;color:var(--text2);">Filtrer :</span>
          <div class="filter-chip" :class="{active: myPostFilter === 'all'}" @click="myPostFilter = 'all'">Tous</div>
          <div class="filter-chip" :class="{active: myPostFilter === 'offer'}" @click="myPostFilter = 'offer'">Offres</div>
          <div class="filter-chip" :class="{active: myPostFilter === 'request'}" @click="myPostFilter = 'request'">Demandes</div>
        </div>
        <div id="posts-list">
          <div v-if="filteredMyPosts.length === 0" style="padding:2rem;text-align:center;color:var(--text3);">Aucun post correspondant.</div>
          <div class="card" v-for="post in filteredMyPosts" :key="post.id" style="margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
              <div>
                <div style="font-weight: bold">{{ post.skill?.name || 'Matière inconnue' }} <span style="font-size: 12px; font-weight: normal; color: var(--text3)">- {{ post.type === 'offer' ? 'Offre' : 'Demande' }}</span></div>
                <p style="margin: 0.5rem 0;">{{ post.description }}</p>
                <div style="font-size: 13px; color: var(--text3)">Format: {{ post.mode }} | Créé le: {{ new Date(post.created_at).toLocaleDateString() }}</div>
              </div>
              <button class="btn btn-ghost btn-sm" style="color: #e74c3c; padding: 4px;" :class="{'is-loading': postActionLoading === post.id}" :disabled="postActionLoading === post.id" @click="handleDeletePost(post.id)" title="Supprimer ce post">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- MATCHES TAB -->
      <div class="tab-content" :class="{active: store.activeTab === 'matches'}">
        <div class="page-header">
          <div>
            <div class="page-title">Correspondances</div>
            <div class="page-subtitle">Résultats de l'algorithme de matching</div>
          </div>
        </div>
        <div id="matches-list">
          <div v-if="pendingMatches.length === 0" style="padding:2rem;text-align:center;color:var(--text3);">Aucune correspondance en attente. Remplissez bien votre profil !</div>
          <div class="card match-card" v-for="match in pendingMatches" :key="match.id" style="margin-bottom: 1rem;">
            <div style="display:flex; justify-content: space-between; align-items:center; gap: 1rem;">
              <div style="display:flex; gap: 1.5rem; flex:1; flex-wrap: wrap;">
                <!-- Mentor -->
                <div class="match-user-card">
                  <div class="match-user-label">Mentor</div>
                  <div style="display:flex; align-items:center; gap: 10px;">
                    <div v-if="!photoOk('mentor-'+match.id, match.mentor?.profile_photo)" class="avatar av-green" style="width:38px;height:38px;font-size:15px;flex-shrink:0;">{{ (match.mentor?.first_name?.[0] || '') + (match.mentor?.last_name?.[0] || '') }}</div>
                    <img v-else :src="match.mentor.profile_photo" style="width:38px;height:38px;border-radius:50%;object-fit:cover;flex-shrink:0;" @error="onPhotoError('mentor-'+match.id)" />
                    <div>
                      <div style="font-weight:600;font-size:14px;">{{ match.mentor?.first_name }} {{ match.mentor?.last_name }}</div>
                      <div style="font-size:12px;color:var(--text3);">{{ match.mentor?.field_of_study }} · {{ match.mentor?.level }}</div>
                    </div>
                  </div>
                </div>
                <!-- Compétence -->
                <div style="display:flex;align-items:center;">
                  <span class="tag tag-green" style="font-size:12px;">{{ match.skill?.name || store.skills.find(s => s.id === match.skill_id)?.name }}</span>
                </div>
                <!-- Disponibilités -->
                <div style="display:flex;flex-direction:column; justify-content:center;">
                  <div style="font-size: 11px; color: var(--text2); margin-bottom: 4px;">{{ match.offer_post_id ? "Dispo pour l'offre :" : "Dispo du mentor :" }}</div>
                  <div style="display:flex; flex-wrap:wrap; gap:4px;">
                    <template v-if="getMatchAvailabilities(match)?.length">
                      <template v-if="getMatchAvailabilities(match).length <= 2">
                        <span v-for="av in getMatchAvailabilities(match)" :key="av.id" style="background: var(--surface2); padding: 2px 6px; border-radius: 4px; font-size: 11px; border: 1px solid var(--border);">
                          {{ formatDay(av.day_of_week) }} {{ av.start_time.slice(0,5) }} - {{ av.end_time.slice(0,5) }}
                        </span>
                      </template>
                      <select v-else style="font-size: 11px; padding: 2px; border-radius: 4px; border: 1px solid var(--border); background: var(--surface2); max-width: 180px;">
                        <option value="">{{ getMatchAvailabilities(match).length }} créneaux disponibles...</option>
                        <option v-for="av in getMatchAvailabilities(match)" :key="av.id" :value="av.id" disabled>
                          {{ formatDay(av.day_of_week) }} {{ av.start_time.slice(0,5) }} - {{ av.end_time.slice(0,5) }}
                        </option>
                      </select>
                    </template>
                    <span v-else style="font-size: 11px; color: var(--text3);">Non précisée</span>
                  </div>
                </div>
              </div>
              <div style="text-align: right; flex-shrink:0;">
                <div style="margin-bottom: 8px;">
                  <span class="tag tag-green">Score: {{ match.score }}%</span>
                </div>
                <div v-if="match.mentee_id === store.user.id">
                  <button class="btn btn-primary btn-sm" :class="{'is-loading': matchActionLoading[match.id] === 'accept'}" :disabled="matchActionLoading[match.id]" @click="handleAcceptMatch(match.id)" style="margin-right: 4px;">Accepter</button>
                  <button class="btn btn-ghost btn-sm" :class="{'is-loading': matchActionLoading[match.id] === 'reject'}" :disabled="matchActionLoading[match.id]" @click="handleRejectMatch(match.id)">Refuser</button>
                </div>
                <div v-else style="font-size: 12px; color: var(--text3)">
                  En attente de la réponse du mentoré...
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- CHAT TAB -->
      <div class="tab-content" :class="{active: store.activeTab === 'chat'}">
        <div class="page-header">
          <div>
            <div class="page-title">Messagerie</div>
            <div class="page-subtitle">Conversations avec tes mentors et mentorés</div>
          </div>
        </div>
        <div class="chat-layout" style="height:calc(100vh - 200px);min-height:400px;">
          <div class="conv-list" style="overflow-y:auto;">
            <div class="conv-list-header" style="display:flex;align-items:center;gap:6px;"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 21 1.9-5.7a8.5 8.5 0 1 1 3.8 3.8z"/></svg> Conversations</div>
            <div v-if="store.conversations.length === 0" style="padding: 1rem; color: var(--text3); font-size: 13px;">Aucune conversation (acceptez un match d'abord).</div>
            <div v-for="conv in store.conversations" :key="conv.id"
                 @click="store.selectConversation(conv.id)"
                 class="conv-item" :class="{active: store.activeConversationId === conv.id}">
              <!-- Avatar -->
              <div v-if="!photoOk('conv-'+conv.id, conv.other_user?.profile_photo)" class="avatar av-green" style="width:36px;height:36px;font-size:13px;flex-shrink:0;">
                {{ (conv.other_user?.first_name?.[0] || '') + (conv.other_user?.last_name?.[0] || '') }}
              </div>
              <img v-else :src="conv.other_user.profile_photo" style="width:36px;height:36px;border-radius:50%;object-fit:cover;flex-shrink:0;" @error="onPhotoError('conv-'+conv.id)" />
              <!-- Infos -->
              <div class="conv-item-info">
                <div class="conv-item-name" :style="conv.unread_count > 0 ? 'font-weight: 700; color: var(--text);' : ''">{{ conv.other_user?.first_name }} {{ conv.other_user?.last_name }}</div>
                <div class="conv-item-preview" :style="conv.unread_count > 0 ? 'font-weight: 600; color: var(--text);' : ''">{{ conv.last_message?.content || 'Démarrer la conversation…' }}</div>
              </div>
              <!-- Badge non-lu -->
              <div v-if="conv.unread_count > 0" class="unread-dot" :title="conv.unread_count + ' non lu(s)'"></div>
            </div>
          </div>
          <div class="chat-area" style="display:flex;flex-direction:column;overflow:hidden;">
            <div v-if="!store.activeConversationId" class="chat-placeholder">
              <div class="chat-placeholder-icon"><svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 21 1.9-5.7a8.5 8.5 0 1 1 3.8 3.8z"/></svg></div>
              <h4>Sélectionne une conversation</h4>
            </div>
            <div v-else style="display:flex; flex-direction:column; height: 100%;">
              <!-- En-tête de la conversation avec identité réelle -->
              <div class="chat-header" v-if="activeConversationPartner">
                <div v-if="!photoOk('chat-header', activeConversationPartner.profile_photo)" class="avatar av-green" style="width:38px;height:38px;font-size:14px;flex-shrink:0;">
                  {{ (activeConversationPartner.first_name?.[0] || '') + (activeConversationPartner.last_name?.[0] || '') }}
                </div>
                <img v-else :src="activeConversationPartner.profile_photo" style="width:38px;height:38px;border-radius:50%;object-fit:cover;flex-shrink:0;" @error="onPhotoError('chat-header')" />
                <div class="chat-header-info">
                  <div class="chat-header-name">{{ activeConversationPartner.first_name }} {{ activeConversationPartner.last_name }}</div>
                  <div class="chat-header-sub"><span class="chat-online-dot"></span>Conversation active</div>
                </div>
              </div>
              <!-- Messages -->
              <div style="flex:1; overflow-y:auto; padding: 1rem;">
                <div v-for="msg in activeConversationMessages" :key="msg.id" style="margin-bottom: 10px;">
                  <div :style="{textAlign: msg.sender_id === store.user.id ? 'right' : 'left'}">
                    <span style="background: var(--surface2); padding: 8px 12px; border-radius: 12px; display: inline-block;">
                      {{ msg.content }}
                    </span>
                    <div style="font-size: 10px; color: var(--text3); margin-top: 2px;">
                      {{ new Date(msg.created_at).toLocaleTimeString().slice(0,5) }}
                      <span v-if="msg.sender_id === store.user.id" style="margin-left: 4px;" :title="msg.is_read ? 'Lu' : 'Envoyé'">
                        <svg v-if="msg.is_read" xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: var(--primary)"><path d="m3 12 5 5 13-13"/><path d="m14 12 5 5 5-13"/></svg>
                        <svg v-else xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>
                      </span>
                    </div>
                  </div>
                </div>
              </div>
              <!-- Zone de saisie -->
              <div style="padding: 1rem; border-top: 1px solid var(--border); display: flex; gap: 8px;">
                <input v-model="chatInput" type="text" placeholder="Écrire un message..." style="flex: 1" @keyup.enter="sendChat" :disabled="isSendingMessage">
                <button class="btn btn-primary" :class="{'is-loading': isSendingMessage}" :disabled="isSendingMessage" @click="sendChat">Envoyer</button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- EXPLORE TAB -->
      <div class="tab-content" :class="{active: store.activeTab === 'explore'}">
        <div class="page-header">
          <div>
            <div class="page-title" style="display:flex;align-items:center;gap:8px;"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg> Rechercher</div>
            <div class="page-subtitle">Explore les offres et demandes du campus</div>
          </div>
        </div>
        <div class="filter-bar" style="margin-bottom: 1rem; display: flex; gap: 10px; flex-wrap: wrap;">
          <input type="text" v-model="exploreSearch" placeholder="Mots-clés..." style="padding: 6px 12px; border: 1px solid var(--border); border-radius: var(--radius); font-size: 13px;" />
          
          <select v-model="exploreType" style="padding: 6px 12px; border: 1px solid var(--border); border-radius: var(--radius); font-size: 13px;">
            <option value="all">Tous types</option>
            <option value="offer">Offres de Mentorat</option>
            <option value="request">Demandes d'Aide</option>
          </select>

          <select v-model="exploreSkillId" style="padding: 6px 12px; border: 1px solid var(--border); border-radius: var(--radius); font-size: 13px;">
            <option value="">Toutes les matières</option>
            <option v-for="s in store.skills" :key="s.id" :value="s.id">{{ s.name }}</option>
          </select>
        </div>

        <div id="explore-posts-list" style="display: grid; gap: 1rem;">
          <div v-if="filteredExplorePosts.length === 0" style="padding:2rem;text-align:center;color:var(--text3);">Aucun post disponible correspondant à vos filtres.</div>
          <div class="card" v-for="post in filteredExplorePosts" :key="post.id">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
              <div style="font-weight: bold">{{ post.skill?.name || 'Matière inconnue' }} 
                <span class="tag" :class="{'tag-green': post.type==='offer', 'tag-red': post.type==='request'}" style="margin-left: 8px;">
                  {{ post.type === 'offer' ? 'Offre de Mentorat' : 'Demande d\'Aide' }}
                </span>
              </div>
              <button class="btn btn-primary btn-sm" v-if="isPostCompatible(post)" @click="openDirectMessage(post)" :disabled="directMessageLoading === post.id" :class="{'is-loading': directMessageLoading === post.id}">{{ post.type === 'offer' ? "Bénéficier de l'offre" : "Proposer mon aide" }}</button>
            </div>
            <p style="margin: 0.5rem 0;">{{ post.description || 'Aucune description fournie.' }}</p>
            <div v-if="post.availabilities && post.availabilities.length > 0" style="margin-bottom: 0.75rem; font-size: 13px;">
              <div style="color: var(--text2); margin-bottom: 4px;">Disponibilités :</div>
              <div style="display: flex; flex-wrap: wrap; gap: 6px;">
                <span style="background: var(--surface2); padding: 2px 8px; border-radius: 4px; font-size: 12px; border: 1px solid var(--border);" v-for="av in post.availabilities" :key="av.id">
                  {{ formatDay(av.day_of_week) }} {{ av.start_time.slice(0,5) }} - {{ av.end_time.slice(0,5) }}
                </span>
              </div>
            </div>
            <div style="font-size: 13px; color: var(--text3); display: flex; justify-content: space-between; align-items:center;">
              <div>Publié par <strong style="cursor:pointer; color:var(--primary); text-decoration:underline;" @click="viewProfile(post.user?.id)">{{ post.user?.first_name }} {{ post.user?.last_name }}</strong> ({{ post.user?.field_of_study }} {{ post.user?.level }})</div>
              <div>Format: {{ post.mode === 'online' ? 'En ligne' : post.mode === 'offline' ? 'Présentiel' : 'Les deux' }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- HISTORY TAB -->
      <div class="tab-content" :class="{active: store.activeTab === 'history'}">
        <div class="page-header">
          <div>
            <div class="page-title">Historique</div>
            <div class="page-subtitle">Vos anciens matchs acceptés et refusés</div>
          </div>
        </div>
        <div id="history-matches-list">
          <div v-if="historyMatches.length === 0" style="padding:2rem;text-align:center;color:var(--text3);">Aucun historique disponible.</div>
          <div class="card match-card" v-for="match in historyMatches" :key="match.id" style="margin-bottom: 1rem; opacity: 0.85;">
            <div style="display:flex; justify-content: space-between; align-items:center; gap: 1rem;">
              <div style="display:flex; gap: 1.5rem; flex:1; flex-wrap: wrap;">
                <!-- Mentor -->
                <div class="match-user-card">
                  <div class="match-user-label">Mentor</div>
                  <div style="display:flex; align-items:center; gap: 10px;">
                    <div v-if="!photoOk('h-mentor-'+match.id, match.mentor?.profile_photo)" class="avatar av-green" style="width:38px;height:38px;font-size:15px;flex-shrink:0;">{{ (match.mentor?.first_name?.[0] || '') + (match.mentor?.last_name?.[0] || '') }}</div>
                    <img v-else :src="match.mentor.profile_photo" style="width:38px;height:38px;border-radius:50%;object-fit:cover;flex-shrink:0;" @error="onPhotoError('h-mentor-'+match.id)" />
                    <div>
                      <div style="font-weight:600;font-size:14px;">{{ match.mentor?.first_name }} {{ match.mentor?.last_name }}</div>
                      <div style="font-size:12px;color:var(--text3);">{{ match.mentor?.field_of_study }} · {{ match.mentor?.level }}</div>
                    </div>
                  </div>
                </div>
                <!-- Compétence -->
                <div style="display:flex;align-items:center;">
                  <span class="tag" style="font-size:12px;">{{ match.skill?.name || store.skills.find(s => s.id === match.skill_id)?.name }}</span>
                </div>
                <!-- Disponibilités -->
                <div style="display:flex;flex-direction:column; justify-content:center;">
                  <div style="font-size: 11px; color: var(--text2); margin-bottom: 4px;">{{ match.offer_post_id ? "Dispo pour l'offre :" : "Dispo du mentor :" }}</div>
                  <div style="display:flex; flex-wrap:wrap; gap:4px;">
                    <template v-if="getMatchAvailabilities(match)?.length">
                      <template v-if="getMatchAvailabilities(match).length <= 2">
                        <span v-for="av in getMatchAvailabilities(match)" :key="av.id" style="background: var(--surface2); padding: 2px 6px; border-radius: 4px; font-size: 11px; border: 1px solid var(--border);">
                          {{ formatDay(av.day_of_week) }} {{ av.start_time.slice(0,5) }} - {{ av.end_time.slice(0,5) }}
                        </span>
                      </template>
                      <select v-else style="font-size: 11px; padding: 2px; border-radius: 4px; border: 1px solid var(--border); background: var(--surface2); max-width: 180px;">
                        <option value="">{{ getMatchAvailabilities(match).length }} créneaux disponibles...</option>
                        <option v-for="av in getMatchAvailabilities(match)" :key="av.id" :value="av.id" disabled>
                          {{ formatDay(av.day_of_week) }} {{ av.start_time.slice(0,5) }} - {{ av.end_time.slice(0,5) }}
                        </option>
                      </select>
                    </template>
                    <span v-else style="font-size: 11px; color: var(--text3);">Non précisée</span>
                  </div>
                </div>
              </div>
              <div style="text-align: right; flex-shrink:0;">
                <div style="margin-bottom: 8px;">
                  <span class="tag" :class="{'tag-green': match.status === 'accepted', 'tag-red': match.status === 'rejected'}">{{ match.status === 'accepted' ? 'Accepté' : 'Refusé' }}</span>
                  <span class="tag tag-green" style="margin-left:4px;">Score: {{ match.score }}%</span>
                </div>
                <div style="font-size: 12px; color: var(--text3)">{{ new Date(match.created_at).toLocaleDateString() }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

    </main>
  </div>

  <!-- Modal Nouveau Post -->
  <div class="post-form-modal" v-if="showPostModal" style="display:flex;">
    <form class="post-form-box" @submit.prevent="submitPost">
      <h3 style="display:flex;align-items:center;gap:8px;"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg> Nouveau post</h3>
      <div class="form-row">
        <div class="form-group">
          <label>Type *</label>
          <select v-model="newPost.type" required>
            <option value="offer">Offre — je peux aider</option>
            <option value="request">Demande — j'ai besoin d'aide</option>
          </select>
        </div>
        <div class="form-group">
          <label>Matière *</label>
          <select v-model.number="newPost.skill_id" required>
            <option value="">Choisir…</option>
            <option v-for="s in store.skills" :key="s.id" :value="s.id">{{ s.name }}</option>
          </select>
        </div>
      </div>
      <div class="form-group">
        <label>Format *</label>
        <select v-model="newPost.mode" required>
          <option value="online">En ligne</option>
          <option value="offline">Présentiel</option>
          <option value="both">Les deux</option>
        </select>
      </div>
      <div class="form-group">
        <label>Créneau de disponibilité *</label>
        <template v-if="store.user.availabilities && store.user.availabilities.length > 0">
          <select v-model="newPost.availability_id" required>
            <option value="">Choisir un créneau…</option>
            <option v-for="av in store.user.availabilities" :key="av.id" :value="av.id">
              {{ formatDay(av.day_of_week) }} {{ av.start_time.slice(0,5) }} — {{ av.end_time.slice(0,5) }}
            </option>
          </select>
        </template>
        <template v-else>
          <div style="font-size: 13px; color: var(--error, #e74c3c); padding: 8px; background: var(--error-bg, #fdf0ef); border-radius: var(--radius);">
            Vous n'avez encore aucune disponibilité. Veuillez en ajouter une dans votre profil d'abord.
          </div>
        </template>
      </div>
      <div class="form-group">
        <label>Description (optionnel)</label>
        <textarea v-model="newPost.description" placeholder="Ex : Je propose des sessions..." style="min-height:80px;"></textarea>
      </div>
      <div class="modal-actions">
        <button type="button" class="btn btn-ghost" @click="showPostModal = false" :disabled="isSubmittingPost">Annuler</button>
        <button type="submit" class="btn btn-primary" :class="{'is-loading': isSubmittingPost}" :disabled="!newPost.skill_id || !newPost.availability_id || isSubmittingPost">Publier le post</button>
      </div>
    </form>
  </div>

  <!-- Modal Profil Utilisateur -->
  <div class="post-form-modal" v-if="showProfileModal" style="display:flex;">
    <div class="post-form-box" style="max-width: 500px; width:100%;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 1rem;">
        <h3 style="margin:0;">Profil de {{ viewedProfile?.first_name }}</h3>
        <button class="btn btn-ghost btn-sm" @click="showProfileModal = false">✕</button>
      </div>
      
      <div v-if="viewedProfile">
        <div style="margin-bottom: 1rem; padding: 1rem; background: var(--surface2); border-radius: var(--radius); display: flex; align-items: center; gap: 1rem;">
          <div class="avatar av-green" v-if="!photoOk('viewed-profile', viewedProfile.profile_photo)" style="width:50px; height:50px; font-size:20px; display:flex; align-items:center; justify-content:center;">{{ getInitials(viewedProfile) }}</div>
          <img v-else :src="viewedProfile.profile_photo" style="width:50px; height:50px; border-radius:50%; object-fit:cover;" @error="onPhotoError('viewed-profile')" />
          <div>
            <strong>{{ viewedProfile.first_name }} {{ viewedProfile.last_name }}</strong>
            <div style="color: var(--text2); font-size: 13px;">{{ viewedProfile.field_of_study }} - Niveau {{ viewedProfile.level }}</div>
            <p style="font-size: 13px; margin-top: 8px;">{{ viewedProfile.bio || 'Aucune bio disponible.' }}</p>
          </div>
        </div>

        <h4 style="margin-bottom:0.5rem;display:flex;align-items:center;gap:6px;">Points forts <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg></h4>
        <div class="tag-row" style="margin-bottom: 1rem;">
          <span class="tag tag-green" v-for="skill in viewedProfile.skills.filter(s => s.proficiency === 'strong')" :key="skill.skill_id">{{ skill.skill.name }}</span>
          <span v-if="!viewedProfile.skills.filter(s => s.proficiency === 'strong').length" style="font-size:12px; color:var(--text3)">Aucun point fort.</span>
        </div>

        <h4 style="margin-bottom:0.5rem;display:flex;align-items:center;gap:6px;">Lacunes <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/></svg></h4>
        <div class="tag-row" style="margin-bottom: 1rem;">
          <span class="tag tag-red" v-for="skill in viewedProfile.skills.filter(s => s.proficiency === 'weak')" :key="skill.skill_id">{{ skill.skill.name }}</span>
          <span v-if="!viewedProfile.skills.filter(s => s.proficiency === 'weak').length" style="font-size:12px; color:var(--text3)">Aucune lacune.</span>
        </div>
      </div>
    </div>
  </div>

  <!-- Modal Message -->
  <div class="post-form-modal" v-if="showMessageModal" style="display:flex;">
    <div class="post-form-box" style="max-width: 500px; width:100%;">
      <h3 style="display:flex;align-items:center;gap:8px;margin-bottom:1rem;">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
        Envoyer un message
      </h3>
      <p style="font-size: 14px; margin-bottom: 1rem; color: var(--text2);">
        Envoyer un message à <strong>{{ selectedPostForMessage?.user?.first_name }}</strong> pour sa publication en <strong>{{ selectedPostForMessage?.skill?.name || 'cette matière' }}</strong> :
      </p>
      <div class="form-group">
        <textarea v-model="messageContent" placeholder="Bonjour, je suis intéressé(e) par..." style="min-height: 100px; width: 100%; font-family: inherit; font-size: inherit; padding: 12px; border-radius: var(--radius); border: 1px solid var(--border); background: var(--surface); color: var(--text);" autofocus></textarea>
      </div>
      <div class="modal-actions" style="margin-top: 1.5rem;">
        <button type="button" class="btn btn-ghost" @click="cancelDirectMessage" :disabled="isSendingDirectMessage">Annuler</button>
        <button type="button" class="btn btn-primary" :class="{'is-loading': isSendingDirectMessage}" :disabled="!messageContent.trim() || isSendingDirectMessage" @click="confirmSendDirectMessage">Envoyer</button>
      </div>
    </div>
  </div>
</div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { store } from '../store'

const router = useRouter()

// Gestion des photos introuvables : stocke les clés d'images en erreur
const brokenPhotos = reactive(new Set())
const onPhotoError = (key) => brokenPhotos.add(key)
const photoOk = (key, url) => url && !brokenPhotos.has(key)

// Profile Edit
const isEditingProfile = ref(false)
const isSavingProfile = ref(false)
const editProfileForm = ref({})

const startEditProfile = () => {
  editProfileForm.value = {
    first_name: store.user.first_name,
    last_name: store.user.last_name,
    field_of_study: store.user.field_of_study,
    level: store.user.level,
    bio: store.user.bio || '',
    profile_photo: store.user.profile_photo || ''
  }
  isEditingProfile.value = true
}

const cancelEditProfile = () => {
  isEditingProfile.value = false
}

const saveProfile = async () => {
  isSavingProfile.value = true
  const res = await store.updateProfile(editProfileForm.value)
  if (res.success) {
    isEditingProfile.value = false
  } else {
    alert("Erreur lors de la mise à jour du profil.")
  }
  isSavingProfile.value = false
}

const onProfilePhotoChange = (event) => {
  const file = event.target.files[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = (e) => {
      // Resize image using a canvas
      const img = new Image()
      img.onload = () => {
        const canvas = document.createElement('canvas')
        const MAX_WIDTH = 400
        const MAX_HEIGHT = 400
        let width = img.width
        let height = img.height

        if (width > height) {
          if (width > MAX_WIDTH) {
            height *= MAX_WIDTH / width
            width = MAX_WIDTH
          }
        } else {
          if (height > MAX_HEIGHT) {
            width *= MAX_HEIGHT / height
            height = MAX_HEIGHT
          }
        }
        canvas.width = width
        canvas.height = height
        const ctx = canvas.getContext('2d')
        ctx.drawImage(img, 0, 0, width, height)
        const dataUrl = canvas.toDataURL('image/jpeg', 0.8)
        editProfileForm.value.profile_photo = dataUrl
      }
      img.src = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

// Posts
const showPostModal = ref(false)
const myPostFilter = ref('all')
const newPost = ref({
  description: '',
  type: 'offer',
  skill_id: '',
  mode: 'online',
  availability_id: ''
})

// Profile View
const showProfileModal = ref(false)
const viewedProfile = ref(null)

const viewProfile = async (id) => {
  if (!id) return
  const res = await store.fetchUserProfile(id)
  if (res.success) {
    viewedProfile.value = res.data
    showProfileModal.value = true
  }
}

// Skills & Avails form states
const newSkill = ref({ id: '', type: 'strong' })
const newAvail = ref({ day_of_week: 'Monday', start_time: '', end_time: '' })

// Chat
const chatInput = ref('')

const userStrongSkills = computed(() => store.user?.skills?.filter(s => s.proficiency === 'strong') || [])
const userWeakSkills = computed(() => store.user?.skills?.filter(s => s.proficiency === 'weak') || [])

const myPosts = computed(() => store.posts.filter(p => p.user_id === store.user?.id))

const filteredMyPosts = computed(() => {
  if (myPostFilter.value === 'all') return myPosts.value
  return myPosts.value.filter(p => p.type === myPostFilter.value)
})

// Explore Filters
const exploreSearch = ref('')
const exploreType = ref('all')
const exploreSkillId = ref('')
const directMessageLoading = ref(null)

const isPostCompatible = (post) => {
  if (post.type === 'offer') {
    return userWeakSkills.value.some(s => s.skill_id === post.skill_id)
  } else if (post.type === 'request') {
    return userStrongSkills.value.some(s => s.skill_id === post.skill_id)
  }
  return false
}

const showMessageModal = ref(false)
const selectedPostForMessage = ref(null)
const messageContent = ref('')
const isSendingDirectMessage = ref(false)

const openDirectMessage = (post) => {
  selectedPostForMessage.value = post
  messageContent.value = ''
  showMessageModal.value = true
}

const cancelDirectMessage = () => {
  showMessageModal.value = false
  selectedPostForMessage.value = null
  messageContent.value = ''
}

const confirmSendDirectMessage = async () => {
  if (!messageContent.value.trim() || !selectedPostForMessage.value) return
  
  const post = selectedPostForMessage.value
  isSendingDirectMessage.value = true
  directMessageLoading.value = post.id
  
  const res = await store.sendDirectMessage(post.user_id, messageContent.value.trim(), post.skill_id)
  
  isSendingDirectMessage.value = false
  directMessageLoading.value = null
  showMessageModal.value = false
  
  if (res.success) {
    alert("Message envoyé avec succès ! La conversation a été créée dans l'onglet Messagerie.")
  } else {
    alert("Erreur lors de l'envoi du message.")
  }
}

const explorePosts = computed(() => {
  return store.posts.filter(p => {
    // Ne pas afficher ses propres posts
    if (p.user_id === store.user?.id) return false
    
    // Ne pas afficher les posts des utilisateurs avec qui on a déjà une conversation
    const hasConversation = store.conversations.some(c => c.other_user?.id === p.user_id)
    return !hasConversation
  })
})

const filteredExplorePosts = computed(() => {
  return explorePosts.value.filter(post => {
    // text search
    if (exploreSearch.value) {
      const searchLower = exploreSearch.value.toLowerCase()
      const matchText = (post.description || '').toLowerCase().includes(searchLower) ||
                        (post.user?.first_name || '').toLowerCase().includes(searchLower) ||
                        (post.user?.last_name || '').toLowerCase().includes(searchLower) ||
                        (post.skill?.name || '').toLowerCase().includes(searchLower)
      if (!matchText) return false
    }
    // type filter
    if (exploreType.value !== 'all' && post.type !== exploreType.value) return false
    
    // skill filter
    if (exploreSkillId.value && post.skill_id !== exploreSkillId.value) return false
    
    return true
  })
})

const pendingMatches = computed(() => store.matches.filter(m => m.status === 'pending'))
const historyMatches = computed(() => store.matches.filter(m => m.status !== 'pending'))

const pendingMatchesCount = computed(() => pendingMatches.value.length)
const acceptedMatchesCount = computed(() => store.matches.filter(m => m.status === 'accepted').length)

const activeConversationMessages = computed(() => {
  if (!store.activeConversationId) return []
  const conv = store.conversations.find(c => c.id === store.activeConversationId)
  return conv?.messages || []
})

const activeConversationPartner = computed(() => {
  if (!store.activeConversationId) return null
  const conv = store.conversations.find(c => c.id === store.activeConversationId)
  return conv?.other_user || null
})

const totalUnreadMessages = computed(() => {
  return store.conversations.reduce((total, conv) => total + (conv.unread_count || 0), 0)
})

const formatDay = (dayEn) => {
  const map = {
    'Monday': 'Lundi', 'Tuesday': 'Mardi', 'Wednesday': 'Mercredi',
    'Thursday': 'Jeudi', 'Friday': 'Vendredi', 'Saturday': 'Samedi', 'Sunday': 'Dimanche'
  }
  return map[dayEn] || dayEn
}

const getMatchAvailabilities = (match) => {
  if (match.offer_post_id) {
    const post = store.posts.find(p => p.id === match.offer_post_id)
    return post?.availabilities || []
  } else {
    // Profile direct
    if (mentorAvailabilitiesCache[match.mentor_id] === undefined) {
      fetchMentorAvailabilities(match.mentor_id)
      return []
    }
    return mentorAvailabilitiesCache[match.mentor_id] || []
  }
}

const mentorAvailabilitiesCache = reactive({})

const fetchMentorAvailabilities = async (mentorId) => {
  if (mentorAvailabilitiesCache[mentorId] !== undefined) return
  mentorAvailabilitiesCache[mentorId] = null // loading state
  const res = await store.fetchUserProfile(mentorId)
  if (res && res.success) {
    mentorAvailabilitiesCache[mentorId] = res.data.availabilities || []
  } else {
    mentorAvailabilitiesCache[mentorId] = []
  }
}

// Loading States
const isAddingSkill = ref(false)
const isAddingAvail = ref(false)
const isSubmittingPost = ref(false)
const isSendingMessage = ref(false)
const matchActionLoading = ref({})

const getInitials = (user) => {
  if (!user) return ''
  return (user.first_name?.[0] || '') + (user.last_name?.[0] || '')
}

const handleLogout = () => {
  store.logout()
  router.push('/login')
}

const handleAddSkill = async () => {
  if (newSkill.value.id) {
    isAddingSkill.value = true
    await store.addSkill(newSkill.value.id, newSkill.value.type)
    newSkill.value.id = ''
    isAddingSkill.value = false
  }
}

const handleAddAvailability = async () => {
  if (newAvail.value.start_time && newAvail.value.end_time) {
    isAddingAvail.value = true
    await store.addAvailability({...newAvail.value})
    newAvail.value.start_time = ''
    newAvail.value.end_time = ''
    isAddingAvail.value = false
  }
}

const submitPost = async () => {
  isSubmittingPost.value = true

  const postData = { ...newPost.value }
  if (postData.availability_id) {
    const av = store.user.availabilities.find(a => a.id === postData.availability_id)
    if (av) {
      postData.availabilities = [{ day_of_week: av.day_of_week, start_time: av.start_time, end_time: av.end_time }]
    }
    delete postData.availability_id
  }

  const res = await store.createPost(postData)
  isSubmittingPost.value = false
  if (res.success) {
    showPostModal.value = false
    newPost.value = { description: '', type: 'offer', skill_id: '', mode: 'online', availability_id: '' }
  } else {
    alert(res.message)
  }
}

const postActionLoading = ref(null)

const handleDeletePost = async (id) => {
  if (confirm("Êtes-vous sûr de vouloir supprimer ce post ?")) {
    postActionLoading.value = id
    await store.deletePost(id)
    postActionLoading.value = null
  }
}

const handleAcceptMatch = async (id) => {
  matchActionLoading.value[id] = 'accept'
  const res = await store.acceptMatch(id)
  matchActionLoading.value[id] = null

  if (res.success) {
    // Recharger les données pour avoir la conversation créée
    await store.fetchDashboardData()

    // Trouver la conversation liée à ce match et l'ouvrir
    const conv = store.conversations.find(c => c.match_id === id)
    if (conv) {
      await store.selectConversation(conv.id)
      store.activeTab = 'chat'
    } else {
      // La conversation n'est pas encore visible, basculer quand même vers chat
      store.activeTab = 'chat'
    }
  }
}

const handleRejectMatch = async (id) => {
  matchActionLoading.value[id] = 'reject'
  await store.rejectMatch(id)
  matchActionLoading.value[id] = null
}

const sendChat = async () => {
  if (chatInput.value.trim() && store.activeConversationId) {
    isSendingMessage.value = true
    await store.sendMessage(store.activeConversationId, chatInput.value)
    chatInput.value = ''
    isSendingMessage.value = false
  }
}
</script>