$(document).ready(function () {


      /**
     * Process to get csrf token in Django
     * @param name
     * @returns {*}
     */
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    var csrftoken = getCookie('csrftoken');

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });


    /**
     * Add toggle to dataset variables
     */
    $('.userBody').on('click', '.varsToggle', function () {
        $(this).next().toggle();
        $(this).find('i').toggleClass('fa-arrow-alt-circle-right fa-arrow-alt-circle-down')
    });


    /**
     * Delete user dataset
     */
    $('.userBody').on('click', '.deleteBtn', function () {
        $(this).parent().submit('submit', function (e) {
            e.preventDefault();
            $.post({
                url: $(this).attr('action'),
                error: function (response, error) {
                    console.log(error);
                },
                success: function (data) {
                    $('#dataset_' + data.id).fadeOut(500, function () {
                        $(this).remove();
                        if (!$(".oldDataset")[0]) {
                            if ($('#noDataset')[0]) {
                                $('#noDataset').slideDown(500);
                            } else {
                                $('<h4 id="noDataset">No datasets uploaded</h4>').hide().insertAfter('#userDataH2').slideDown(500);
                            }
                        }
                    });
                }
            });

        });
    });


});
