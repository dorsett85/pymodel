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
                    text: data.y_var + ' vs. ' + data.x_var
                },
                xAxis: {
                    title: {
                        text: data.x_var
                    }
                },
                yAxis: {
                    title: {
                        text: data.y_var
                    }
                },
                legend: {
                    title: {text: '<span style="color: #a0a0a3">' + data.cat_var + '</span>'},
                    layout: 'vertical',
                    verticalAlign: 'middle',
                    align: 'right',
                    margin: 5,
                    padding: 5

                },
                series: data.scatter
            });

            /**
             * Histogram
             */
            Highcharts.chart('plot2', {
                chart: {type: 'area'},
                title: {
                    text: data.x_var + ' Histogram'
                },
                plotOptions: {
                    column: {
                        groupPadding: 0,
                        pointPadding: 0
                    }
                },
                // tooltip: {
                //     formatter: function() {
                //         var s = '';
                //
                //         $.each(this.points, function(i, point) {
                //             s += '<br/><span style="color:' + point.color + '">\u25CF</span> ' +
                //                 point.series.name + ': ' + point.y + '<br>' +
                //                 point.point.range;
                //         });
                //
                //         return s;
                //     },
                //     shared: true
                // },
                xAxis: [{}, {}],
                yAxis: [{title: {text: 'Frequency'}}],
                legend: {
                    title: {text: '<span style="color: #a0a0a3">' + data.cat_var + '</span>'},
                    layout: 'vertical',
                    verticalAlign: 'middle',
                    align: 'right',
                    margin: 5,
                    padding: 5

                },
                series: data.den,
            });

        }
    })
});
