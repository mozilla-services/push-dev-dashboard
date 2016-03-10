(function(win, doc, $) {
    'use strict';

    $('.sign-in-btn').on('click', function(e) {
        dashboard.analytics.trackEvent({
            category: 'Sign in',
            action: 'click',
            label: e.target.text
        });
    });

})(window, document, jQuery);
