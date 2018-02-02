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
     * Function to add or change dataset ID in window url.
     * Don't change if it already matches the dataset ID
     */
    function changeURL(IdMatch) {
        if (/\/0$/.test(window.location.pathname)) {
            window.history.pushState("", "", window.location.pathname.replace(/\d+$/, $('#dataID').val()));
        } else if (!IdMatch) {
            window.history.pushState("", "", window.location.pathname.replace(/\d+$/, $('#dataID').val()));
        }
    }


    /**
     * Function to populate predictor and response variables
     */
    function populateVars() {
        changeURL(new RegExp($('#dataID').val() + "$"));

        // Remove errors
        $('#createModelErrors').remove();

        $.post({
            url: "/home/" + $('#userName').val() + '/create/' + $('#dataID').val(),
            success: function (data) {
                $.each(data, function (i, item) {
                    $('#predictorVars').append($('<option>', {
                        value: item,
                        text: item
                    }));
                    $('#responseVar').append($('<option>', {
                        value: item,
                        text: item
                    }));
                });
            },
            error: function () {
                console.log("fail");
            }
        });
    }


    /**
     * Populate predictor and response variables on load and
     * repopulate on dataID change
     */
    populateVars();

    $("#dataID").change(function () {
        changeURL();
        $('#predictorVars').empty();
        $('#responseVar').empty();
        populateVars();
    });


    /**
     * Remove form errors when form is changed
     */
    $('#modelCreateForm').change(function () {
        $('.formErrorHighlight').removeClass('formErrorHighlight');
        $('#createModelErrors').remove();
    })

    /**
     * Run Python script with form input
     */
    $('#pyGet').click(function (e) {
        e.preventDefault();

        // Start spinner icon while dashboard loads, disable button
        $('#fa-spinner').addClass('fa fa-spinner fa-spin');
        $('#pyGet').attr('disabled', true);

        // Remove errors
        $('#createModelErrors').remove();

        $.post({
            url: "/home/" + $('#userName').val() + '/create/' + $('#dataID').val(),
            data: $("#modelCreateForm").serialize(),
            dataType: 'JSON',
            success: function (pyData) {
                console.log(pyData);

                // Stop spinner after chart loads, enable button, add <hr>
                $('#fa-spinner').removeClass('fa fa-spinner fa-spin');
                $('#pyGet').attr('disabled', false);
                $('#outputDivider').attr('hidden', false);

                // Add title for model type and response variable
                $('#outputHeader').find('h2').empty().html($('#modelType').val()).append(
                    $('<h4>').html('Predicting ' + $('#responseVar').val())
                );

                /**
                 * Add summary statistics table
                 * Update MathJax after success
                 */
                $('#summaryStats').empty();

                $statsTableHead = $('<thead>').append($('<tr>'));
                $statsTableBody = $('<tbody>').append($('<tr>'));

                $.map(pyData.stats, function (stat, idx) {
                    $statsTableHead.find('tr').append($('<th>').html(idx).attr('scope', 'col'));
                    $statsTableBody.find('tr').append($('<td>').html(stat));
                });
                $('#summaryStats').append($statsTableHead, [$statsTableBody]);
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
                                dashStyle: 'dash',
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
                var matrix = [];
                var count = 0;

                var mat = [];
                var loop = 0
                $.each(Object.keys(pyData.corr_matrix), function (key, value) {
                    $.each(pyData.corr_matrix[value], function (idx, val) {
                        mat[loop] = [key, idx, val];
                        loop += 1;
                    });
                })
                console.log(mat);

                // pyData.corr_matrix.map(function (data, index) {
                //     for (i = 0; i < Object.keys(data).length; i++) {
                //         matrix[count] = [index, i, data[Object.keys(data)[i]]];
                //         count += 1;
                //     }
                // });

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
                        categories: Object.keys(pyData.corr_matrix)
                            // pyData.corr_matrix.map(function (data, i) {
                            // return Object.keys(data)[i]
                        // })
                    },
                    yAxis: {
                        categories: Object.keys(pyData.corr_matrix),
                        //     pyData.corr_matrix.map(function (data, i) {
                        //     return Object.keys(data)[i]
                        // }),
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
                        data: mat,
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
                $('#pyGet').attr('disabled', false);

                // Show errors
                $('#modelCreateForm').after(
                    $('<div>').attr(
                        {id: 'createModelErrors', class: 'alert alert-danger'}
                    ).append(
                        $('<ul>').append($('<li>').html(data.responseJSON.message))
                    )
                );

                // Highlight form input containing the error
                $('#' + data.responseJSON.error).addClass('formErrorHighlight');

            }
        });


    })


});
