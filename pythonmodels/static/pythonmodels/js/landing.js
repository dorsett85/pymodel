$(document).ready(function () {


    /**
     * Set active navigation li
     * Change path if active li is create model tab
     */
    var path = window.location.pathname;
    if (path.match(/create/i)) {
        path = path.replace(/\d+$/, "0")
    }
    var activeTab = $("a[href='" + path + "']").parent();
    activeTab.addClass('active');

    // Hide collapsed navigation after click
    $('.nav a').click(function () {
        $('#myNavbar').collapse('hide');
    });

    // increase height of login and registration pages
    var lh = $('.loginRegistration').height();
    var hh = $('.header').height();
    var fh = $('footer').height();
    $('.loginRegistration').h


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

            // Create highcharts global theme
            Highcharts.createElement('link', {
                href: 'https://fonts.googleapis.com/css?family=Indie+Flower|Bree+Serif',
                rel: 'stylesheet',
                type: 'text/css'
            }, null, document.getElementsByTagName('head')[0]);

            Highcharts.theme = {
                colors: ['#2b908f', '#90ee7e', '#f45b5b', '#7798BF', '#aaeeee', '#ff0066',
                    '#eeaaee', '#55BF3B', '#DF5353', '#7798BF', '#aaeeee'],
                chart: {
                    backgroundColor: {
                        linearGradient: {x1: 0, y1: 0, x2: 1, y2: 1},
                        stops: [
                            [0, '#2a2a2b'],
                            [1, '#3e3e40']
                        ]
                    },
                    style: {
                        fontFamily: '\'Bree Serif\', sans-serif'
                    },
                    plotBorderColor: '#606063'
                },
                title: {
                    style: {
                        color: '#E0E0E3',
                        textTransform: 'uppercase',
                        fontSize: '20px'
                    }
                },
                subtitle: {
                    style: {
                        color: '#E0E0E3',
                        textTransform: 'uppercase'
                    }
                },
                xAxis: {
                    gridLineColor: '#707073',
                    labels: {
                        style: {
                            color: '#E0E0E3'
                        }
                    },
                    lineColor: '#707073',
                    minorGridLineColor: '#505053',
                    tickColor: '#707073',
                    title: {
                        style: {
                            color: '#A0A0A3',
                            fontSize: '14px'
                        }
                    }
                },
                yAxis: {
                    gridLineColor: '#707073',
                    labels: {
                        style: {
                            color: '#E0E0E3'
                        }
                    },
                    lineColor: '#707073',
                    minorGridLineColor: '#505053',
                    tickColor: '#707073',
                    tickWidth: 1,
                    title: {
                        style: {
                            color: '#A0A0A3',
                            fontSize: '14px'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.85)',
                    style: {
                        color: '#F0F0F0'
                    }
                },
                plotOptions: {
                    series: {
                        dataLabels: {
                            color: '#B0B0B3'
                        },
                        marker: {
                            lineColor: '#333'
                        }
                    },
                    boxplot: {
                        fillColor: '#505053'
                    },
                    candlestick: {
                        lineColor: 'white'
                    },
                    errorbar: {
                        color: 'white'
                    }
                },
                legend: {
                    itemStyle: {
                        color: '#E0E0E3'
                    },
                    itemHoverStyle: {
                        color: '#FFF'
                    },
                    itemHiddenStyle: {
                        color: '#606063'
                    }
                },
                credits: {
                    style: {
                        color: '#666'
                    }
                },
                labels: {
                    style: {
                        color: '#707073'
                    }
                },
                drilldown: {
                    activeAxisLabelStyle: {
                        color: '#F0F0F3'
                    },
                    activeDataLabelStyle: {
                        color: '#F0F0F3'
                    }
                },
                navigation: {
                    buttonOptions: {
                        symbolStroke: '#DDDDDD',
                        theme: {
                            fill: '#505053'
                        }
                    }
                },

                // scroll charts
                rangeSelector: {
                    buttonTheme: {
                        fill: '#505053',
                        stroke: '#000000',
                        style: {
                            color: '#CCC'
                        },
                        states: {
                            hover: {
                                fill: '#707073',
                                stroke: '#000000',
                                style: {
                                    color: 'white'
                                }
                            },
                            select: {
                                fill: '#000003',
                                stroke: '#000000',
                                style: {
                                    color: 'white'
                                }
                            }
                        }
                    },
                    inputBoxBorderColor: '#505053',
                    inputStyle: {
                        backgroundColor: '#333',
                        color: 'silver'
                    },
                    labelStyle: {
                        color: 'silver'
                    }
                },
                navigator: {
                    handles: {
                        backgroundColor: '#666',
                        borderColor: '#AAA'
                    },
                    outlineColor: '#CCC',
                    maskFill: 'rgba(255,255,255,0.1)',
                    series: {
                        color: '#7798BF',
                        lineColor: '#A6C7ED'
                    },
                    xAxis: {
                        gridLineColor: '#505053'
                    }
                },
                scrollbar: {
                    barBackgroundColor: '#808083',
                    barBorderColor: '#808083',
                    buttonArrowColor: '#CCC',
                    buttonBackgroundColor: '#606063',
                    buttonBorderColor: '#606063',
                    rifleColor: '#FFF',
                    trackBackgroundColor: '#404043',
                    trackBorderColor: '#404043'
                },

                // special colors for some of the
                legendBackgroundColor: 'rgba(0, 0, 0, 0.5)',
                background2: '#505053',
                dataLabelsColor: '#B0B0B3',
                textColor: '#C0C0C0',
                contrastTextColor: '#F0F0F3',
                maskColor: 'rgba(255,255,255,0.3)'
            };

            // Apply the theme
            Highcharts.setOptions(Highcharts.theme);


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
