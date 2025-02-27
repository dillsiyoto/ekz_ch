function acceptCookies() {
    document.getElementById('cookie-banner').style.display = 'none';
    document.cookie = "cookiesAccepted=true; path=/; max-age=31536000";
}

function declineCookies() {
    document.getElementById('cookie-banner').style.display = 'none';
    alert("Вы отказались от использования cookie. Некоторые функции могут быть недоступны.");
}
