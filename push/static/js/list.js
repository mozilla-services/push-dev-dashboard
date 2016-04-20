(function(win, doc, $) {
    'use strict';

    $('.add-app-btn').on('click', function(e) {
        dashboard.analytics.trackEvent({
            category: 'Push Applications',
            action: 'Add'
        });
    });

})(window, document, jQuery);
