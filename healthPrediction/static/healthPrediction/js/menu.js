document.addEventListener('DOMContentLoaded', function() {
    var menuTrigger = document.querySelector('.menu-trigger');
    var dropdownMenu = document.querySelector('.dropdown-menu');

    menuTrigger.addEventListener('click', function() {
        dropdownMenu.classList.toggle('active');
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!menuTrigger.contains(e.target) && !dropdownMenu.contains(e.target)) {
            dropdownMenu.classList.remove('active');
        }
    });

    // Ensure menu closes on window resize
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            dropdownMenu.classList.remove('active');
        }
    });
});
