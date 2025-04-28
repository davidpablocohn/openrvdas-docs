$(document).ready(function() {
  // Hide all child menus initially
  $('.nav__sub-title + .nav__items').hide();
  
  // Add click event to parent items
  $('.nav__sub-title').click(function() {
    $(this).next('.nav__items').slideToggle(300);
  });
});
