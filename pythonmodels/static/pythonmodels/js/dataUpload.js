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
             * @type {jQuery|HTMLElement}
             */

                // new dataset card and card-header
            var $dataDiv = $('<div/>', {'id': 'dataset_' + data.pk, 'class': 'card border-dark datasetDiv'});
            var $dataHeader = $('<h4/>', {
                'class': 'card-header newDataset'
            }).append(
                '<i class="fas fa-table"></i> ' + data.name
            );

            var $dataVariables = $('<ol/>', {'class': 'listVars'});
            $.each(data.var_info, function (key, variable) {
                $dataVariables.append(
                    $('<li/>').append(
                        '<span class="varsToggle">' + variable.name + ' <i class="varInfoIcon fas fa-plus"></i></span>',
                        $('<ul/>', {'class': 'listVars'}).append(
                            '<li>' + variable.type + '</li>',
                            '<li>Non-NA\'s: ' + variable.count + '</li>',
                            '<li>NA\'s: ' + variable.nan + '</li>',
                            (variable.type in {'boolean': 0, 'character': 0, 'datetime': 0} ?
                                    '<li>Unique Values: ' + variable.unique + '</li>' +
                                    '<li>Most Frequent: ' + variable.top + ' (' + variable.freq + ')</li>' +
                                    (variable.type === 'datetime' ?
                                        '<li>Earliest: ' + variable.first_date + '</li>' +
                                        '<li>Latest: ' + variable.last_date + '</li>' : '') :
                                    (variable.type === 'numeric' ?
                                        '<li>Mean: ' + variable.mean + '</li>' +
                                        '<li>Std: ' + variable.std + '</li>' +
                                        '<li>Min: ' + variable.min + '</li>' +
                                        '<li>Q1: ' + variable.Q1 + '</li>' +
                                        '<li>Median: ' + variable.median + '</li>' +
                                        '<li>Q3: ' + variable.Q3 + '</li>' +
                                        '<li>Max: ' + variable.max + '</li>' : '')
                            )
                        )
                    )
                )
            });

            // Make variable info list
            var $listVars = $('<li/>').append(
                '<span class="varsToggle">Variable Info <i class="fas fa-arrow-alt-circle-right"></i>',
                $dataVariables
            );

            // Make model button and clone hidden deleteUpload form
            var $dataButtons = $('<div/>', {'class': 'btn-toolbar'}).append(
                $('<a/>', {
                    'class': 'btn btn-dark buttonSpace',
                    'href': '/home/Clayton/create/' + data.pk,
                    'text': 'Make Model'
                }),
                $('#deleteUpload').clone().attr({
                    'action': '/datasetdelete/' + data.pk
                }).css("visibility", "visible")
            );

            // Make card body
            var $dataBody = $('<div/>', {'class': 'card-body'}).append(
                $('<ul/>', {'class': 'list-unstyled'}).append(
                    '<li>Number of Variables <span class="badge badge-dark">' + data.vars + '</span></li>',
                    '<li>Number of Observations <span class="badge badge-dark">' + data.observations + '</span></li>',
                    $listVars
                ),
                $dataButtons
            );

            /**
             * Create new upload div
             */
            $('#newUpload').prepend(
                $dataDiv.append(
                    $dataHeader,
                    $dataBody
                ).hide().fadeIn(1000)
            );
        })
    }
};


$(document).ready(function () {


});
