let alias = jQuery.noConflict();

var site_theme = (localStorage.getItem('theme') != null)
    ? localStorage.getItem('theme')
    : 'light';

function toggle_theme(_theme) {
    if (_theme === "dark") {
        alias('body').attr("data-bs-theme", "dark")
        alias('#btn-theme').html("<i class=\"bi bi-sun-fill\"></i>")
        alias('#btn-theme').attr("onclick", "toggle_theme('light')")
        alias('#source-code-css').attr("href", "https://github.coventry.ac.uk/pages/ab6459/CUEH_Slides/js/custom/styles/atom-one-dark.css")

        alias('.slide-background .title-slide .slide-background-content').each(function() {
            let bgImage = alias(this).css("background-image");
            if (bgImage) {
                let newBgImage = bgImage.replace("light", "dark");
                alias(this).css("background-image", newBgImage);
            }
        })

    } else {
        alias('body').attr("data-bs-theme", "light")
        alias('#btn-theme').html("<i class=\"bi bi-moon-fill\"></i>")
        alias('#btn-theme').attr("onclick", "toggle_theme('dark')")
        alias('#source-code-css').attr("href", "https://github.coventry.ac.uk/pages/ab6459/CUEH_Slides/js/custom/styles/atom-one-light.css")

        alias('.slide-background .title-slide .slide-background-content').each(function() {
            let bgImage = alias(this).css("background-image");
            if (bgImage) {
                let newBgImage = bgImage.replace("dark", "light");
                alias(this).css("background-image", newBgImage);
            }
        })


    }
    localStorage.setItem('theme', _theme);
}

alias(document).ready(function () {
    toggle_theme(site_theme)
})
