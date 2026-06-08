// Dark mode
function toggleDark() {
  const html = document.documentElement;
  const isDark = html.getAttribute('data-theme') === 'dark';
  html.setAttribute('data-theme', isDark ? 'light' : 'dark');
  document.getElementById('dark-btn').textContent = isDark ? '🌙' : '☀️';
  localStorage.setItem('skit_theme', isDark ? 'light' : 'dark');
}

// Restore theme on load
(function () {
  const saved = localStorage.getItem('skit_theme');
  if (saved === 'dark') {
    document.documentElement.setAttribute('data-theme', 'dark');
    const btn = document.getElementById('dark-btn');
    if (btn) btn.textContent = '☀️';
  }
})();

// Auto-dismiss flash messages after 4s
setTimeout(() => {
  document.querySelectorAll('.flash').forEach(el => el.remove());
}, 4000);
