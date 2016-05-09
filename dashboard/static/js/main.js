$(document).foundation();
window.dashboard = {
    features: {}
};
(function(win) {
    'use strict'
    win.dashboard.features.localStorage = (function() {
        var uid = Date();
        var result;
        try {
            localStorage.setItem(uid, uid);
            result = localStorage.getItem(uid) === uid;
            localStorage.removeItem(uid);
            return result;
        } catch (exception) {
            return false;
        }
    }());
})(window);
