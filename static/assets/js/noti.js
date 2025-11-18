// script.js
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/static/assets/js/service-worker.js')
        .then(function(registration) {
            return registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: "BAXF-7oj9p-zx_UBeNNxy2482jRY478wwL6AvAFYp8MQlWcxJRAUObejt3s9uv80IGnyHjTEcXNX1D25QJJ2XFg"
            });
        })
        .then(function(subscription) {
            // ارسال subscription به سرور
            fetch('/notification/save_subscription/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')  // برای Django CSRF
                },
                body: JSON.stringify(subscription)
            });
        });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}