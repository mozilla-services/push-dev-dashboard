(function(win, doc, $) {
    'use strict';

    function createNode(text) {
        var node = document.createElement('pre');
        node.style.width = '1px';
        node.style.height = '1px';
        node.style.position = 'fixed';
        node.style.top = '5px';
        node.textContent = text;
        return node;
    }

    function copyNode(node) {
        var selection = getSelection();
        selection.removeAllRanges();

        var range = document.createRange();
        range.selectNodeContents(node);
        selection.addRange(range);

        document.execCommand('copy');
        selection.removeAllRanges();
    }

    function copyText(text) {
        var node = createNode(text);
        document.body.appendChild(node);
        copyNode(node);
        document.body.removeChild(node);
    }

    function copyInput(node) {
        node.select();
        document.execCommand('copy');
        getSelection().removeAllRanges();
    }

    function isFormInput(element) {
        return element.nodeName === 'INPUT' || element.nodeName === 'TEXTAREA';
    }

    $(document).on('click', '.js-copy-button', function() {
        var text;
        if ((text = this.getAttribute('data-clipboard-text')) !== null) {
            copyText(text);
        } else {
            var container = this.closest('.js-copy-container');
            var content = container.querySelector('.js-copy-target');
            if (isFormInput(content)) {
                if (content.type === 'hidden') {
                    copyText(content.value);
                } else {
                    copyInput(content);
                }
            } else {
                copyNode(content);
            }
        }
        this.blur();
    });
})(window, document, jQuery);
