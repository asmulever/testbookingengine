(function () {
    function getCookie(name) {
        var value = "; " + document.cookie;
        var parts = value.split("; " + name + "=");
        if (parts.length === 2) return parts.pop().split(";").shift();
        return null;
    }

    function setCookie(name, value, days) {
        var maxAge = days * 24 * 60 * 60;
        document.cookie = name + "=" + value + "; path=/; max-age=" + maxAge + "; SameSite=Lax";
    }

    function applyTheme(theme) {
        document.documentElement.setAttribute("data-theme", theme);
        var icon = document.getElementById("theme-toggle-icon");
        if (!icon) return;

        if (theme === "dark") {
            icon.classList.remove("bi-sun-fill");
            icon.classList.add("bi-moon-stars-fill");
        } else {
            icon.classList.remove("bi-moon-stars-fill");
            icon.classList.add("bi-sun-fill");
        }
    }

    function initThemeToggle() {
        var button = document.getElementById("theme-toggle-btn");
        var currentTheme = document.documentElement.getAttribute("data-theme") || getCookie("theme_mode") || "light";
        applyTheme(currentTheme);

        if (!button) return;
        button.addEventListener("click", function () {
            var activeTheme = document.documentElement.getAttribute("data-theme") || "light";
            var nextTheme = activeTheme === "dark" ? "light" : "dark";
            applyTheme(nextTheme);
            setCookie("theme_mode", nextTheme, 365);
        });
    }

    document.addEventListener("DOMContentLoaded", initThemeToggle);
})();
