(function(win, doc, $) {
    'use strict';

    // When the page loads, select the vapid key token, so the user can easily
    // copy it.
    // TODO: https://github.com/mozilla-services/push-dev-dashboard/issues/182
    // for code that could potentially add a "copy-to-clipboard" button
    $('#vapid-key-token').select();

})(window, document, jQuery);
