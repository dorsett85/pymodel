$(document).ready(function () {


    /**
     * Hide Highcharts containers on load
     */
    $('#modelPlot, #corrMatrix').hide().height(350);


    /**
     * Form change listeners
     */
    $('#modelCreateForm').change(function () {

        // Print model type below model type selector
        var type = $('#modelType').find(':selected').parent().attr('label');
        $('#modelTypePara').empty().html(type);

        // Remove form errors
        $('.formErrorHighlight').removeClass('formErrorHighlight');
        $('.formErrors').remove()
    });


    /**
     * Run Python script with form input
     */
    $('#modelPost').click(function (e) {
        e.preventDefault();

        // Start spinner icon while dashboard loads, disable button
        $(this).children('.createBtnSpin').addClass('fa fa-spinner fa-spin');
        $('#modelPost').attr('disabled', true);

        // Remove errors
        $('.formErrors').remove();

        $.post({
            url: window.location.pathname,
            data: $("#modelCreateForm").serialize(),
            dataType: 'JSON',
            success: function (pyData) {
                console.log(pyData);

                // Stop spinner after chart loads, enable button
                $('.fa-spinner').removeClass('fa fa-spinner fa-spin');
                $('#modelPost').attr('disabled', false);

                // Add title for model type and response variable
                if (pyData.kfolds) {
                    var kfolds = ' (' + pyData.kfolds + '-fold cv)';
                } else {
                    var kfolds = ''
                }

                // Remove no output header and add new output header
                $('#modelNoOutputHeader').hide();
                var $modelType= $('#modelType').find(':selected');
                $('#modelOutputHeader').empty().append(
                    '<h3>' + $modelType.text() + ' ' + $modelType.parent().attr('label') + '</h3>',
                    '<h5>Predicting ' + $('#responseVar').val() + kfolds + '</h5>'
                );

                /**
                 * Add summary statistics table
                 * Update MathJax after success
                 */
                $('#summaryStats').empty();

                var $statsTableHead = $('<thead>').append($('<tr>'));
                var $statsTableBody = $('<tbody>').append($('<tr>'));

                $.map(pyData.stats, function (stat, idx) {
                    $statsTableHead.find('tr').append($('<th>').html(idx).attr('scope', 'col'));
                    $statsTableBody.find('tr').append($('<td>').html(stat));
                });
                $('#summaryStats').append($statsTableHead, $statsTableBody);
                MathJax.Hub.Queue(["Typeset", MathJax.Hub, document.getElementById('summaryStats')]);

                /**
                 * Model specific plots
                 */
                $('#modelPlot').show().empty();

                if (pyData.model === 'ols' ||
                    pyData.model === 'rfr' ||
                    pyData.model === 'en' ||
                    pyData.model === 'gbr' ||
                    pyData.model === 'svr') {

                    // Predicted vs. actual
                    Highcharts.chart('modelPlot', {
                        title: {
                            text: 'Predicted vs. Actual'
                        },
                        xAxis: {title: {text: 'Actual'}},
                        yAxis: {title: {text: 'Predicted'}},
                        series: [{
                            name: 'Predicted vs. Actual',
                            type: 'scatter',
                            data: pyData.pred_vs_true.scatter,
                            color: 'rgba(73, 191, 238, 0.5)',
                            showInLegend: false
                        }, {
                            name: 'Perfect Fit',
                            type: 'line',
                            data: pyData.pred_vs_true.fit,
                            color: 'rgba(228, 228, 51, 0.75)',
                            marker: {enabled: false}
                        }]
                    });

                } else if (pyData.model === 'log' ||
                    pyData.model === 'rfc' ||
                    pyData.model === 'knn' ||
                    pyData.model === 'gbc' ||
                    pyData.model === 'svc') {

                    // Confusion matrix
                    Highcharts.chart('modelPlot', {
                        chart: {
                            type: 'heatmap',
                            marginTop: 40,
                            marginBottom: 80,
                            marginRight: 70,
                            plotBorderWidth: 1,
                        },
                        title: {
                            text: 'Confusion Matrix'
                        },
                        xAxis: {
                            title: {text: 'Predicted'},
                            categories: pyData.cf_matrix.categories
                        },
                        yAxis: {
                            title: {text: 'True'},
                            categories: pyData.cf_matrix.categories,
                            reversed: true
                        },
                        colorAxis: {
                            color: '#FFFFFF',
                            maxColor: '#FFFFFF'
                        },
                        legend: {enabled: false},
                        series: [{
                            name: 'Confusion',
                            borderWidth: 1,
                            data: pyData.cf_matrix.matrix,
                            dataLabels: {
                                enabled: true,
                                color: '#000000'
                            }
                        }]
                    });

                }

                /**
                 * Correlation matrix
                 */
                $('#corrMatrix').show().empty();

                // Create correlation matrix
                Highcharts.chart('corrMatrix', {
                    chart: {
                        type: 'heatmap',
                        marginTop: 40,
                        marginBottom: 80,
                        plotBorderWidth: 1
                    },
                    title: {
                        text: 'Correlation Matrix'
                    },
                    xAxis: {
                        categories: pyData.corr_matrix.vars,
                    },
                    yAxis: {
                        categories: pyData.corr_matrix.vars,
                        title: null,
                        reversed: true
                    },
                    colorAxis: {
                        min: -1,
                        max: 1,
                        stops: [
                            [0, '#ff0000'],
                            [.5, '#FFFFFF'],
                            [1, '#00FF0B']
                        ],
                        reversed: false
                    },
                    legend: {
                        align: 'right',
                        layout: 'vertical',
                        margin: 0,
                        verticalAlign: 'top',
                        y: 25,
                        symbolHeight: 280
                    },
                    series: [{
                        name: 'Correlation',
                        borderWidth: 1,
                        data: pyData.corr_matrix.matrix,
                        dataLabels: {
                            enabled: true,
                            color: '#000000'
                        }
                    }]
                });
            },
            error: function (data, error) {

                // Stop spinner and enable button
                $('.fa-spinner').removeClass('fa fa-spinner fa-spin');
                $('#modelPost').attr('disabled', false);

                // Show errors
                $('#modelCreateForm').after(
                    $('<div/>', {'class': 'alert alert-danger formErrors'}).append(
                        data.responseJSON.message
                    )
                );

                // Highlight form input containing the error
                $('#' + data.responseJSON.error).addClass('formErrorHighlight');

            }
        });


    })


});