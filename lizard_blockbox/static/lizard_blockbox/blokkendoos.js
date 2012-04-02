(function() {
  var FLOT_URL, JSON_COMBINATIONS_URL, all_selected_measure_ids, available_measure_labels, blockedByList, blockedList, clicked, current_reach_measure_ids, current_reach_measure_ids_clicked, current_reach_measure_ids_unclicked, diffArray, draw_point, getIndicesForCombinations, getTicks, processCompleted, refreshGraph, remove_item_from_array, result_ids, selected_measure_ids, setPlaceholderControl, setPlaceholderTop, setupIfAllDataReady, showTooltip;

  FLOT_URL = "/";

  JSON_COMBINATIONS_URL = "/";

  current_reach_measure_ids = void 0;

  selected_measure_ids = void 0;

  available_measure_labels = {};

  clicked = [];

  blockedList = {};

  blockedByList = {};

  processCompleted = {
    'measuresLoaded': false,
    'combinationsLoaded': false
  };

  diffArray = function(bigArray, smallArray) {
    return $.grep(bigArray, function(bigArrayElement) {
      return $.inArray(bigArrayElement, smallArray) < 0;
    });
  };

  setupIfAllDataReady = function() {
    if (processCompleted.combinationsLoaded && processCompleted.measuresLoaded) {
      return $(document).ready(function() {
        setFlotSeries(FLOT_URL);
        $("#selected_measures").updateMeasuresTable({}, []);
        return $("#other_selected_measures").updateOtherMeasuresTable({}, []);
      });
    }
  };

  jQuery(function($) {
    return $.fn.updateMeasuresTable = function(measure_ids, available_measure_labels) {
      var createSumRow, measure_labels, table, target;
      target = $(this);
      table = $("<table class='generic-table' 'border='0' cellspacing='5' cellpadding='5' id='measure_table'>\n    <thead>\n    <tr class='header'>\n        <th>Maatregel</th>\n        <th>Code</th>\n        <th>Kosten &uarr;</th>\n    </tr>\n    </thead>\n    <tbody/>\n</table>");
      measure_labels = $.map(measure_ids, function(id) {
        return available_measure_labels[id];
      });
      createSumRow = function() {
        var sum;
        sum = 0;
        _.each(measure_labels, function(label) {
          return sum = sum + label[2].cost;
        });
        return target.find("tbody").children().last().parent().append("<tr class='sum'><td><strong>Totaal</strong></td><td></td><td>" + sum.toFixed(1) + " mln</td></tr>");
      };
      target.empty();
      target.html(table);
      _.each(measure_labels, function(label) {
        return target.find("tbody").append("<tr class='row'><td>" + label[2].title + "</td><td>" + label[2].code + "</td><td>" + label[2].cost + " mln</td></tr>");
      });
      createSumRow();
      if (_.isEmpty(measure_ids)) {
        target.find("tbody").append("<tr class='row'><td>...</td><td>...</td><td>...</td></tr>");
      }
      return this;
    };
  });

  jQuery(function($) {
    return $.fn.updateOtherMeasuresTable = function(measure_ids, selected_measure_labels) {
      var createSumRow, measure_labels, table, target;
      target = $(this);
      table = $("<table border='0' cellspacing='5' cellpadding='5' id='other_measure_table'>\n    <thead>\n    <tr class='header'>\n        <th>Maatregel</th>\n        <th>Code</th>\n        <th>Kosten &uarr;</th>\n    </tr>\n    </thead>\n    <tbody/>\n</table>");
      measure_labels = $.map(measure_ids, function(id) {
        return available_measure_labels[id];
      });
      createSumRow = function() {
        var sum;
        sum = 0;
        _.each(measure_labels, function(label) {
          return sum = sum + label[2].cost;
        });
        return target.find("tbody").children().last().parent().append("<tr class='sum'><td><strong>Totaal</strong></td><td></td><td>" + sum.toFixed(1) + " mln</td></tr>");
      };
      target.empty();
      target.html(table);
      _.each(measure_labels, function(label) {
        return target.find("tbody").append("<tr class='row'><td>" + label[2].title + "</td><td>" + label[2].code + "</td><td>" + label[2].cost + " mln</td></tr>");
      });
      createSumRow();
      if (_.isEmpty(measure_labels)) {
        target.find("tbody").append("<tr class='row'><td>...</td><td>...</td><td>...</td></tr>");
      }
      return this;
    };
  });

  jQuery.getJSON(FLOT_URL, {}, function(json, textStatus) {
    var json_data;
    json_data = json;
    current_reach_measure_ids = $.map(json_data.measure_control_data, function(label) {
      var id;
      id = label[2].id;
      available_measure_labels[id] = [label];
      return id;
    });
    selected_measure_ids = $.map(json_data.selected_measures, function(label) {
      var id;
      id = label[2].id;
      available_measure_labels[id] = [label];
      return id;
    });
    processCompleted.measuresLoaded = true;
    return setupIfAllDataReady();
  });

  jQuery.getJSON(JSON_COMBINATIONS_URL, {}, function(json, textStatus) {
    var combinations;
    combinations = json;
    processCompleted.combinationsLoaded = true;
    return setupIfAllDataReady();
  });

  showTooltip = function(x, y, contents) {
    return $("<div id=\"tooltip\">" + contents + "</div>").css({
      opacity: "1.00",
      position: "absolute",
      display: "none",
      top: y - 35,
      left: x + 5,
      border: "1px solid #046f96",
      padding: "2px",
      backgroundcolor: "#fee"
    }).appendTo("body").fadeIn(200);
  };

  remove_item_from_array = function(array, removeItem) {
    return $.grep(array, function(value) {
      return value !== removeItem;
    });
  };

  draw_point = function(datapoint, plotobj, fillcolor, radius, linewidth, linecolor) {
    var axes, ctx, offset, x, y;
    axes = plotobj.getAxes();
    ctx = plotobj.getCanvas().getContext("2d");
    offset = plotobj.getPlotOffset();
    x = offset.left + axes.xaxis.p2c(datapoint[0]);
    y = offset.top + axes.yaxis.p2c(datapoint[1]);
    ctx.lineWidth = linewidth;
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, Math.PI * 2, false);
    ctx.closePath();
    ctx.fillStyle = fillcolor;
    ctx.strokeStyle = linecolor;
    ctx.fill();
    ctx.stroke();
    return true;
  };

  getIndicesForCombinations = function(series_data, combos) {
    var indices;
    indices = [];
    _.each(series_data, function(value, counter) {
      if (_.include(_.flatten(combos), value[2].code)) {
        return indices.push(counter);
      }
    });
    return indices;
  };

  refreshGraph = function(data) {
    pl_lines.setData([
      {
        data: data.basecase_data,
        points: {
          show: true,
          symbol: "diamond"
        },
        lines: {
          show: true
        },
        color: "blue"
      }, {
        data: data.result_data,
        points: {
          show: true,
          symbol: "circle"
        },
        lines: {
          show: true
        },
        color: "yellow"
      }
    ]);
    pl_lines.setupGrid();
    pl_lines.draw();
    return pl_linesx;
  };

  window.setFlotSeries = function(url) {
    $.ajax({
      type: "POST",
      url: url,
      dataType: "json",
      success: function(data) {
        if (data.basecase_data.length) {
          setPlaceholderTop(data.basecase_data, data.result_data);
          setPlaceholderControl(data.measure_control_data);
          return refreshGraph(data);
        } else {
          return $("#graph_errors").html("<p class=\"error\">\n    Geen basis data beschikbaar voor deze raai.\n</p>");
        }
      }
    });
    return {
      error: function(data) {
        return $("#graph_errors").html("<p class=\"error\">\n    Geen data gevonden voor deze raai en dit toekomstbeeld\n</p>");
      }
    };
  };

  setPlaceholderTop = function(basecase_data, result_data) {
    var ed_data, options, pl_lines;
    options = void 0;
    ed_data = void 0;
    options = {
      xaxis: {
        transform: function(v) {
          return -v;
        },
        position: "top"
      },
      yaxis: {
        min: -1,
        max: 1,
        reserveSpace: true,
        labelWidth: 21
      },
      grid: {
        clickable: true,
        borderWidth: 1
      },
      legend: {
        show: true,
        noColumns: 4,
        container: $("#placeholder_top_legend")
      }
    };
    ed_data = [
      {
        data: json_data.basecase_data,
        label: "Uitgangssituatie",
        points: {
          show: true,
          symbol: "diamond"
        },
        lines: {
          show: true
        },
        color: "blue"
      }
    ];
    return pl_lines = $.plot($("#placeholder_top"), ed_data, options);
  };

  getTicks = function() {
    var ticks;
    ticks = [];
    _.each(json_data.measure_control_data, function(val, count) {
      return ticks[val[1]] = [val[1], val[2].type];
    });
    ticks = remove_item_from_array(ticks, undefined);
    return ticks;
  };

  setPlaceholderControl = function(control_data) {
    var add_code_to_bbl, add_code_to_blockedlist, current_reach_selected_measure_ids, ed_data, highlight_initial, highlight_point_on_click, measure_controls, options, other_measures, other_reach_measure_ids_selected, pl_control, x_max, x_min, y_max, y_min;
    add_code_to_blockedlist = function(key, value) {
      if (!blockedList[key]) blockedList[key] = [];
      if (!_.include(blockedList[key], [value])) blockedList[key].push(value);
      return blockedList;
    };
    add_code_to_bbl = function(key, value) {
      if (!blockedByList[key]) blockedByList[key] = [];
      if (!_.include(blockedByList[key], [value])) blockedByList[key].push(value);
      return blockedByList;
    };
    highlight_initial = function(item, id) {
      var code, combos, indices;
      if (_.include(selected_measure_ids, item[2].id)) {
        clicked.push(id);
        code = item[2].code;
        combos = [combinations[0][code]];
        indices = getIndicesForCombinations(pl_control.getData()[0].data, combos);
        _.each(indices, function(value, count) {
          var loopcode;
          loopcode = pl_control.getData()[0].data[value][2].code;
          add_code_to_blockedlist(code, loopcode);
          add_code_to_bbl(loopcode, code);
          return draw_point(pl_control.getData()[0].data[value], pl_control, "orange", pl_control.getData()[0].points.radius, pl_control.getData()[0].points.lineWidth, pl_control.getData()[0].color);
        });
        return draw_point(item, pl_control, "blue", pl_control.getData()[0].points.radius, pl_control.getData()[0].points.lineWidth, pl_control.getData()[0].color);
      }
    };
    highlight_point_on_click = function(item) {
      var code, combos, current_reach_selected_measure_ids, current_reach_selected_measures, indices, other_measures;
      clicked.push(item.dataIndex);
      other_measures = [];
      current_reach_selected_measures = [];
      current_reach_selected_measure_ids = [];
      _.each(clicked, function(val, counter) {
        current_reach_selected_measures.push(item.series.data[val][2]);
        return current_reach_selected_measure_ids.push(item.series.data[val][2].id);
      });
      $("#selected_measures").updateMeasuresTable(current_reach_selected_measure_ids, available_measure_labels);
      code = item.series.data[item.dataIndex][2].code;
      combos = [combinations[0][code]];
      indices = getIndicesForCombinations(item.series.data, combos);
      _.each(indices, function(value, count) {
        var loopcode;
        loopcode = item.series.data[value][2].code;
        add_code_to_blockedlist(code, loopcode);
        add_code_to_bbl(loopcode, code);
        return draw_point(item.series.data[value], pl_control, "orange", item.series.points.radius, item.series.points.lineWidth, item.series.color);
      });
      return draw_point(item.datapoint, pl_control, "blue", item.series.points.radius, item.series.points.lineWidth, item.series.color);
    };
    options = void 0;
    ed_data = void 0;
    x_min = void 0;
    x_max = void 0;
    y_min = void 0;
    y_max = void 0;
    options = {
      xaxis: {
        transform: function(v) {
          return -v;
        },
        inverseTransform: function(v) {
          return -v;
        },
        show: true,
        position: "bottom",
        labelWidth: 50,
        min: pl_lines.getAxes().xaxis.min,
        max: pl_lines.getAxes().xaxis.max
      },
      yaxis: {
        reserveSpace: true,
        labelWidth: 21,
        position: "left",
        show: false
      },
      grid: {
        clickable: true,
        hoverable: true,
        borderWidth: 1
      },
      legend: {
        show: true,
        noColumns: 4,
        container: $("#placeholder_control_legend"),
        labelFormatter: function(label, series) {
          var cb;
          cb = label;
          return cb;
        }
      }
    };
    measure_controls = [
      {
        label: "Serie 2",
        data: control_data,
        points: {
          show: true,
          symbol: "circle",
          radius: 5,
          lineWidth: 2
        },
        lines: {
          show: false
        },
        color: "red"
      }
    ];
    pl_control = $.plot($("#placeholder_control"), measure_controls, options);
    $("#placeholder_control").bind("plothover", function(event, pos, item) {
      if (item) {
        $("#tooltip").remove();
        return showTooltip(item.pageX, item.pageY, item.series.data[item.dataIndex][2].code + " (" + item.series.data[item.dataIndex][2].title + ")");
      } else {
        return $("#tooltip").remove();
      }
    });
    other_measures = [];
    _.each(pl_control.getData()[0].data, function(val, id) {
      return highlight_initial(val, id);
    });
    current_reach_selected_measure_ids = $.map(clicked, function(i) {
      return pl_control.getData()[0].data[i][2].id;
    });
    $("#selected_measures").updateMeasuresTable(current_reach_selected_measure_ids, available_measure_labels);
    other_reach_measure_ids_selected = _.difference(selected_measure_ids, current_reach_selected_measure_ids);
    $("#other_selected_measures").updateOtherMeasuresTable(other_reach_measure_ids_selected, json_data.selected_measures);
    return $("#placeholder_control").bind("plotclick", function(event, pos, item) {
      var axes, code, ctx, idx, offset, point_is_selected;
      if (!item) return false;
      if (_.include(_.keys(blockedByList), item.series.data[item.dataIndex][2].code)) {
        return false;
      }
      point_is_selected = _.include(clicked, item.dataIndex);
      if (!point_is_selected) {
        highlight_point_on_click(item);
      } else {
        idx = $.inArray(item.dataIndex, clicked);
        if (idx !== -1) clicked.splice(idx, 1);
        axes = pl_control.getAxes();
        ctx = pl_control.getCanvas().getContext("2d");
        offset = pl_control.getPlotOffset();
        code = item.series.data[item.dataIndex][2].code;
        draw_point(item.datapoint, pl_control, "white", item.series.points.radius, item.series.points.lineWidth, item.series.color);
        current_reach_selected_measure_ids = $.map(clicked, function(id) {
          return item.series.data[id][2].id;
        });
        $("#selected_measures").updateMeasuresTable(current_reach_selected_measure_ids, available_measure_labels);
        _.each(blockedList[code], function(blocked_item, counter) {
          var different;
          different = _.difference(blockedByList[blocked_item], [code]);
          if (different.length === 0) {
            return _.each(item.series.data, function(datapoint, counter) {
              if (datapoint[2].code === blocked_item) {
                draw_point(datapoint, pl_control, "white", item.series.points.radius, item.series.points.lineWidth, item.series.color);
                blockedByList[blocked_item] = remove_item_from_array(blockedByList[blocked_item], code);
                if (blockedByList[blocked_item].length === 0) {
                  return delete blockedByList[blocked_item];
                }
              }
            });
          }
        });
      }
      return delete blockedList[code];
    });
  };

  result_ids = [];

  _.each(clicked, function(value, counter) {
    return result_ids.push(item.series.data[value][2].id);
  });

  result_ids = result_ids.join(",");

  current_reach_measure_ids_clicked = [];

  _.each(clicked, function(i) {
    return current_reach_measure_ids_clicked.push(item.series.data[i][2].id);
  });

  current_reach_measure_ids_unclicked = _.difference(current_reach_measure_ids, current_reach_measure_ids_clicked);

  all_selected_measure_ids = _.difference(_.union(selected_measure_ids, current_reach_measure_ids_clicked), current_reach_measure_ids_unclicked);

  $.post(FLOT_URL, {
    has_measures: true,
    measures: all_selected_measure_ids
  }, (function(data) {}, refreshGraph(data)), "json");

}).call(this);
