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
        $('#modelTypePara').empty().html(type)

        // Remove form errors
        $('.formErrorHighlight').removeClass('formErrorHighlight');
        $('#createModelErrors').remove()
    });


    /**
     * Run Python script with form input
     */
    $('#modelPost').click(function (e) {
        e.preventDefault();

        // Start spinner icon while dashboard loads, disable button
        $('#fa-spinner').addClass('fa fa-spinner fa-spin');
        $('#modelPost').attr('disabled', true);

        // Remove errors
        $('#createModelErrors').remove();

        $.post({
            url: window.location.pathname,
            data: $("#modelCreateForm").serialize(),
            dataType: 'JSON',
            success: function (pyData) {
                console.log(pyData);

                // Stop spinner after chart loads, enable button
                $('#fa-spinner').removeClass('fa fa-spinner fa-spin');
                $('#modelPost').attr('disabled', false);

                // Add title for model type and response variable
                if (pyData.kfolds) {
                    var kfolds = ' (' + pyData.kfolds + '-fold cv)';
                } else {
                    var kfolds = ''
                }

                // Remove no output header and add new output header
                $('#noOutputHeader').hide();
                var $modelType= $('#modelType').find(':selected');
                $('#outputHeader').empty().append(
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

                    // Residuals vs. fitted plot
                    var modelPlot = Highcharts.chart('modelPlot', {
                        chart: {
                            type: 'scatter',
                            zoomType: 'xy'
                        },
                        title: {
                            text: 'Residuals vs. Fitted'
                        },
                        xAxis: {
                            title: {
                                text: 'Fitted Values'
                            }
                        },
                        yAxis: {
                            title: {
                                text: 'Residuals'
                            }
                        },
                        legend: {enabled: false},
                        series: [{
                            regression: true,
                            regressionSettings: {
                                name: 'Polynomial line',
                                type: 'polynomial',
                                color: 'rgba(223, 183, 83, .9)',
                                dashStyle: 'dash'
                            },
                            name: 'Residuals vs. Fitted',
                            color: 'rgba(223, 83, 83, .5)',
                            data: pyData.resid_vs_fit.map(function (data) {
                                return [data.pred, data.resid];
                            })
                        }]
                    });
                } else if (pyData.model === 'log' ||
                    pyData.model === 'rfc' ||
                    pyData.model === 'knn' ||
                    pyData.model === 'gbc' ||
                    pyData.model === 'svc') {

                    // Setup confusion matrix data
                    var cf_keys = Object.keys(pyData.cf_matrix);
                    var matrix = [];
                    var count = 0;
                    $.each(cf_keys, function (key, value) {
                        $.each(pyData.cf_matrix[value], function (idx, val) {
                            matrix[count] = [key, idx, val];
                            count += 1
                        })
                    });

                    // Create confusion matrix
                    Highcharts.chart('modelPlot', {
                        chart: {
                            type: 'heatmap',
                            marginTop: 40,
                            marginBottom: 80,
                            marginRight: 70,
                            plotBorderWidth: 1
                        },
                        title: {
                            text: 'Confusion Matrix'
                        },
                        xAxis: {
                            title: {text: 'Predicted'},
                            categories: cf_keys
                        },
                        yAxis: {
                            title: {text: 'True'},
                            categories: cf_keys,
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
                            data: matrix,
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

                // Setup correlation matrix data
                var corr_keys = Object.keys(pyData.corr_matrix);
                var matrix = [];
                var count = 0;
                $.each(corr_keys, function (key, value) {
                    $.each(pyData.corr_matrix[value], function (idx, val) {
                        matrix[count] = [key, idx, val];
                        count += 1
                    })
                });

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
                        categories: corr_keys,
                    },
                    yAxis: {
                        categories: corr_keys,
                        title: null,
                        reversed: true
                    },
                    colorAxis: {
                        min: -1,
                        max: 1,
                        stops: [
                            [0, '#ff0000'],
                            [.5, '#FFFFFF'],
                            [1, '#00FF0B'],
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
                        data: matrix,
                        dataLabels: {
                            enabled: true,
                            color: '#000000'
                        }
                    }]
                });
            },
            error: function (data, error) {

                // Stop spinner and enable button
                $('#fa-spinner').removeClass('fa fa-spinner fa-spin');
                $('#modelPost').attr('disabled', false);

                // Show errors
                $('#modelCreateForm').after(
                    $('<div/>', {'id': 'createModelErrors', 'class': 'alert alert-danger'}).append(
                        data.responseJSON.message
                    )
                );

                // Highlight form input containing the error
                $('#' + data.responseJSON.error).addClass('formErrorHighlight');

            }
        });


    })


})