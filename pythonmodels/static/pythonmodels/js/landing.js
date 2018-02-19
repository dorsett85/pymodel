$(document).ready(function () {


    /**
     * Populate landing page charts
     */
    $.getJSON({
        url: "/",
        success: function (data) {
            var keys = Object.keys(data[0]);
            var dataPoints = data.map(function (points) {
                return [points[keys[0]], points[keys[1]]]
            });

            // Remove load spinner
            $('.landingSpinner').hide();
            $('#plot1, #plot2').height(300);

            // Create first chart
            Highcharts.chart('plot1', {
                chart: {
                    type: 'scatter'
                },
                title: {
                    text: keys[0] + ' vs. ' + keys[1]
                },
                xAxis: {
                    title: {
                        text: keys[0]
                    }
                },
                yAxis: {
                    title: {
                        text: keys[1]
                    }
                },
                legend: {enabled: false},
                series: [{
                    name: keys[0] + ' vs. ' + keys[1],
                    color: 'rgba(34, 230, 34, 0.5)',
                    data: dataPoints
                }]
            });

            /**
             * Get second chart
             */
            $.getJSON({
                url: '/',
                data: {chart2: "chart2"},
                success: function (data) {
                    var key = Object.keys(data[0]);
                    var dataPoints = data.map(function (points) {
                        return points[key[0]]
                    });

                    // Create second chart
                    Highcharts.chart('plot2', {
                        title: {
                            text: key[0] + ' Histogram'
                        },
                        xAxis: [{}, {}],
                        yAxis: [{title: ''}, {title: {text: 'Frequency'}}],
                        series: [{
                            name: key[0],
                            type: 'histogram',
                            color: 'rgb(34, 126, 230)',
                            xAxis: 1,
                            yAxis: 1,
                            baseSeries: 's1',
                            zIndex: -1
                        }, {
                            data: dataPoints,
                            id: 's1',
                            visible: false
                        }],
                        legend: {enabled: false}
                    });
                }
            })
        }
    })
});
