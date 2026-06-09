// ==================== MODULE DASHBOARD ====================
// Tableau de bord principal et sous-pages du profil utilisateur

function loadDashboardContent() {
    const container = document.getElementById('dashboardContent');
    if (!container) return;
    container.innerHTML = `
        <div class="page-header" style="text-align:left; margin-bottom:1.5rem;">
            <h1>Bonjour, Kofi 👋</h1>
            <p>Bienvenue sur ton tableau de bord MentorLink</p>
        </div>
        <div class="dash-grid">
            <div class="dash-card"><div class="dash-card-label">Matchs suggérés</div><div class="dash-card-value green">4</div></div>
            <div class="dash-card"><div class="dash-card-label">Messages non lus</div><div class="dash-card-value blue">2</div></div>
            <div class="dash-card"><div class="dash-card-label">Mes annonces</div><div class="dash-card-value">1</div></div>
            <div class="dash-card"><div class="dash-card-label">Heures de mentorat</div><div class="dash-card-value">6h</div></div>
        </div>

        <div class="filters-bar">
            <select class="filter-select" id="filterMatiere">
                <option value="">Toutes matières</option>
                <option>Algorithmique</option>
                <option>Python</option>
                <option>Maths</option>
            </select>
            <select class="filter-select" id="filterNiveau">
                <option value="">Tous niveaux</option>
                <option>L1</option><option>L2</option><option>L3</option>
            </select>
            <select class="filter-select" id="filterDispo">
                <option value="">Toutes dispo</option>
                <option>Weekend</option>
                <option>Soir</option>
            </select>
            <button class="btn btn-accent" onclick="alert('Filtres appliqués (simulation)')">Filtrer</button>
        </div>

        <h3>🎯 Meilleurs matchs pour toi</h3>
        <div class="match-list">
            <div class="match-card">
                <div class="avatar">AK</div>
                <div class="match-info">
                    <div class="match-name">Aïcha Kpènou · L3 GL</div>
                    <div class="match-meta">Disponible: Samedi après-midi</div>
                    <div class="match-tags">
                        <span class="match-tag">Algo</span>
                        <span class="match-tag">Maths</span>
                        <span class="match-tag">C++</span>
                    </div>
                </div>
                <div>
                    <span class="score-badge">92% Match</span><br>
                    <button class="btn btn-accent" style="margin-top:8px;" onclick="showPage('messenger')">Contacter</button>
                </div>
            </div>
            <div class="match-card">
                <div class="avatar">MB</div>
                <div class="match-info">
                    <div class="match-name">Moussa Bello · Master Cloud</div>
                    <div class="match-meta">Disponible: Soirs de semaine</div>
                    <div class="match-tags">
                        <span class="match-tag">Python</span>
                        <span class="match-tag">Architecture</span>
                    </div>
                </div>
                <div>
                    <span class="score-badge">78% Match</span><br>
                    <button class="btn btn-outline" style="margin-top:8px;" onclick="showPage('messenger')">Contacter</button>
                </div>
            </div>
        </div>

        <div style="display:flex; justify-content:space-between; align-items:center;">
            <h3>📋 Mes annonces</h3>
            <button class="btn btn-accent" onclick="showDashboardPage('editprofile')">+ Créer une demande</button>
        </div>
        <div class="announce-card">
            <div class="announce-header">
                <div class="announce-title">Besoin d'aide en Algorithmique</div>
                <span class="announce-type type-demand">Demande</span>
            </div>
            <p>Recherche un mentor pour les structures de données complexes (arbres binaires) pour mon examen.</p>
            <div class="match-meta">👁️ 42 vues · 💬 3 réponses · Publié il y a 2j</div>
            <div>
                <button class="btn btn-outline btn-sm" onclick="alert('Modifier la demande')">✏️ Modifier</button>
                <button class="btn btn-outline btn-sm" style="border-color:#ff6b6b;color:#ff6b6b;" onclick="alert('Demande supprimée')">🗑 Supprimer</button>
            </div>
        </div>
    `;
}

