$(document).ready(function () {


    /**
     * Add dataset description
     */
    $('.userBody').on('click', '.addDescrip', function (e) {
        e.preventDefault();
        if ($(this).prev().hasClass('datasetDescrip')) {
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
        if ($closestForm.prev().prev().hasClass('datasetDescrip')) {
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
                            'class': 'font-weight-bold datasetDescrip', 'text': data.datasetDescrip
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
