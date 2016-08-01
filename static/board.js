var seriesOptions = [],
    seriesCounter = 0,
    names = ['total', 'style', 'content', 'total variation']; //['MSFT', 'AAPL', 'GOOG'];


var outputs = []

var options = {
    title: {
        text: 'neural-style board'
    },

    subtitle: {

    },

    chart: {
        zoomType: 'x'
    },

    rangeSelector: {
        selected: 4
    },

    yAxis: {
        //type: 'logarithmic',
        labels: {
            formatter: function () {
                return  this.value.toExponential(2) // (this.value > 0 ? ' + ' : '') + this.value + '%';
            }
        },

        plotLines: [{
            value: 0,
            width: 2,
            color: 'silver'
        }]
    },

    xAxis: {
        //floor : 10,
        tickInterval: 1,
        labels: {
            formatter: function () {
                return this.value
            }
        },
        plotLines: [{
            value: 0,
            width: 2,
            color: 'silver'
        }]
    },

    plotOptions: {
        series: {
            //compare: 'percent', //'value',undefined
            cursor: 'pointer',
            point: {
                events: {
                    click: function (e) {
                        hs.htmlExpand(null, {
                            pageOrigin: {
                                x: e.pageX || e.clientX,
                                y: e.pageY || e.clientY
                            },
                            headingText: this.series.name + ' loss@' + this.x+'=' + this.y.toExponential(3),
                            maincontentText: '<img src="/'+ outputs[this.x]+'" style="width:100%;height:100%;"></img>' ,
                            width: 200,
                            height: 200
                        });
                    }
                }
            },
            marker: {
                lineWidth: 1
            }
        }
    },

    tooltip: {
        shared: true,
        crosshairs: true,
        pointFormatter: function () {
            // undefined at this point
        },
        //pointFormat: '<span style="color:{series.color}">{series.name}</span>: <b>{point.y} </b> ({point.change}%)<br/>',
        //valueDecimals: 2
    },
    series: seriesOptions
}



/**
 * Create the chart when all data is loaded
 * @returns {undefined}
 */
function createChart() {

    //$('#container').highcharts('StockChart', {
    $('#container').highcharts(options);
}

function toLogarithmic() {
    options.subtitle.text = 'Logarithmic View';
    options.yAxis.type = 'logarithmic';
    options.plotOptions.series.compare = undefined;
    options.tooltip.pointFormatter = function () {
        return '<span style="color:' + this.series.color + '">'+ this.series.name +'</span>: <b>'+
                    this.y.toExponential(3) + '<br/>'
    }
    createChart();
}

function toPercent() {
    options.subtitle.text = 'Percent compare View';
    options.yAxis.type = undefined;
    options.plotOptions.series.compare = 'percent';
    options.tooltip.pointFormatter = function () {
         return '<span style="color:' + this.series.color + '">'+ this.series.name +'</span>: <b>'+
            this.y.toExponential(3) +'</b> (' + this.change.toFixed(2)  + '%) <br/>'
    }
    createChart();
}

function toValue() {
    options.subtitle.text = 'Value compare View';
    options.yAxis.type = undefined;
    options.plotOptions.series.compare = 'value';
    options.tooltip.pointFormatter = function () {
         return '<span style="color:' + this.series.color + '">'+ this.series.name +'</span>: <b>'+
            this.y.toExponential(3) +'</b> (' + this.change.toExponential(3)  + ') <br/>'
    }
    createChart();
}

function toDefault() {
    options.subtitle.text = undefined;
    options.yAxis.type = undefined;
    options.plotOptions.series.compare = undefined;
    options.tooltip.pointFormatter = function () {
        return '<span style="color:' + this.series.color + '">'+ this.series.name +'</span>: <b>'+
                    this.y.toExponential(3) + '<br/>'
    }
    createChart();
}

function loadjson(fname) {
    $(function () {
        $.each(names, function (i, name) {

            $.getJSON(fname, function(data) {

                seriesOptions[i] = {
                    name: name,
                    data: data['loss'][name],
                };

                for(var item in data.output)
                {
                    outputs[data.output[item][0]] = data.output[item][1];
                }

                // As we're loading the data asynchronously, we don't know what order it will arrive. So
                // we keep a counter and create the chart when all the data is loaded.
                seriesCounter += 1;

                if (seriesCounter === names.length) {
                    toDefault();
                    createChart();
                }
            });

        });
    });
}

