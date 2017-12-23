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


    /*
     * Run R script with form input
     */
    $('#rGet').click(function (e) {
        e.preventDefault();

        $.post({
            url: "/rmodel/" + $('#dataID').val(),
            data: $("#modelCreateForm").serialize(),
            success: function (data) {

                // Initial R import data cleanup
                var rData = JSON.parse(data);
                console.log(rData);

                // var matrix = [];
                // rData.cor_matrix.map(function (data, index) {
                //     for (i = 0; i < Object.keys(data).length; i++) {
                //         matrix[index] = [index, index, data[Object.keys(data)[0]], Object.keys(data)[index]]
                //     }
                // });
                // console.log(matrix);

                // Empty and show highcharts containers
                $('#residVsFitted, #container2').show().empty();

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
                    subtitle: {
                        text: $('#responseVar').val() + ' as a function of ' + $('#predictorVars').val().join(" & ")
                    },
                    xAxis: {
                        title: {
                            enabled: true,
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
                        data: rData.augment.map(function (data) {
                            return [data[".fitted"], data[".resid"]];
                        })
                    }]
                });

                /**
                 * Rsquare value
                 */

                Highcharts.chart('container2', {

                    chart: {
                        type: 'heatmap',
                        marginTop: 40,
                        marginBottom: 80,
                        plotBorderWidth: 1
                    },


                    title: {
                        text: 'Sales per employee per weekday'
                    },

                    xAxis: {
                        categories: rData.cor_matrix.map(function (data) {
                            return data._row
                        })
                    },

                    yAxis: {
                        categories: rData.cor_matrix.map(function (data) {
                            return data._row
                        }),
                        title: null
                    },

                    colorAxis: {
                        min: 0,
                        minColor: '#FFFFFF',
                        maxColor: Highcharts.getOptions().colors[0]
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
                        name: 'Sales per employee',
                        borderWidth: 1,
                        data: rData.cor_matrix.map(function (data, i) {
                            return [i, i, i]
                        }),
                        dataLabels: {
                            enabled: true,
                            color: '#000000'
                        }
                    }]

                });
                //     var myChart = Highcharts.chart('container2', {
                //             chart: {
                //                 type: 'bar'
                //             },
                //             title: {
                //                 text: 'Fruit Consumption'
                //             },
                //             xAxis: {
                //                 categories: ['Apples', 'Bananas', 'Oranges']
                //             },
                //             yAxis: {
                //                 title: {
                //                     text: 'Fruit eaten'
                //                 }
                //             },
                //             series: [{
                //                 name: 'Jane',
                //                 data: [1, 2, 4]
                //             }, {
                //                 name: 'John',
                //                 data: [5, 7, 3]
                //             }]
                //         });
                //
                //
            },
            error: function () {
                console.log('Fail!')
            }
        })
        ;
    })


})
