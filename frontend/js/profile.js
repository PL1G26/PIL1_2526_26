// ==================== MODULE PROFIL PUBLIC ====================
// Affichage de la fiche publique d'un utilisateur

function loadPublicProfile() {
    const container = document.getElementById('publicProfileContent');
    if (!container) return;

    container.innerHTML = `
        <div class="profile-header">
            <div class="avatar avatar-lg">KA</div>
            <div>
                <h2>Kofi Adjovi</h2>
                <p class="match-meta">L1 Génie Logiciel · IFRI</p>
                <div class="match-tags">
                    <span class="match-tag">Python</span>
                    <span class="match-tag">Web</span>
                </div>
            </div>
        </div>
        <div class="profile-section">
            <h3>👋 Bio</h3>
            <p>Passionné par le développement, je cherche à progresser en algorithmique.</p>
        </div>
        <div class="profile-section">
            <h3>🎯 Recherche aide en</h3>
            <div class="tags-group">
                <span class="tag selected-weakness">Algorithmique</span>
                <span class="tag selected-weakness">Maths</span>
            </div>
        </div>
        <button class="btn btn-accent" onclick="showPage('messenger')">Contacter</button>
    `;
}