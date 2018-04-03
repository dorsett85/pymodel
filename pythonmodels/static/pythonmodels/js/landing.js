$(document).ready(function () {


    /**
     * Populate landing page charts
     */
    $.getJSON({
        url: "/",
        success: function (data) {
            console.log(data);

            // Remove load spinner
            $('.landingSpinner').hide();
            $('#plot1, #plot2').height(300);

            /**
             * Scatter plot
             */
            Highcharts.chart('plot1', {
                chart: {
                    type: 'scatter'
                },
                title: {
                    text: data.scatter.y_var + ' vs. ' + data.scatter.x_var
                },
                xAxis: {
                    title: {
                        text: data.scatter.x_var
                    }
                },
                yAxis: {
                    title: {
                        text: data.scatter.y_var
                    }
                },
                legend: {
                    title: {text: '<span style="color: #a0a0a3">' + data.scatter.cat_var + '</span>'},
                    layout: 'vertical',
                    verticalAlign: 'middle',
                    align: 'right',
                    margin: 5,
                    padding: 5
                },
                series: data.scatter.points
            });

            /**
             * Density plot
             */
            Highcharts.chart('plot2', {
                chart: {type: 'area'},
                title: {
                    text: data.density.x_var + ' Density'
                },
                yAxis: [{title: {text: 'Probability'}}],
                legend: {
                    title: {text: '<span style="color: #a0a0a3">' + data.density.cat_var + '</span>'},
                    margin: 5,
                    padding: 5
                },
                series: data.density.points,
            });

        }
    })
});
