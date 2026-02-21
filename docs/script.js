
document.addEventListener('DOMContentLoaded', () => {

    // Sidebar Navigation Logic
    const navItems = document.querySelectorAll('.nav-item');
    const sections = document.querySelectorAll('.book-section');

    function activateSection(targetId) {
        // Deactivate all
        sections.forEach(sec => sec.classList.remove('active'));
        navItems.forEach(item => item.classList.remove('active'));

        // Activate target
        const targetSection = document.getElementById(targetId);
        const targetNav = document.querySelector(`.nav-item[data-target="${targetId}"]`);

        if (targetSection) {
            targetSection.classList.add('active');
            // Scroll to top of content
            document.querySelector('.content').scrollTop = 0;
        }

        if (targetNav) {
            targetNav.classList.add('active');
        }

        // Close sidebar on mobile after clicking a link
        if (window.innerWidth <= 768) {
            closeSidebar();
        }
    }

    // Mobile Sidebar Toggle Logic
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');

    function openSidebar() {
        sidebar.classList.add('open');
        overlay.classList.add('open');
    }

    function closeSidebar() {
        sidebar.classList.remove('open');
        overlay.classList.remove('open');
    }

    if (menuToggle && sidebar && overlay) {
        menuToggle.addEventListener('click', openSidebar);
        overlay.addEventListener('click', closeSidebar);
    }

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const targetId = item.getAttribute('data-target');
            activateSection(targetId);
        });
    });

    // Dark Mode Toggle
    const toggle = document.createElement('button');
    toggle.textContent = '🌙';
    toggle.className = 'theme-toggle';
    // Style directly or add to CSS
    Object.assign(toggle.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '10px 15px',
        borderRadius: '20px',
        border: 'none',
        background: '#34495e',
        color: '#fff',
        cursor: 'pointer',
        boxShadow: '0 2px 5px rgba(0,0,0,0.2)',
        zIndex: 1000
    });

    toggle.addEventListener('click', () => {
        document.body.classList.toggle('dark-mode');
        const isDark = document.body.classList.contains('dark-mode');

        if (isDark) {
            toggle.textContent = '☀️';
            // Simple Dark Mode injection
            document.documentElement.style.setProperty('--bg-color', '#1a1a1a');
            document.documentElement.style.setProperty('--text-color', '#ecf0f1');
            document.querySelector('.content').style.background = '#1a1a1a';
            document.querySelector('.sidebar').style.background = '#000';

            // Fix text colors in stanza
            document.querySelectorAll('.stanza-col:last-child').forEach(el => el.style.color = '#bdc3c7');
        } else {
            toggle.textContent = '🌙';
            document.documentElement.style.removeProperty('--bg-color');
            document.documentElement.style.removeProperty('--text-color');
            document.querySelector('.content').style.background = '';
            document.querySelector('.sidebar').style.background = '';

            document.querySelectorAll('.stanza-col:last-child').forEach(el => el.style.color = '');
        }
    });

    document.body.appendChild(toggle);

    // Auto-activate first section if none active (fallback)
    if (!document.querySelector('.book-section.active') && sections.length > 0) {
        sections[0].classList.add('active');
        if (navItems.length > 0) navItems[0].classList.add('active');
    }
});
