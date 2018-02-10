/**
 * Dropzone
 */
Dropzone.options.uploadData = {
    url: window.location.pathname,
    acceptedFiles: ".csv, .xlsx",
    maxFiles: 1,
    addRemoveLinks: true,
    init: function () {
        this.on('error', function (file, error) {
            $('.dz-error-message').children(':first').html(error.file)
        });
        this.on("success", function (file, data) {
            $('.dz-progress').hide();
            $('.dz-error-mark').hide();
            console.log(data);

            /**
             * Define longer new dataset elements
             */

            // new dataset card and card-header
            var $dataDiv = $('<div/>', {'id': 'dataset_' + data.pk, 'class': 'card border-dark datasetDiv'});
            var $dataHeader = $('<h4/>', {
                'class': 'card-header newDataset'
            }).append(
                '<i class="fas fa-table"></i> ' + data.name
            );

            // Add description ul
            var $descripUl = $('<ul/>', {'class': 'list-group list-group-flush'}).append(
                $('<li/>', {'class': 'list-group-item'}).append(
                    $('<a/>', {'class': 'text-dark addDescrip', 'href': ''}).append(
                        '<span class="font-weight-bold">Add Description</span>',
                        ' <i class="fas fa-pencil-alt"></i>'
                    ),
                    $('.descripForm').last().clone()
                )
            )

            // Make model button and clone hidden deleteUpload form
            var $dataButtons = $('<div/>', {'class': 'btn-toolbar'}).append(
                $('<a/>', {
                    'class': 'btn btn-dark buttonSpace',
                    'href': '/home/Clayton/dataset/' + data.pk,
                    'text': 'View Dataset'
                }),
                $('.deleteUpload').last().clone().attr({
                    'action': '/datasetdelete/' + data.pk
                }).css("visibility", "visible")
            );

            // Make card body
            var $dataBody = $('<div/>', {'class': 'card-body'}).append(
                $('<ul/>', {'class': 'list-unstyled'}).append(
                    '<li>Number of Variables <span class="badge badge-dark">' + data.vars + '</span></li>',
                    '<li>Number of Observations <span class="badge badge-dark">' + data.observations + '</span></li>'
                ),
                $dataButtons
            );

            /**
             * Create new upload div
             */
            $('#newUpload').prepend(
                $dataDiv.append(
                    $dataHeader,
                    $descripUl,
                    $dataBody
                ).hide().fadeIn(1000)
            );
        })
    }
};


$(document).ready(function () {


});
