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
     * Add dataset description
     */
    $('.userBody').on('click', '.addDescrip', function (e) {
        e.preventDefault();
        if ($(this).prev().attr('class') === 'datasetDescrip') {
            $(this).next().find('.datasetDescripBox').text($(this).prev().text());
            $(this).prev().hide();
        }
        $(this).hide().next().hide().slideDown()
    });

    // Show dataset description or addDescription div on cancel
    $('.userBody').on('click', '.cancelDescrip', function () {
        $closestForm = $(this).closest('.descripForm');
        $closestForm.slideUp();
        $closestForm.prev().slideDown();
        if ($closestForm.prev().prev().attr('class') === 'datasetDescrip') {
            $closestForm.prev().prev().slideDown();
        }
    });

    // Save description to database and return results
    $('.userBody').on('click', '.saveDescrip', function () {
        datasetID = $(this).closest('.datasetDiv').attr('id').match(/\d+/).toString();
        $(this).closest('.descripForm').submit('submit', function (e) {
            e.preventDefault();
            $.post({
                url: '/datasetdescription/' + datasetID,
                data: $(this).serialize(),
                error: function (response, error) {
                    console.log(error);
                },
                success: function (data) {
                    console.log(data);
                    var $updatedDataset = $('#' + data.datasetFormID);

                    // Initiate new add descriptor object depending on if description is empty or not
                    if (data.datasetDescrip === '') {
                        var $addDescripHead = $('<a/>', {'class': 'text-dark addDescrip', 'href': ""}).append(
                            '<span class="font-weight-bold">Add Description</span>',
                            ' <i class="fas fa-pencil-alt"></i>'
                        ).hide();
                        $updatedDataset.find('.addDescrip').replaceWith($addDescripHead);
                        $updatedDataset.find('.datasetDescrip').empty().hide();
                    } else {
                        var $datasetDescrip = $('<span/>', {
                            'class': 'datasetDescrip', 'text': data.datasetDescrip
                        }).hide();
                        var $addDescripIcon = $('<a/>', {'class': 'text-muted addDescrip', 'href': ""}).append(
                            ' <i class="fas fa-pencil-alt"></i>'
                        ).hide();
                        $updatedDataset.find('.addDescrip').replaceWith($addDescripIcon);
                        if($updatedDataset.find('.datasetDescrip').length) {
                            $updatedDataset.find('.datasetDescrip').replaceWith($datasetDescrip)
                        } else {
                            $updatedDataset.find('.addDescrip').before($datasetDescrip);
                        }
                        $updatedDataset.find('.datasetDescrip').show();
                    }

                    $updatedDataset.find('.descripForm').hide();
                    $updatedDataset.find('.addDescrip').show();
                }
            })
        })
    });


    /**
     * Add toggle to dataset variables
     */
    $('.userBody').on('click', '.varsToggle', function () {
        $(this).toggleClass('font-weight-bold');
        $(this).next().toggle();
        $(this).find('i').toggleClass('fa-arrow-alt-circle-right fa-arrow-alt-circle-down');
        $(this).children('.varInfoIcon').toggleClass('fa-plus fa-minus')
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
