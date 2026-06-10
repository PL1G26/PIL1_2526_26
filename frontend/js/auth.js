// ==================== MODULE AUTHENTIFICATION ====================
// Gestion des formulaires : connexion, inscription, mot de passe oublié,
// réinitialisation, contact et FAQ accordéon

document.addEventListener('DOMContentLoaded', function () {

    // --- Connexion ---
    document.getElementById('loginForm')?.addEventListener('submit', (e) => {
        e.preventDefault();
        showPage('dashboard');
    });

    // --- Inscription ---
    document.getElementById('registerForm')?.addEventListener('submit', (e) => {
        e.preventDefault();
        showPage('dashboard');
    });

    // --- Mot de passe oublié ---
    document.getElementById('forgotForm')?.addEventListener('submit', (e) => {
        e.preventDefault();
        alert('Email de réinitialisation envoyé');
        showPage('login');
    });

    // --- Réinitialisation du mot de passe ---
    document.getElementById('resetForm')?.addEventListener('submit', (e) => {
        e.preventDefault();
        alert('Mot de passe réinitialisé');
        showPage('login');
    });

    // --- Formulaire de contact ---
    document.getElementById('contactForm')?.addEventListener('submit', (e) => {
        e.preventDefault();
        alert('Message envoyé !');
    });

    // --- FAQ accordéon ---
    document.querySelectorAll('.faq-question').forEach(q => {
        q.addEventListener('click', () => q.parentElement.classList.toggle('open'));
    });

});