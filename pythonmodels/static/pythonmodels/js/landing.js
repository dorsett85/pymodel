$(document).ready(function () {


    /**
     * Populate landing page charts
     */
    $.getJSON({
        url: "/",
        success: function (data) {
            var keys = Object.keys(data.scatter[0]);
            var dataPoints = data.scatter.map(function (point) {
                return [point[keys[0]], point[keys[1]]]
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
                    text: keys[1] + ' vs. ' + keys[0]
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
                    console.log(data);

                    // Histogram data
                    var bins = data.hist.map(function (bin) {
                        return {x: bin.space, y: bin.count, range: bin.bins}
                    });

                    // Density data
                    var dens = data.density.map(function (den) {
                        return {x: den.space, y: den.prob}
                    });

                    // Create second chart
                    Highcharts.chart('plot2', {
                        title: {
                            text: data.var + ' Histogram'
                        },
                        plotOptions: {
                            column: {
                                groupPadding: 0,
                                pointPadding: 0
                            }
                        },
                        tooltip: {
                            formatter: function() {
                                var s = '';

                                $.each(this.points, function(i, point) {
                                    s += '<br/><span style="color:' + point.color + '">\u25CF</span> ' +
                                        point.series.name + ': ' + point.y + '<br>' +
                                        point.point.range;
                                });

                                return s;
                            },
                            shared: true
                        },
                        xAxis: [{}, {}],
                        yAxis: [{title: {text: 'Frequency'}}],
                        series: [{
                            name: 'Count',
                            type: 'column',
                            color: 'rgb(34, 126, 230)',
                            data: bins
                        }],
                        legend: {enabled: false}
                    });
                }
            })
        }
    })
});
