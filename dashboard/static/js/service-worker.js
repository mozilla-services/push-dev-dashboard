self.addEventListener('push', function(event) {
    'use strict'
    event.waitUntil(
        self.registration.showNotification('Push Test Page', {
            body: 'Test push message'
        })
    );
});
