$(document).ready(function () {


    $.ajaxSetup({
        headers: {
            'X-CSRF-TOKEN': $('meta[name="csrf-token"]').attr('content')
        }
    });

    /*
     * Delete dataset
     */
    $('body').on('click', '.deleteBtn', function (e) {
        e.preventDefault();
        console.log($(this).parent().val());
        $.post({
            url: window.location.pathname + "/destroy/" + $(this).parent().val(),
            success: function (response) {
                console.log(response);
                $('#dataset_' + response.id).fadeOut(500, function () {
                    $(this).remove();
                    if (!$(".newDataset")[0] && !$(".oldDataset")[0]) {
                        if ($('#noDataset')[0]) {
                            $('#noDataset').slideDown(500);
                        } else {
                            $('<h4 id="noDataset">No datasets uploaded</h4>').hide().insertAfter('#userDataH2').slideDown(500);
                        }
                    }
                });

            },
            error: function () {
                console.log("Fail!");
            }
        });
    });


});
