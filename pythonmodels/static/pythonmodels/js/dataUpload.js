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
            $('#newUpload').append(
                $('<div/>', {'id': 'dataset_' + response[0].pk, 'class': 'row newDataset datasetDiv'}).append(
                    $('<h4/>').html(response[0].fields.name), [
                        $('<ul/>').append(
                            $('<li/>').html('Variables: ' + response[0].fields.vars), [
                                $('<li/>').html('Observations: ' + response[0].fields.observations)
                            ]
                        ),
                        $('<a/>', {'class': 'btn btn-default', 'href': '/home/Clayton/create/' + response[0].pk}).html('Make Model')
                    ]
                ).hide().fadeIn(1000)
            );
        })
    }
};