function showDashboardPage(page) {
    document.querySelectorAll('.sidebar-menu li a').forEach(a => a.classList.remove('active'));
    event.target.closest('a').classList.add('active');

    const container = document.getElementById('dashboardContent');

    if (page === 'profile') {
        container.innerHTML = `
            <div class="profile-header">
                <div class="avatar avatar-lg">KA</div>
                <div>
                    <h2>Kofi Adjovi</h2>
                    <p class="match-meta">L1 Génie Logiciel · IFRI</p>
                    <p>Passionné par le développement, je cherche à progresser en algorithmique</p>
                </div>
            </div>
            <div class="profile-section">
                <h3>✅ Matières fortes</h3>
                <div class="tags-group">
                    <span class="tag selected-strength">Python</span>
                    <span class="tag selected-strength">Web</span>
                    <span class="tag selected-strength">SQL</span>
                </div>
            </div>
            <div class="profile-section">
                <h3>📚 Matières faibles</h3>
                <div class="tags-group">
                    <span class="tag selected-weakness">Algorithmique</span>
                    <span class="tag selected-weakness">Maths</span>
                </div>
            </div>
            <div class="profile-section">
                <h3>🕐 Disponibilités</h3>
                <div class="dispo-grid">
                    <span class="dispo-tag">Lundi soir</span>
                    <span class="dispo-tag">Mercredi soir</span>
                    <span class="dispo-tag">Samedi matin</span>
                </div>
            </div>
            <button class="btn btn-outline" onclick="showDashboardPage('editprofile')">Modifier le profil</button>
        `;
    } else if (page === 'editprofile') {
        container.innerHTML = `
            <h3>Modifier mon profil</h3>
            <form class="profile-section">
                <div class="form-row">
                    <div class="form-group"><label>Nom</label><input value="Kofi"></div>
                    <div class="form-group"><label>Prénom</label><input value="Adjovi"></div>
                </div>
                <div class="form-group"><label>Email</label><input value="kofi@ifri.edu"></div>
                <div class="form-group"><label>Téléphone</label><input value="+229 01 XX XX XX"></div>
                <div class="form-row">
                    <div class="form-group"><label>Filière</label><select><option>GL</option><option>IA</option></select></div>
                    <div class="form-group"><label>Niveau</label><select><option>L1</option><option>L2</option></select></div>
                </div>
                <button class="btn btn-accent">Enregistrer les modifications</button>
            </form>
        `;
    } else if (page === 'competences') {
        container.innerHTML = `
            <h3>Mes compétences</h3>
            <div class="profile-section">
                <h4>Matières où je peux aider (mentor)</h4>
                <div class="tags-group">
                    <span class="tag selected-strength">Python</span>
                    <span class="tag selected-strength">Web</span>
                    <span class="tag selected-strength">SQL</span>
                    <span class="tag">+ Ajouter</span>
                </div>
            </div>
            <div class="profile-section">
                <h4>Matières où j'ai besoin d'aide (mentoré)</h4>
                <div class="tags-group">
                    <span class="tag selected-weakness">Algorithmique</span>
                    <span class="tag selected-weakness">Maths</span>
                    <span class="tag">+ Ajouter</span>
                </div>
            </div>
        `;
    } else if (page === 'disponibilites') {
        container.innerHTML = `
            <h3>Mes disponibilités horaires</h3>
            <div class="profile-section">
                <div class="tags-group">
                    <span class="dispo-tag">Lundi 18h-20h</span>
                    <span class="dispo-tag">Mardi 14h-16h</span>
                    <span class="dispo-tag">Mercredi 18h-20h</span>
                    <span class="dispo-tag">Samedi 10h-12h</span>
                    <span class="dispo-tag">Dimanche 15h-17h</span>
                </div>
                <button class="btn btn-accent mt-3">Sauvegarder</button>
            </div>
        `;
    } else if (page === 'photo') {
        container.innerHTML = `
            <div class="profile-section">
                <h3>Photo de profil</h3>
                <div class="avatar avatar-lg" style="margin-bottom:1rem;">KA</div>
                <input type="file" accept="image/*">
                <button class="btn btn-accent mt-3">Télécharger</button>
            </div>
        `;
    } else if (page === 'settings') {
        container.innerHTML = `
            <div class="profile-section">
                <h3>Paramètres du compte</h3>
                <div class="form-group"><label><input type="checkbox"> Notifications par email</label></div>
                <div class="form-group"><label><input type="checkbox"> Notifications push</label></div>
                <div class="form-group">
                    <label>Langue</label>
                    <select><option>Français</option><option>English</option></select>
                </div>
                <button class="btn btn-danger">Désactiver mon compte</button>
            </div>
        `;
    } else {
        loadDashboardContent();
    }
}