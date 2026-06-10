// ==================== MODULE THÈME ====================
// Gestion du mode sombre / clair

function initTheme() {
    const savedTheme = localStorage.getItem('mentorlink-theme');
    const darkModeToggle = document.getElementById('darkModeToggle');

    if (savedTheme === 'light') {
        document.body.classList.add('light-mode');
        if (darkModeToggle) {
            darkModeToggle.innerHTML = '<i class="bi bi-sun-fill"></i>';
            darkModeToggle.setAttribute('title', 'Mode sombre');
        }
    } else {
        document.body.classList.remove('light-mode');
        if (darkModeToggle) {
            darkModeToggle.innerHTML = '<i class="bi bi-moon-fill"></i>';
            darkModeToggle.setAttribute('title', 'Mode clair');
        }
    }
}

function toggleTheme() {
    const isLightMode = document.body.classList.toggle('light-mode');
    const darkModeToggle = document.getElementById('darkModeToggle');

    if (isLightMode) {
        localStorage.setItem('mentorlink-theme', 'light');
        if (darkModeToggle) {
            darkModeToggle.innerHTML = '<i class="bi bi-sun-fill"></i>';
            darkModeToggle.setAttribute('title', 'Mode sombre');
        }
        showThemeToast('Mode clair activé ☀️');
    } else {
        localStorage.setItem('mentorlink-theme', 'dark');
        if (darkModeToggle) {
            darkModeToggle.innerHTML = '<i class="bi bi-moon-fill"></i>';
            darkModeToggle.setAttribute('title', 'Mode clair');
        }
        showThemeToast('Mode sombre activé 🌙');
    }
}

function showThemeToast(message) {
    const toast = document.createElement('div');
    toast.textContent = message;
    toast.style.position = 'fixed';
    toast.style.bottom = '20px';
    toast.style.right = '20px';
    toast.style.backgroundColor = 'var(--surface2)';
    toast.style.color = 'var(--accent)';
    toast.style.padding = '10px 20px';
    toast.style.borderRadius = '8px';
    toast.style.border = `1px solid var(--accent)`;
    toast.style.zIndex = '9999';
    toast.style.fontSize = '0.9rem';
    toast.style.backdropFilter = 'blur(10px)';
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 1500);
}

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function () {
    initTheme();
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (darkModeToggle) {
        darkModeToggle.removeEventListener('click', toggleTheme);
        darkModeToggle.addEventListener('click', toggleTheme);
    }
});