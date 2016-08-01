var seriesOptions = [],
    seriesCounter = 0,
    names = ['total', 'style', 'content', 'total variation']; //['MSFT', 'AAPL', 'GOOG'];


var outputs = []
var title = {
    text: 'neural-style board'
};
var compare = undefined;

var options = {
    title: title,

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
            //compare: 'percent',
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
                            maincontentText: '<img src="/picture?path='+ outputs[this.x]+'" style="width:100%;height:100%;"></img>' ,
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
            var change = '';
            if (compare === 'percent')
                change = '('+this.change.toFixed(2)+'% )';
            else if (compare === 'value')
                change = '('+this.change.toExponential(3)+')'
            return '<span style="color:' + this.series.color + '">'+ this.series.name +'</span>: <b>'+
                    this.y.toExponential(3) +change +'<br/>';
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
    $('#container').highcharts(options);
}

/**
    TODO: fix the bug in logarithmic view
 */
//function toLogarithmic() {
//    //options.subtitle.text = 'Logarithmic View';
//    options.yAxis.type = 'logarithmic';
//    createChart()
//    //options.plotOptions.series.compare = undefined;
//    //options.tooltip.pointFormatter = function () {
//    //    return '<span style="color:' + this.series.color + '">'+ this.series.name +'</span>: <b>'+
//    //                this.y.toExponential(3) + '<br/>'
//    //}
//    //createChart();
//    var chart = $('#container').highcharts();
//    chart.setTitle(title, {'text': 'Logarithmic View'});
//    chart.yAxis[0].setCompare('null');
//    compare = undefined
//
//}

function toPercent() {
    var chart = $('#container').highcharts();
    chart.setTitle(title, {'text': 'Percent compare View'});
    chart.yAxis[0].setCompare('percent');
    chart.series[3].hide();
    compare = 'percent'
}

function toValue() {
    var chart = $('#container').highcharts();
    chart.setTitle(title, {'text': 'Value compare View'});
    chart.series[3].hide();
    chart.yAxis[0].setCompare('value');
    compare = 'value'
}

function toDefault() {
    var chart = $('#container').highcharts();
    chart.setTitle(title);
    chart.series[3].show();
    chart.yAxis[0].setCompare('null');
    compare = undefined
}

function loadjson(json) {
    $(function () {
        $.each(names, function (i, name) {

            //$.getJSON(fname, function(data) {

                seriesOptions[i] = {
                    name: name,
                    data: json['loss'][name],
                };

                for(var item in json.output)
                {
                    outputs[json.output[item][0]] = json.output[item][1];
                }

                // As we're loading the data asynchronously, we don't know what order it will arrive. So
                // we keep a counter and create the chart when all the data is loaded.
                seriesCounter += 1;

                if (seriesCounter === names.length) {
                    createChart();
                    toDefault();
                }
            //});

        });
    });
}

function getOutputs() {
    return outputs;
}

function setOutputs(output) {
    outputs = output;
}

var updater = {
    errorSleepTime: 500,
    cursor: null,

    poll: function() {
        $.ajax({url: "/json", type: "POST", dataType: "text",
            success: updater.onSuccess,
                error: updater.onError});
    },

    onSuccess: function(response) {
        try {
            updater.newMessages(eval("(" + response + ")"));
        } catch (e) {
            updater.onError();
            return;
        }
        updater.errorSleepTime = 500;
        window.setTimeout(updater.poll, 0);
    },

    onError: function(response) {
        updater.errorSleepTime *= 2;
        console.log("Poll error; sleeping for", updater.errorSleepTime, "ms");
        window.setTimeout(updater.poll, updater.errorSleepTime);
    },

    newMessages: function(response) {
        if (!response.messages) return;
        updater.cursor = response.cursor;
        var messages = response.messages;
        updater.cursor = messages[messages.length - 1].id;
        //console.log(messages.length, "new messages, cursor:", updater.cursor);
        for (var i = 0; i < messages.length; i++) {
            updater.showMessage(messages[i]);
        }
    },

    showMessage: function(message) {
        var existing = $("#m" + message.id);
        if (existing.length > 0) return;
        json = message.json;
        //console.log(json)
        var chart = $('#container').highcharts();
        if (json !== undefined) {
            chart.series[0].addPoint([json['iter'], json['losses'][0]]);
            chart.series[1].addPoint([json['iter'], json['losses'][2]]);
            chart.series[2].addPoint([json['iter'], json['losses'][1]]);
            chart.series[3].addPoint([json['iter'], json['losses'][3]]);
            var outputs = getOutputs();
            outputs[json['output'][0]] = json['output'][1];
            setOutputs(outputs);
        }
    }
};

