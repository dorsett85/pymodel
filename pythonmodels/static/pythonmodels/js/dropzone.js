/*
 * Dropzone configuration
 */
Dropzone.options.uploadData = {
    url: window.location.pathname,
    // headers: {
    //     'X-CSRF-TOKEN': $('meta[name="csrf-token"]').attr('content')
    // },
    dictDefaultMessage: "Drag and Drop Dataset Here",
    acceptedFiles: ".csv, .xls, .xlsx",
    maxFiles: 1,
    addRemoveLinks: true,
    init: function () {
        this.on('error', function (file, error) {
            console.log(error);
            $('.dz-error-message span').html(error.file)
        });
        this.on("addedfile", function (file) {
            // Do something
        });
        this.on("success", function (file, response) {
            console.log(file);
            $('.dz-progress').hide();
            $('.dz-error-mark').hide();
            console.log(response);
            $('#noDataset').fadeOut();
            $('#newUploads').append("<div id=\'dataset_" + response.data.id + "\' class='row newDataset datasetDiv'></div>");
            $('#dataset_' + response.data.id).append(
                "<h4>" + response.data.name + "</h4>",
                "<ul>" +
                "<li>Variables: " + response.data.vars + "</li>" +
                "<li>Observations: " + response.data.observations + "</li>" +
                "</ul>",
                "<ul class='nav navbar-nav'>" +
                "<li><a href=\'/home/" + response.user.name + "/create/" + response.data.id + "\'>Make Model</a></li>" +
                "<li value=\'" + response.data.id + "\'><a href=\'#\' class='deleteBtn'>Delete Dataset</a></li>" +
                "</ul>" +
                "<br>"
            ).hide().fadeIn(1000);
        });
    }
};