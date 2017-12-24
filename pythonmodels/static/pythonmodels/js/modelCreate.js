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
     * Hide Highcharts containers on load
     */
    $('#residVsFitted, #container2').hide();


    /**
     * Function to add or change dataset ID in window url.
     * Don't change if it already matches the dataset ID
     */
    function changeURL(IdMatch) {
        if (/0$/.test(window.location.pathname)) {
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
     * Run Python script with form input
     */
    $('#pyGet').click(function (e) {
        e.preventDefault();

        $.post({
            url: "/home/" + $('#userName').val() + '/create/' + $('#dataID').val(),
            data: $("#modelCreateForm").serialize(),
            dataType: 'JSON',
            success: function (pyData) {
                console.log(pyData);


                // Add title for model type
                $('#outputHeader').find('h3').empty().html("Linear Regression");

                // Add coefficients table
                var rowTRs = [];
                $('#modelCoefs').empty();
                pyData.map(function (coef, idx) {

                    // Add header
                    if (idx === 0) {
                        var cols = [];
                        Object.keys(coef).map(function (header, i) {
                            cols[i] = '<th>' + header + '</th>'
                        });
                        $cols = $('<thead>').append($('<tr>').append(cols.join("")));
                    }
                    ;

                    // Add rows
                    var rowTDs = [];
                    Object.keys(coef).map(function (row, i) {
                        rowTDs[i] = '<td>' + coef[row] + '</td>'
                    });
                    rowTRs[idx] = '<tr>' + rowTDs.join("") + '</tr>';
                });
                $cols.appendTo('#modelCoefs');
                $('#modelCoefs thead').after($('<tbody>').append(rowTRs.join("")));

                // Convert to datatable
                $('#modelCoefs').DataTable({
                    destroy: true,
                    "sDom": ''
                });

                // Empty and show highcharts containers
                $('#residVsFitted, #corMatrix').show().empty();

                /**
                 * Residuals vs. fitted plot
                 */
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
                            type: 'polynomial',
                            color: 'rgba(223, 183, 83, .9)',
                            dashStyle: 'dash'
                        },
                        name: 'Female',
                        color: 'rgba(223, 83, 83, .5)',
                        data: pyData.map(function (data) {
                            return [data[".fitted"], data[".resid"]];
                        })
                    }]
                });

                /**
                 * Correlation matrix
                 */

                    // Setup correlation matrix data
                var matrix = [];
                var count = 0;
                pyData.cor_matrix.map(function (data, index) {
                    for (i = 0; i < Object.keys(data).length - 1; i++) {
                        matrix[count] = [index, i, Math.round(data[Object.keys(data)[i]] * 100) / 100];
                        count += 1;
                    }
                });

                // Create correlation matrix
                Highcharts.chart('corMatrix', {
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
                        categories: pyData.cor_matrix.map(function (data) {
                            return data._row
                        })
                    },
                    yAxis: {
                        categories: pyData.cor_matrix.map(function (data) {
                            return data._row
                        }),
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
            error: function () {
                console.log('Fail!')
            }
        })
        ;
    })


})
