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
            $('.dz-error-message').children(':first').html(error.file);
        })
        this.on("success", function (file, data) {
            $('.dz-progress').hide();
            $('.dz-error-mark').hide();
            console.log(data);

            // Define longer new dataset elements
            var $dataDiv = $('<div/>', {'id': 'dataset_' + data.pk, 'class': 'row newDataset datasetDiv'});
            var $makeModel = $('<a/>', {'class': 'btn btn-default', 'href': '/home/Clayton/create/' + data.pk});
            $makeModel.html('Make Model');
            var $listVars = $('<li/>', {
                'class': 'varsToggle',
                'css': {'cursor': 'pointer'},
                'text': 'Variable Names '
            }).append(
                '<i class="fas fa-arrow-alt-circle-right"></i>'
            );
            var $dataVariables = $('<ul/>');
            $.each(data.var_info, function (key, value) {
                $dataVariables.append(
                    '<li>' + value.name + ': ' + value.type + '</li>'
                )
            });
            $dataVariables.hide();

            // Clone hidden deleteUpload form
            var $deleteUpload = $('#deleteUpload').clone().attr({'action': '/datasetdelete/' + data.pk});
            $deleteUpload.css("visibility", "visible");

            // Create new upload div
            $('#newUpload').prepend(
                $dataDiv.append(
                    '<h3>' + data.name + '</h3>',
                    $('<ul/>').append(
                        '<li>Number of Variables: ' + data.vars + '</li>',
                        '<li>Number of Observations: ' + data.observations + '</li>',
                        $listVars,
                        $dataVariables
                    ),
                    $('<div/>', {'class': 'btn-toolbar'}).append($makeModel, $deleteUpload)
                ).hide().fadeIn(1000)
            );
        })
    }
};


$(document).ready(function () {


});
