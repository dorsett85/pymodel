$(document).ready(function () {


    /**
     * Process to get csrf token in Django
     * @param name
     * @returns {*}
     */
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    var csrftoken = getCookie('csrftoken');

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });


    /**
     * Create datatables and add back opacity to show them
     */
    $('#varNumTable, #varOtherTable').DataTable({'dom': 'ftip'});
    $('#varTables').css('opacity', 1);


    /**
     * MathJax inline math setup
     */
    MathJax.Hub.Config({
        tex2jax: {inlineMath: [['$', '$']]}
    });


    /**
     * Hide Highcharts containers on load
     */
    $('#residVsFitted, #container2').hide();


    /**
     * Remove form errors when form is changed
     */
    $('#modelCreateForm').change(function () {
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
                $('#outputHeader').empty().append(
                    '<h3>' + $('#modelType').val() + '</h3>',
                    '<h5>Predicting ' + $('#responseVar').val() + '</h5>'
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
                 * Residuals vs. fitted plot
                 */
                $('#residVsFitted').show().empty();
                if (pyData.model === 'ols') {
                    var residVsFitted = Highcharts.chart('residVsFitted', {
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
                            name: 'Residual vs. Fitted',
                            color: 'rgba(223, 83, 83, .5)',
                            data: pyData.residual.map(function (data) {
                                return [data.pred, data.resid];
                            })
                        }]
                    });
                }


                /**
                 * Correlation matrix
                 */
                $('#corMatrix').show().empty();

                // Setup correlation matrix data
                var corr_keys = Object.keys(pyData.corr_matrix);
                var matrix = [];
                var count = 0;
                $.each(corr_keys, function (key, value) {
                    $.each(pyData.corr_matrix[value], function (idx, val) {
                        matrix[count] = [key, idx, val];
                        count+= 1
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
                        categories: corr_keys
                    },
                    yAxis: {
                        categories: corr_keys,
                        title: null
                    },
                    colorAxis: {
                        min: -1,
                        max: 1,
                        stops: [
                            [0, '#ff0000'],
                            [.5, '#FFFFFF'],
                            [1, '#00FF0B']
                        ]
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
                        $('<ul/>').append($('<li/>').html(data.responseJSON.message))
                    )
                );

                // Highlight form input containing the error
                $('#' + data.responseJSON.error).addClass('formErrorHighlight');

            }
        });


    })


});