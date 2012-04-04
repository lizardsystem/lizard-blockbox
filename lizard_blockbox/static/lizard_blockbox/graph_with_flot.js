// jslint configuration
/*jslint browser: true */
/*global $, window */

var console = console || {
  log:function() {},
  warn: function() {},
  dir: function() {},
  error: function() {}
};





var setPlaceholderTop;
var setPlaceholderControl;

var options = {
    xaxis: {
        position: "top"
    },
    grid: {
        clickable: true,
        borderWidth: 1
    },
    legend: {
        show: true,
        noColumns: 4,
        container: $("#placeholder_top_legend"),
        labelFormatter: function(label, series) {
            var cb = label;
            return cb;
        }
    }
};


function setFlotSeries() {
    setPlaceholderTop(json_data.basecase_data, json_data.result_data);
    setPlaceholderControl(json_data.measure_control_data);
}

function refreshGraph() {
    // pl_lines.setData([json_data.basecase_data, json_data.result_data]);
    // pl_lines.setupGrid();
    // pl_lines.draw();

    $.plot($("#placeholder_top"), ed_data, options);
}
    

function setPlaceholderTop(basecase_data, result_data) {
    var d1, d2, d3, d4, d5, area_labels, options, pl, x_min, x_max, y_min, y_max;

    ed_data = [
    {
        data: json_data.basecase_data,
        points: {
            show: true,
            symbol: "diamond"
        },
        lines: {
            show: true
        },
        color: "blue"
    },
    {
        label: "Serie 1",
        data: json_data.result_data,
        points: {
            show: true,
            symbol: "triangle",
            radius: 1
        },
        lines: {
            show: true,
            lineWidth: 2
        },
        color: "red"
    }
    ];
    
    options = {
        xaxis: {
            position: "top"
        },
        grid: {
            clickable: true,
            borderWidth: 1
        },
        legend: {
            show: true,
            noColumns: 4,
            container: $("#placeholder_top_legend"),
            labelFormatter: function(label, series) {
                var cb = label;
                return cb;
            }
        }
    };
    

    pl_lines = $.plot($("#placeholder_top"), ed_data, options);
}

function setPlaceholderControl(control_data) {

    var d1, d2, d3, d4, d5, area_labels, options, options2, ed_data, pl, x_min, x_max, y_min, y_max;
    options = {
        xaxis: {
            position: "bottom"
        },
        grid: {
            clickable: true,
            borderWidth: 1
        },
        legend: {
            show: true,
            noColumns: 4,
            container: $("#placeholder_control_legend"),
            labelFormatter: function(label, series) {
                var cb = label;
                return cb;
            }
        }
    };
    measures_controls = [
    {
        label: "Serie 2",
        data: control_data,
        points: {
            show: true,
            symbol: "square",
            radius: 2
        },
        lines: {
            show: false
        },
        color: "red"
    },
    {
        label: "Serie 3",
        data: d4,
        points: {
            show: true,
            symbol: "triangle",
            radius: 1
        },
        lines: {
            show: false
        },
        color: "green"
    },
    {
        data: d5,
        points: {
            show: false
        },
        lines: {
            show: true,
            lineWidth: 1,
            radius: 1
        },
        color: "gray",
        shadowSize: 0
    }
    ];

    pl_control = $.plot($("#placeholder_control"), measures_controls, options);

    $("#placeholder_control").bind("plotclick",
    function(event, pos, item) {
        if (item) {

            pl_lines.unhighlight(item.series, item.datapoint);
            result_id = item.series.data[item.dataIndex][2].id;
            refreshGraph();
        }
    });
}


function showTooltip(x, y, contents) {
    $('<div id="tooltip">' + contents + '</div>').css({
        position: 'absolute',
        display: 'none',
        top: y - 35,
        left: x + 5,
        border: '1px solid #fdd',
        padding: '2px',
        backgroundcolor: '#fee'
    }).appendTo("body").fadeIn(200);
}


$(document).ready(function() {
    setFlotSeries();
});
