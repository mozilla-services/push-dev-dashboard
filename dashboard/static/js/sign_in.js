(function(win, doc, $) {
    'use strict';

    $('.sign-in-btn').on('click', function(e) {
        dashboard.analytics.trackEvent({
            category: 'Auth',
            action: 'Started sign-in',
            label: e.target.text
        });
    });

    if (win.dashboard.features.localStorage) (function() {
        var key = 'authenticated';
        var authStoredValue = localStorage.getItem(key);
        var authCurrentValue = $(doc.body).data(key);
        try {
            // User just logged in
            if (authCurrentValue && !authStoredValue) {
                localStorage.setItem(key, authCurrentValue);
                dashboard.analytics.trackEvent({
                    category: 'Auth',
                    action: 'Finished sign-in'
                });
            }
            else if (!authCurrentValue && authStoredValue) {
                localStorage.removeItem(key);
                dashboard.analytics.trackEvent({
                    category: 'Auth',
                    action: 'Finished sign-out'
                });
            }
        }
        catch (e) {
            // Browser doesn't support localStorage
        }
    }());

    if (document.getElementById('sign-in-error')) (function() {
        dashboard.analytics.trackEvent({
            category: 'Auth',
            action: 'Error',
            label: $('#sign-in-error-text').text()
        });
    }());

})(window, document, jQuery);
