// ==================== MODULE MATCHING ====================
// Correspondances, historique, suggestions et publication d'annonces

function loadMatchingContent() {
    const container = document.getElementById('matchingContent');
    container.innerHTML = `
        <div class="page-header" style="text-align:left;">
            <h1>Matching</h1>
            <p>Résultats des correspondances basés sur ton profil</p>
        </div>

        <div class="filters-bar">
            <select class="filter-select"><option>Toutes matières</option></select>
            <select class="filter-select"><option>Tous niveaux</option></select>
            <select class="filter-select"><option>Toutes dispo</option></select>
            <button class="btn btn-accent">Filtrer</button>
        </div>

        <h3>🎯 Correspondances actives</h3>
        <div class="match-list">
            <div class="match-card">
                <div class="avatar">AK</div>
                <div class="match-info">
                    <div class="match-name">Aïcha Kpènou</div>
                    <div class="match-meta">L3 GL · Algo, Maths, C++</div>
                    <div class="match-tags">
                        <span class="match-tag">Mentor</span>
                        <span class="match-tag">Score: 92%</span>
                    </div>
                </div>
                <button class="btn btn-accent" onclick="showMatchDetail(1)">Voir détail</button>
            </div>
            <div class="match-card">
                <div class="avatar">MB</div>
                <div class="match-info">
                    <div class="match-name">Moussa Bello</div>
                    <div class="match-meta">Master Cloud · Python, Architecture</div>
                    <div class="match-tags">
                        <span class="match-tag">Mentor</span>
                        <span class="match-tag">Score: 78%</span>
                    </div>
                </div>
                <button class="btn btn-outline" onclick="showMatchDetail(2)">Voir détail</button>
            </div>
        </div>

        <h3>📊 Historique des correspondances</h3>
        <div class="match-list">
            <div class="match-card">
                <div class="match-info">
                    <div class="match-name">Jean K. (L2 RS)</div>
                    <div class="match-meta">Match du 15/05/2026 · Score: 68%</div>
                </div>
                <span class="score-badge">Terminé</span>
            </div>
        </div>

        <h3>💡 Suggestions automatiques</h3>
        <div class="announce-card">
            <p>Basé sur tes matières faibles, nous te suggérons de rejoindre le groupe d'étude "Algorithmique Avancée"</p>
            <button class="btn btn-outline">Rejoindre</button>
        </div>

        <h3>✏️ Publier une annonce</h3>
        <div class="publish-form">
            <div class="form-group">
                <select>
                    <option>Offre de mentorat (je veux aider)</option>
                    <option>Demande d'aide (je cherche un mentor)</option>
                </select>
            </div>
            <div class="form-group">
                <select>
                    <option>Sélectionner matière</option>
                    <option>Algorithmique</option>
                    <option>Python</option>
                </select>
            </div>
            <div class="form-group">
                <textarea placeholder="Description..."></textarea>
            </div>
            <button class="btn btn-accent">Publier</button>
        </div>
    `;
}

function showMatchDetail(matchId) {
    alert(`Détail du match #${matchId}\nScore de compatibilité: ${matchId === 1 ? '92%' : '78%'}\nBasé sur vos matières, disponibilités et objectifs communs.`);
}