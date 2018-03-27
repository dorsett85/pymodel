$(document).ready(function () {


    /**
     * Hide Highcharts containers on load
     */
    $('#visPlot1, #visPlot2').hide().height(350);


    /**
     * Form change listeners
     */
    $('#visCreateForm').change(function () {

        // Remove form errors
        $('.formErrorHighlight').removeClass('formErrorHighlight');
        $('.formErrors').remove()
    });


    /**
     * Run Python script with form input
     */
    $('#visPost').click(function (e) {
        e.preventDefault();

        // Start spinner icon while dashboard loads, disable button
        $(this).children('.createBtnSpin').addClass('fa fa-spinner fa-spin');
        $('#visPost').attr('disabled', true);

        // Remove errors
        $('.formErrors').remove();

        $.post({
            url: window.location.pathname,
            data: $("#visCreateForm").serialize(),
            dataType: 'JSON',
            success: function (pyData) {
                console.log(pyData);

                // Stop spinner after chart loads, enable button
                $('.fa-spinner').removeClass('fa fa-spinner fa-spin');
                $('#visPost').attr('disabled', false);

                // Remove no output header and add new output header
                $('#visNoOutputHeader').hide();
                $('#visOutputHeader').empty().append(
                    '<h3>' + $('#xVar').val() + ' Exploratory Visualizations</h3>'
                );


                /**
                 * Vis plot 1
                 */
                $('#visPlot1').show().empty();

                Highcharts.chart('visPlot1', {
                    title: {
                        text: $('#xVar').val() + ' Density'
                    },
                    xAxis: {title: {text: 'Value'}},
                    yAxis: {title: {text: 'Probability'}},
                    series: [{
                        name: 'Probability vs. Value',
                        type: 'area',
                        data: pyData.x_den,
                        color: 'rgba(73, 191, 238, 0.5)',
                        showInLegend: false
                    }]
                });

                /**
                 * Vis plot 2
                 */
                $('#visPlot2').show().empty();

                Highcharts.chart('visPlot2', {
                    title: {
                        text: $('#xVar').val() + ' Values'
                    },
                    xAxis: {title: {text: 'Observation'}},
                    yAxis: {title: {text: ''}},
                    series: [{
                        name: $('#xVar').val(),
                        type: 'scatter',
                        data: pyData.x_vals,
                        color: 'rgba(228, 228, 51, 0.75)',
                        showInLegend: false
                    }]
                });
            },
            error: function (data, error) {

                // Stop spinner and enable button
                $('.fa-spinner').removeClass('fa fa-spinner fa-spin');
                $('#visPost').attr('disabled', false);

                // Show errors
                $('#visCreateForm').after(
                    $('<div/>', {'class': 'alert alert-danger formErrors'}).append(
                        data.responseJSON.message
                    )
                );

                // Highlight form input containing the error
                $('#' + data.responseJSON.error).addClass('formErrorHighlight');

            }
        });


    })


})