document.addEventListener("DOMContentLoaded", function () {
    const sidebar = document.querySelector(".sidebar");
    const menuBtn = document.getElementById("menuBtn");
    const sidebarCloseBtn = document.getElementById("sidebarCloseBtn");
    const sidebarOverlay = document.getElementById("sidebarOverlay");

    function openMobileSidebar() {
        if (sidebar) sidebar.classList.add("active");
        if (sidebarOverlay) sidebarOverlay.classList.add("active");
        document.body.style.overflow = "hidden";
    }

    function closeMobileSidebar() {
        if (sidebar) sidebar.classList.remove("active");
        if (sidebarOverlay) sidebarOverlay.classList.remove("active");
        document.body.style.overflow = "";
    }

    if (menuBtn) {
        menuBtn.addEventListener("click", function (e) {
            e.stopPropagation();
            if (window.innerWidth <= 768) {
                if (sidebar && sidebar.classList.contains("active")) {
                    closeMobileSidebar();
                } else {
                    openMobileSidebar();
                }
            } else {
                if (sidebar) sidebar.classList.toggle("collapsed");
            }
        });
    }

    if (sidebarCloseBtn) {
        sidebarCloseBtn.addEventListener("click", function (e) {
            e.stopPropagation();
            closeMobileSidebar();
        });
    }

    if (sidebarOverlay) {
        sidebarOverlay.addEventListener("click", function () {
            closeMobileSidebar();
        });
    }

    // Auto close sidebar on nav link click in mobile view
    const menuLinks = document.querySelectorAll(".sidebar .menu li a, .sidebar .logout a");
    menuLinks.forEach(function (link) {
        link.addEventListener("click", function () {
            if (window.innerWidth <= 768) {
                closeMobileSidebar();
            }
        });
    });

    window.addEventListener("resize", function () {
        if (window.innerWidth > 768) {
            closeMobileSidebar();
        }
    });
});