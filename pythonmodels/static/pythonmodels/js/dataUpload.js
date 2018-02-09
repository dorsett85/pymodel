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

            // Make variable info div

            // Initiate variables to iterate
            var $varLi = $('<li/>', {'class': 'list-group-item'});
            var $varSpan = $('<span/>', {'class': 'font-weight-bold'});

            // Function to return completed variable info item
            function varInfo(varType, spanText, liText) {
                var $varItem = $varLi.clone();
                var $spanItem = $varSpan.clone();
                if (typeof varType !== 'undefined') {
                    $varItem.addClass('list-group-item text-center');
                    if (varType === 'boolean') {
                        $varItem.addClass('list-group-item-danger')
                    }
                    else if (varType === 'character') {
                        $varItem.addClass('list-group-item-success')
                    }
                    else if (varType === 'numeric') {
                        $varItem.addClass('list-group-item-primary')
                    }
                    else {
                        $varItem.addClass('list-group-item-warning')
                    }
                } else {
                }
                $varItem.append($spanItem.text(spanText), liText);
                return $varItem
            }

            // Declare list and iterate over variable info
            var $dataVariables = $('<ol/>', {'class': 'listVars'});
            $.each(data.var_info, function (key, variable) {

                var $varUl = $('<ul/>', {'class': 'listVars list-group'}).append(
                    varInfo(variable.type, variable.type),
                    varInfo(undefined, 'Non-NA\'s: ', variable.count),
                    varInfo(undefined, 'NA\'s: ', variable.nan)
                );
                if (variable.type in {'boolean': 0, 'character': 0, 'datetime': 0}) {
                    $varUl.append(
                        varInfo(undefined, 'Non-NA\'s: ', variable.count),
                        varInfo(undefined, 'Unique Values: ', variable.unique),
                        varInfo(undefined, 'Most Frequent: ', variable.top + ' (' + variable.freq + ')')
                    )
                    if (variable.type === 'datetime') {
                    $varUl.append(
                        varInfo(undefined, 'Earliest: ', variable.first_date),
                        varInfo(undefined, 'Latest: ', variable.last_date)
                    )}
                } else if (variable.type === 'numeric') {
                    $varUl.append(
                        varInfo(undefined, 'Mean: ', variable.mean),
                        varInfo(undefined, 'Std: ', variable.std),
                        varInfo(undefined, 'Min: ', variable.min),
                        varInfo(undefined, 'Q1: ', variable.Q1),
                        varInfo(undefined, 'Median: ', variable.median),
                        varInfo(undefined, 'Q3: ', variable.Q3),
                        varInfo(undefined, 'Max: ', variable.max)
                    )
                }

                $dataVariables.append(
                    $('<li/>').append(
                        '<span class="varsToggle">' + variable.name + ' <i class="varInfoIcon fas fa-plus"></i></span>',
                        $varUl
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
