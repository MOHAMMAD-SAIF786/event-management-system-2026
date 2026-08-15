/* ========================================================
   ROYAL EVENTS - NAVBAR & MOBILE DRAWER ENGINE
   ======================================================== */

const menuToggle = document.getElementById("menuToggle");
const navMenu = document.getElementById("navMenu");
const navCheck = document.getElementById("nav-check");
const navBackdrop = document.getElementById("navBackdrop");
const header = document.getElementById("header");

function updateMenuIcon(isOpen) {
    if (menuToggle) {
        menuToggle.innerHTML = isOpen
            ? '<i class="fa-solid fa-xmark"></i>'
            : '<i class="fa-solid fa-bars"></i>';
        menuToggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
    }
}

function openMobileMenu() {
    if (navCheck) navCheck.checked = true;
    if (navMenu) navMenu.classList.add("active");
    if (navBackdrop) navBackdrop.classList.add("active");
    updateMenuIcon(true);
    document.body.style.overflow = "hidden";
}

function closeMobileMenu() {
    if (navCheck) navCheck.checked = false;
    if (navMenu) navMenu.classList.remove("active");
    if (navBackdrop) navBackdrop.classList.remove("active");
    updateMenuIcon(false);
    document.body.style.overflow = "";
}

function isMobileMenuOpen() {
    return (navCheck && navCheck.checked) || (navMenu && navMenu.classList.contains("active"));
}

if (menuToggle && navMenu) {
    // 1. Menu toggle button click
    menuToggle.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (isMobileMenuOpen()) {
            closeMobileMenu();
        } else {
            openMobileMenu();
        }
    });

    // 2. Close button in drawer header
    const closeBtn = document.querySelector(".menu-close-btn");
    if (closeBtn) {
        closeBtn.addEventListener("click", (e) => {
            e.preventDefault();
            e.stopPropagation();
            closeMobileMenu();
        });
    }

    // 3. Backdrop click to dismiss
    if (navBackdrop) {
        navBackdrop.addEventListener("click", () => {
            closeMobileMenu();
        });
    }

    // 4. Checkbox change sync
    if (navCheck) {
        navCheck.addEventListener("change", () => {
            if (navCheck.checked) {
                openMobileMenu();
            } else {
                closeMobileMenu();
            }
        });
    }

    // 5. Dropdown trigger on mobile (Services)
    const dropdowns = document.querySelectorAll(".dropdown");
    dropdowns.forEach(drop => {
        const trigger = drop.querySelector(".dropdown-trigger, > a");
        if (trigger) {
            trigger.addEventListener("click", function (e) {
                if (window.innerWidth <= 991) {
                    e.preventDefault();
                    e.stopPropagation();
                    const wasActive = drop.classList.contains("active");
                    
                    if (wasActive) {
                        drop.classList.remove("active");
                        trigger.setAttribute("aria-expanded", "false");
                    } else {
                        drop.classList.add("active");
                        trigger.setAttribute("aria-expanded", "true");
                    }
                }
            });
        }
    });

    // 6. Close menu when navigating via actual destination links (never on dropdown toggle)
    document.querySelectorAll(".nav-menu a").forEach(link => {
        link.addEventListener("click", (e) => {
            const href = link.getAttribute("href");
            if (link.classList.contains("dropdown-trigger") || href === "javascript:void(0)" || href === "#" || !href) {
                return;
            }
            if (window.innerWidth <= 991) {
                closeMobileMenu();
            }
        });
    });

    // 7. Close on Escape key
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && isMobileMenuOpen()) {
            closeMobileMenu();
        }
    });

    // 8. Auto-reset when resizing to desktop viewport
    window.addEventListener("resize", () => {
        if (window.innerWidth > 991 && isMobileMenuOpen()) {
            closeMobileMenu();
        }
    });
}

// Header Shadow on Scroll
if (header) {
    window.addEventListener("scroll", () => {
        if (window.scrollY > 50) {
            header.classList.add("scrolled");
        } else {
            header.classList.remove("scrolled");
        }
    });
}

document.addEventListener("DOMContentLoaded", () => {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll(".nav-menu > li > a");

    navLinks.forEach(link => {
        const href = link.getAttribute("href");
        if (!href || href === "javascript:void(0)") return;

        link.classList.remove("active");

        if (href === "/" && (currentPath === "/" || currentPath === "")) {
            link.classList.add("active");
        } else if (href !== "/") {
            const cleanHref = href.split("?")[0].replace(/\/$/, "");
            const cleanPath = currentPath.replace(/\/$/, "");
            if (cleanPath === cleanHref || (cleanHref.length > 1 && cleanPath.startsWith(cleanHref))) {
                link.classList.add("active");
            }
        }
    });

    // User profile dropdown click toggle & click outside
    const userMenuDropdown = document.querySelector(".user-menu-dropdown");
    if (userMenuDropdown) {
        const userMenuBtn = userMenuDropdown.querySelector(".user-menu-btn");
        if (userMenuBtn) {
            userMenuBtn.addEventListener("click", (e) => {
                e.stopPropagation();
                userMenuDropdown.classList.toggle("active");
            });
        }

        document.addEventListener("click", (e) => {
            if (!userMenuDropdown.contains(e.target)) {
                userMenuDropdown.classList.remove("active");
            }
        });
    }
});