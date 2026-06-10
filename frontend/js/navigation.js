// ==================== MODULE NAVIGATION ====================
// Gestion du routing entre les pages et du menu mobile

function showPage(pageId) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    const targetPage = document.getElementById('page-' + pageId);
    if (targetPage) targetPage.classList.add('active');
    else document.getElementById('page-404').classList.add('active');

    window.scrollTo(0, 0);

    // Charger le contenu dynamique selon la page
    if (pageId === 'dashboard') loadDashboardContent();
    if (pageId === 'matching')  loadMatchingContent();
    if (pageId === 'messenger') loadMessengerContent();
    if (pageId === 'profile')   loadPublicProfile();
}

function toggleMobileMenu() {
    document.getElementById('navLinks').classList.toggle('active');
}