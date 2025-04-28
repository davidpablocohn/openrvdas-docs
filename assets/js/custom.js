document.addEventListener('DOMContentLoaded', function() {
  console.log('Updated collapsible navigation script loaded');

  // Find all nav__sub-title elements
  const navTitles = document.querySelectorAll('.nav__sub-title');

  navTitles.forEach(function(title) {
    // Remove any existing toggle indicators to prevent duplicates
    const existingToggles = title.querySelectorAll('.nav-toggle');
    existingToggles.forEach(toggle => toggle.remove());

    // Add new toggle indicator
    const toggle = document.createElement('span');
    toggle.className = 'nav-toggle';
    toggle.textContent = ' +';
    toggle.style.float = 'right';
    title.appendChild(toggle);

    // Get the UL that follows each nav__sub-title
    const submenu = title.nextElementSibling;

    // Add click handler to title
    title.onclick = function(event) {
      // Prevent event bubbling
      event.preventDefault();
      event.stopPropagation();

      // Toggle submenu visibility
      if (submenu && submenu.tagName === 'UL') {
        console.log('Toggling submenu for:', title.textContent.trim());

        if (submenu.style.display === 'none' || submenu.style.display === '') {
          // Expand menu
          submenu.style.display = 'block';
          toggle.textContent = ' −'; // Minus sign
          console.log('Expanded submenu');
        } else {
          // Collapse menu
          submenu.style.display = 'none';
          toggle.textContent = ' +'; // Plus sign
          console.log('Collapsed submenu');
        }
      }

      return false;
    };

    // Initially hide all submenus
    if (submenu && submenu.tagName === 'UL') {
      submenu.style.display = 'none';
    }

    // Add pointer cursor to indicate clickable
    title.style.cursor = 'pointer';
  });
});
