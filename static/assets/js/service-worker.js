self.addEventListener('push', function(event) {
    const payload = event.data ? event.data.json() : {};
    const title = payload.title || 'Default Title';
    const options = {
        body: payload.body || 'Default Message',
        icon: '/static/assets/img/benzin.png',  // آیکون نوتیفیکیشن
        badge: '/static/assets/img/benzin.png'  // بج نوتیفیکیشن
    };
    event.waitUntil(self.registration.showNotification(title, options));
});