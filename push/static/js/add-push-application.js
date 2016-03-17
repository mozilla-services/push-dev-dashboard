function formSubmit(e) {
    'use strict';

    e.preventDefault();
    var $form = $(this);
    var csrf_token = $form.find('input[name=csrfmiddlewaretoken]').val();
    var api_call = $.ajax({
        url: $form.attr('action'),
        method: $form.attr('method'),
        data: $form.serialize(),
        processData: false,
        headers: {
            'X-CSRFToken': csrf_token
        },
        contentType: 'application/x-www-form-urlencoded; charset=UTF-8'
    });

    api_call.fail(function(jqXHR) {
        $.each(jqXHR.responseJSON, function(index, element) {
            $('#id_' + index).after('<div class="alert callout">' + element + '</div>');
        });
    });

    api_call.success(function() {
        window.location.reload();
    });
}

$(document).ready(function() {
    'use strict';

    $('form').submit(formSubmit);
});
