document.addEventListener('DOMContentLoaded', function() {
  console.log('Fixed collapsible menu script');

  // Find all navigation section titles
  const sectionTitles = document.querySelectorAll('.nav__sub-title');

  // First, remove any existing toggle indicators to avoid duplicates
  document.querySelectorAll('.nav-toggle').forEach(function(toggle) {
    toggle.remove();
  });

  // Process each section
  sectionTitles.forEach(function(title) {
    // Add toggle indicator
    const toggle = document.createElement('span');
    toggle.className = 'nav-toggle';
    toggle.textContent = ' +';
    toggle.style.float = 'right';
    title.appendChild(toggle);

    // Get the submenu
    const submenu = title.nextElementSibling;
    if (!submenu || submenu.tagName !== 'UL') return;

    // Check if this menu contains the active page
    const isActive = submenu.querySelector('a.active') !== null;

    // Set initial state
    if (isActive) {
      // Keep the active section's menu expanded
      submenu.style.display = 'block';
      toggle.textContent = ' −'; // Minus sign
    } else {
      // Collapse non-active sections
      submenu.style.display = 'none';
    }

    // Make the title look clickable
    title.style.cursor = 'pointer';

    // Add click handler directly to the title element
    title.onclick = function() {
      if (submenu.style.display === 'none' || submenu.style.display === '') {
        submenu.style.display = 'block';
        toggle.textContent = ' −'; // Minus sign
      } else {
        submenu.style.display = 'none';
        toggle.textContent = ' +'; // Plus sign
      }
      return false;
    };
  });
});
