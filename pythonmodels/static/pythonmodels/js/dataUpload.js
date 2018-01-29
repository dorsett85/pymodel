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
        this.on("success", function (file, response) {
            $('.dz-progress').hide();
            $('.dz-error-mark').hide();
            console.log(response);

            // Create make model button and clone hidden deleteUpload form
            var $makeModel = $('<a/>', {'class': 'btn btn-default', 'href': '/home/Clayton/create/' + response[0].pk})
            $makeModel.html('Make Model');
            var $deleteUpload = $('#deleteUpload').clone().attr({'action': '/datasetdelete/' + response[0].pk});
            $deleteUpload.css("visibility", "visible");

            // Create new upload div
            $('#newUpload').append(
                $('<div/>', {'id': 'dataset_' + response[0].pk, 'class': 'row newDataset datasetDiv'}).append(
                    '<h4>' + response[0].fields.name + '</h4> \
                    <ul> \
                        <li>Variables: ' + response[0].fields.vars + '</li> \
                        <li>Observations: ' + response[0].fields.observations + '</li> \
                    </ul>',
                    [$('<div/>', {'class': 'btn-toolbar'}).append($makeModel, [$deleteUpload])]
                ).hide().fadeIn(1000)
            );
        })
    }
};


$(document).ready(function () {

});
