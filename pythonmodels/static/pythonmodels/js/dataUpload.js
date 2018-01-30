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
            $.each(response.var_info, function (key, value) {
                console.log(value.name, value.type);
            });

            // Create make model button and clone hidden deleteUpload form
            var $makeModel = $('<a/>', {'class': 'btn btn-default', 'href': '/home/Clayton/create/' + response.pk})
            $makeModel.html('Make Model');
            var $deleteUpload = $('#deleteUpload').clone().attr({'action': '/datasetdelete/' + response.pk});
            $deleteUpload.css("visibility", "visible");

            // Create new upload div
            $('#newUpload').append(
                $('<div/>', {'id': 'dataset_' + response.pk, 'class': 'row newDataset datasetDiv'}).append(
                    '<h4>' + response.name + '</h4> \
                    <ul> \
                        <li>Variables: ' + response.vars + '</li> \
                        <li>Observations: ' + response.observations + '</li> \
                    </ul>',
                    [$('<div/>', {'class': 'btn-toolbar'}).append($makeModel, [$deleteUpload])]
                ).hide().fadeIn(1000)
            );
        })
    }
};


$(document).ready(function () {

});
