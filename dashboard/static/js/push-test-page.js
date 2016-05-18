navigator.serviceWorker.register('/static/js/service-worker.js')
.then(function(registration) {
    'use strict';
    return registration.pushManager.getSubscription()
    .then(function(subscription) {
        if (subscription) {
            return subscription;
        }
        return registration.pushManager.subscribe({ userVisibleOnly: true });
    });
}).then(function(subscription) {
    'use strict';
    // Show subscription object for selenium test to parse into pywebpush
    document.getElementById('subscription_json').textContent = JSON.stringify(subscription);
});
