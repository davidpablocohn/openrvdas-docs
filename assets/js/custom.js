document.addEventListener('DOMContentLoaded', function() {
  // Hide all child menus initially
  const subMenus = document.querySelectorAll('.nav__sub-title + .nav__items');
  subMenus.forEach(menu => {
    menu.style.display = 'none';
  });

  // Add click event to parent items
  const parentItems = document.querySelectorAll('.nav__sub-title');
  parentItems.forEach(item => {
    item.addEventListener('click', function() {
      const subMenu = this.nextElementSibling;
      if (subMenu && subMenu.classList.contains('nav__items')) {
        if (subMenu.style.display === 'none' || subMenu.style.display === '') {
          subMenu.style.display = 'block';
        } else {
          subMenu.style.display = 'none';
        }
      }
    });
  });
});
