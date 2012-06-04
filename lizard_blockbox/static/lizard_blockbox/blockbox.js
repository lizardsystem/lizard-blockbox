(function() {
  var ANIMATION_DURATION, BLACK, BLUE, BlockboxRouter, DARKGREEN, DARKRED, DIAMOND_COLOR, GRAY, GREEN, JSONLayer, JSONRiverLayer, JSONTooltip, LIGHTBLUE, LIGHTGREEN, LIGHTRED, MIDDLEGREEN, MIDDLERED, MeasuresMapView, PURPLE, RED, RiverLayerBorderRule, RiverLayerRule, SQUARE_COLOR, STROKEWIDTH, TRIANGLE_COLOR, YELLOW, doit, graphTimer, hasTooltip, measuresMapView, onFeatureHighlight, onFeatureToggle, onFeatureUnhighlight, onPopupClose, resize_graphs, selectRiver, selectVertex, setFlotSeries, setMeasureGraph, setMeasureResultsGraph, setMeasureSeries, showLabel, showTooltip, toggleMeasure, updateVertex,
    __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; },
    __indexOf = Array.prototype.indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

  ANIMATION_DURATION = 150;

  GRAY = "#c0c0bc";

  BLUE = "#046F96";

  LIGHTBLUE = "#bddfed";

  RED = "#A31535";

  YELLOW = "#E2D611";

  GREEN = "#635E0D";

  LIGHTRED = "#A36775";

  MIDDLERED = "#A33E56";

  DARKRED = RED;

  LIGHTGREEN = "#63623F";

  MIDDLEGREEN = "#636026";

  DARKGREEN = GREEN;

  DIAMOND_COLOR = "#105987";

  TRIANGLE_COLOR = "#E78B00";

  SQUARE_COLOR = "#122F64";

  PURPLE = "#E01B6A";

  BLACK = "#000000";

  STROKEWIDTH = 5;

  graphTimer = '';

  hasTooltip = '';

  toggleMeasure = function(measure_id) {
    return $.ajax({
      type: 'POST',
      url: $('#blockbox-table').data('measure-toggle-url'),
      data: {
        'measure_id': measure_id
      },
      success: function(data) {
        var $holder;
        setFlotSeries();
        $holder = $('<div/>');
        $holder.load('. #page', function() {
          return $("#selected-measures-list").html($('#selected-measures-list', $holder).html());
        });
        measuresMapView.render();
        return this;
      }
    });
  };

  selectRiver = function(river_name) {
    return $.ajax({
      type: 'POST',
      url: $('#blockbox-river').data('select-river-url'),
      data: {
        'river_name': river_name
      },
      success: function(data) {
        setFlotSeries();
        measuresMapView.render();
        return this;
      }
    });
  };

  selectVertex = function(vertex_id) {
    return $.ajax({
      type: 'POST',
      url: $('#blockbox-vertex').data('select-vertex-url'),
      data: {
        'vertex': vertex_id
      },
      success: function(data) {
        setFlotSeries();
        measuresMapView.render();
        return this;
      }
    });
  };

  updateVertex = function() {
    return $.getJSON($('#blockbox-vertex').data('update-vertex-url'), function(data) {
      var html, id, name, options;
      options = (function() {
        var _results;
        _results = [];
        for (id in data) {
          name = data[id];
          _results.push("<option value='" + id + "'>" + name + "</option>");
        }
        return _results;
      })();
      html = options.join("");
      console.log(html);
      $('#blockbox-vertex select').html(html);
      return $('#blockbox-vertex .chzn-select').trigger("liszt:updated");
    });
  };

  BlockboxRouter = (function(_super) {

    __extends(BlockboxRouter, _super);

    function BlockboxRouter() {
      BlockboxRouter.__super__.constructor.apply(this, arguments);
    }

    BlockboxRouter.prototype.routes = {
      "map": "map",
      "table": "table"
    };

    BlockboxRouter.prototype.map = function() {
      var to_table_text;
      to_table_text = $('.toggle_map_and_table').parent().data('to-table-text');
      $('a.toggle_map_and_table span').text(to_table_text);
      $('a.toggle_map_and_table').attr("href", "#table");
      return $('#blockbox-table').slideUp(ANIMATION_DURATION, function() {
        return $('#map').slideDown(ANIMATION_DURATION);
      });
    };

    BlockboxRouter.prototype.table = function() {
      var to_map_text;
      to_map_text = $('.toggle_map_and_table').parent().data('to-map-text');
      $('a.toggle_map_and_table span').text(to_map_text);
      $('a.toggle_map_and_table').attr("href", "#map");
      return $('#map').slideUp(ANIMATION_DURATION, function() {
        return $('#blockbox-table').slideDown(ANIMATION_DURATION, function() {
          return $('#blockbox-table').height($("#content").height() - 250 - 39);
        });
      });
    };

    return BlockboxRouter;

  })(Backbone.Router);

  window.app_router = new BlockboxRouter;

  Backbone.history.start();

  MeasuresMapView = Backbone.View.extend({
    measures: function() {
      var _this = this;
      return $.getJSON(this.static_url + 'lizard_blockbox/measures.json', function(json) {
        _this.measures = JSONTooltip('Maatregelen', json);
        return _this.render_measures(_this.measures);
      });
    },
    selected_items: function() {
      var el, _i, _len, _ref, _results;
      _ref = $("#selected-measures-list li a");
      _results = [];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        el = _ref[_i];
        _results.push($(el).data("measure-shortname"));
      }
      return _results;
    },
    render_rivers: function(rivers) {
      var json_url;
      if (rivers == null) rivers = this.Rivers;
      json_url = $('#blockbox-table').data('calculated-measures-url');
      return $.getJSON(json_url, function(data) {
        var attributes, feature, num, target_difference, _i, _j, _len, _len2, _ref;
        target_difference = {};
        for (_i = 0, _len = data.length; _i < _len; _i++) {
          num = data[_i];
          target_difference[num.location_reach] = num.measures_level;
        }
        _ref = rivers.features;
        for (_j = 0, _len2 = _ref.length; _j < _len2; _j++) {
          feature = _ref[_j];
          attributes = feature.attributes;
          attributes.target_difference = target_difference[attributes.MODELKM];
        }
        return rivers.redraw();
      });
    },
    render_measures: function(measures) {
      var feature, selected_items, _i, _len, _ref, _ref2;
      if (measures == null) measures = this.measures;
      selected_items = this.selected_items();
      _ref = measures.features;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        feature = _ref[_i];
        if (_ref2 = feature.attributes.code, __indexOf.call(selected_items, _ref2) >= 0) {
          feature.attributes.selected = true;
        } else {
          feature.attributes.selected = false;
        }
      }
      return measures.redraw();
    },
    rivers: function() {
      var _this = this;
      return $.getJSON(this.static_url + 'lizard_blockbox/kilometers.json', function(json) {
        _this.Rivers = JSONRiverLayer('Rivers', json);
        return _this.render_rivers(_this.Rivers);
      });
    },
    initialize: function() {
      var runDelayed,
        _this = this;
      this.static_url = $('#lizard-blockbox-graph').data('static-url');
      runDelayed = function() {
        _this.measures();
        return _this.rivers();
      };
      return setTimeout(runDelayed, 500);
    },
    render: function() {
      this.render_measures();
      return this.render_rivers();
    }
  });

  measuresMapView = new MeasuresMapView();

  onPopupClose = function(evt) {
    return selectControl.unselect(selectedFeature);
  };

  onFeatureHighlight = function(feature) {
    var ff, popup, selectedFeature;
    selectedFeature = feature;
    ff = feature.feature;
    popup = new OpenLayers.Popup.FramedCloud("chicken", ff.geometry.getBounds().getCenterLonLat(), null, "<div style='font-size:.8em'>" + ff.data.titel + "</div>", null, false, false);
    feature.feature.popup = popup;
    return map.addPopup(popup);
  };

  onFeatureUnhighlight = function(feature) {
    map.removePopup(feature.feature.popup);
    feature.feature.popup.destroy();
    return feature.feature.popup = null;
  };

  onFeatureToggle = function(feature) {
    var attr, short_name;
    attr = feature.attributes;
    short_name = attr["code"];
    return toggleMeasure(short_name);
  };

  JSONLayer = function(name, json) {
    var geojson_format, vector_layer;
    geojson_format = new OpenLayers.Format.GeoJSON();
    vector_layer = new OpenLayers.Layer.Vector(name);
    map.addLayer(vector_layer);
    return vector_layer.addFeatures(geojson_format.read(json));
  };

  RiverLayerRule = function(from, to, color) {
    var rule;
    rule = new OpenLayers.Rule({
      filter: new OpenLayers.Filter.Comparison({
        type: OpenLayers.Filter.Comparison.BETWEEN,
        property: "target_difference",
        lowerBoundary: from,
        upperBoundary: to
      }),
      symbolizer: {
        fillColor: color,
        strokeColor: color,
        strokeWidth: STROKEWIDTH
      }
    });
    return rule;
  };

  RiverLayerBorderRule = function(to, color) {
    var rule;
    rule = new OpenLayers.Rule({
      filter: new OpenLayers.Filter.Comparison({
        type: OpenLayers.Filter.Comparison.EQUAL_TO,
        property: "target_difference",
        value: to
      }),
      symbolizer: {
        fillColor: color,
        strokeColor: color
      }
    });
    return rule;
  };

  JSONRiverLayer = function(name, json) {
    var geojson_format, rules, styleMap, vector_layer;
    rules = [
      RiverLayerRule(1.00, 1.50, DARKRED), RiverLayerRule(0.50, 1.00, MIDDLERED), RiverLayerRule(0.10, 0.50, LIGHTRED), RiverLayerRule(-0.10, 0.10, BLUE), RiverLayerRule(-0.50, -0.10, LIGHTGREEN), RiverLayerRule(-1.00, -0.50, MIDDLEGREEN), RiverLayerRule(-1.50, -1.00, DARKGREEN), new OpenLayers.Rule({
        elseFilter: true,
        symbolizer: {
          fillColor: GRAY,
          strokeColor: GRAY,
          strokeWidth: STROKEWIDTH
        }
      })
    ];
    styleMap = new OpenLayers.StyleMap(OpenLayers.Util.applyDefaults({
      fillColor: GRAY,
      strokeColor: GRAY,
      strokeWidth: STROKEWIDTH
    }, OpenLayers.Feature.Vector.style["default"]));
    styleMap.styles["default"].addRules(rules);
    geojson_format = new OpenLayers.Format.GeoJSON();
    vector_layer = new OpenLayers.Layer.Vector(name, {
      styleMap: styleMap
    });
    map.addLayer(vector_layer);
    vector_layer.addFeatures(geojson_format.read(json));
    return vector_layer;
  };

  JSONTooltip = function(name, json) {
    var geojson_format, highlightCtrl, styleMap, vector_layer;
    styleMap = new OpenLayers.StyleMap(OpenLayers.Util.applyDefaults({
      fillColor: GREEN,
      strokeColor: GREEN
    }, OpenLayers.Feature.Vector.style["default"]));
    styleMap.styles["default"].addRules([
      new OpenLayers.Rule({
        filter: new OpenLayers.Filter.Comparison({
          type: OpenLayers.Filter.Comparison.EQUAL_TO,
          property: "selected",
          value: true
        }),
        symbolizer: {
          fillColor: RED,
          strokeColor: RED
        }
      }), new OpenLayers.Rule({
        elseFilter: true
      })
    ]);
    geojson_format = new OpenLayers.Format.GeoJSON();
    vector_layer = new OpenLayers.Layer.Vector(name, {
      styleMap: styleMap
    });
    map.addLayer(vector_layer);
    vector_layer.addFeatures(geojson_format.read(json));
    highlightCtrl = new OpenLayers.Control.SelectFeature(vector_layer, {
      hover: true,
      highlightOnly: true,
      renderIntent: "temporary",
      eventListeners: {
        featurehighlighted: onFeatureHighlight,
        featureunhighlighted: onFeatureUnhighlight
      }
    });
    map.addControl(highlightCtrl);
    highlightCtrl.activate();
    return vector_layer;
  };

  showLabel = function(x, y, contents) {
    return $('<div id="label">#{contents}</div>').css({
      position: 'absolute',
      display: 'none',
      top: y + 5,
      left: x + 250,
      border: '1px solid #fdd',
      padding: '2px',
      'background-color': '#fee',
      opacity: 0.80
    });
  };

  showTooltip = function(x, y, name, type_name) {
    return $("<div id=\"tooltip\" class=\"popover top\">\n  <div class=\"popover-inner\">\n    <div class=\"popover-title\"><h3>" + name + "</h3></div>\n    <div class=\"popover-content\">Type: " + type_name + "</div>\n  </div>\n</div>").css({
      top: y - 35,
      left: x + 5
    }).appendTo("body").fadeIn(200);
  };

  setFlotSeries = function() {
    var json_url;
    json_url = $('#blockbox-table').data('calculated-measures-url');
    return $.getJSON(json_url, function(data) {
      window.min_graph_value = data[0].location;
      window.max_graph_value = data[data.length - 1].location;
      setMeasureResultsGraph(data);
      return setMeasureSeries();
    });
  };

  setMeasureSeries = function() {
    var cities_list_url, json_url;
    json_url = $('#blockbox-table').data('measure-list-url');
    cities_list_url = $('#blockbox-table').data('cities-list-url');
    return $.getJSON(json_url, function(data) {
      return $.getJSON(cities_list_url, function(cities) {
        return setMeasureGraph(data, cities);
      });
    });
  };

  setMeasureResultsGraph = function(json_data) {
    var cities, ed_data, measures, num, options, pl_lines, reference, selected_river, vertex;
    vertex = (function() {
      var _i, _len, _results;
      _results = [];
      for (_i = 0, _len = json_data.length; _i < _len; _i++) {
        num = json_data[_i];
        _results.push([num.location, num.vertex_level]);
      }
      return _results;
    })();
    reference = (function() {
      var _i, _len, _results;
      _results = [];
      for (_i = 0, _len = json_data.length; _i < _len; _i++) {
        num = json_data[_i];
        _results.push([num.location, num.reference_target]);
      }
      return _results;
    })();
    measures = (function() {
      var _i, _len, _results;
      _results = [];
      for (_i = 0, _len = json_data.length; _i < _len; _i++) {
        num = json_data[_i];
        _results.push([num.location, num.measures_level]);
      }
      return _results;
    })();
    cities = (function() {
      var _i, _len, _results;
      _results = [];
      for (_i = 0, _len = json_data.length; _i < _len; _i++) {
        num = json_data[_i];
        _results.push([num.location, num.city]);
      }
      return _results;
    })();
    selected_river = $("#blockbox-river .chzn-select")[0].value;
    ed_data = [
      {
        data: vertex,
        points: {
          show: false
        },
        lines: {
          show: true
        },
        color: GRAY
      }, {
        label: "Doelwaarde",
        data: reference,
        points: {
          show: false
        },
        lines: {
          show: true,
          lineWidth: 2
        },
        color: BLUE
      }, {
        label: "Effect maatregelen",
        data: measures,
        points: {
          show: false
        },
        lines: {
          show: true,
          lineWidth: 2
        },
        color: RED
      }
    ];
    options = {
      xaxis: {
        min: window.min_graph_value,
        max: window.max_graph_value,
        transform: function(v) {
          if (selected_river === 'Maas') {
            return -v;
          } else {
            return v;
          }
        },
        inverseTransform: function(v) {
          if (selected_river === 'Maas') {
            return -v;
          } else {
            return v;
          }
        },
        position: "top"
      },
      yaxis: {
        labelWidth: 21,
        reserveSpace: true,
        position: "left",
        tickDecimals: 1
      },
      grid: {
        minBorderMargin: 20,
        clickable: true,
        borderWidth: 1,
        axisMargin: 10
      },
      legend: {
        container: $("#measure_results_graph_legend"),
        labelFormatter: function(label, series) {
          var cb;
          cb = label;
          return cb;
        }
      }
    };
    pl_lines = $.plot($("#measure_results_graph"), ed_data, options);
    return window.topplot = pl_lines;
  };

  setMeasureGraph = function(control_data, cities_data) {
    var cities, city, d4, d5, key, label_mapping, measure, measures, measures_controls, non_selectable_measures, num, options, pl_control, pl_lines, previousPoint, selected_measures, selected_river, value, yticks, _i, _len;
    measures = (function() {
      var _i, _len, _results;
      _results = [];
      for (_i = 0, _len = control_data.length; _i < _len; _i++) {
        num = control_data[_i];
        if (num.selectable && !num.selected) {
          _results.push([num.km_from, num.type_index, num.name, num.short_name, num.measure_type]);
        }
      }
      return _results;
    })();
    selected_measures = (function() {
      var _i, _len, _results;
      _results = [];
      for (_i = 0, _len = control_data.length; _i < _len; _i++) {
        num = control_data[_i];
        if (num.selected) {
          _results.push([num.km_from, num.type_index, num.name, num.short_name, num.measure_type]);
        }
      }
      return _results;
    })();
    non_selectable_measures = (function() {
      var _i, _len, _results;
      _results = [];
      for (_i = 0, _len = control_data.length; _i < _len; _i++) {
        num = control_data[_i];
        if (!num.selectable) {
          _results.push([num.km_from, num.type_index, num.name, num.short_name, num.measure_type]);
        }
      }
      return _results;
    })();
    cities = (function() {
      var _i, _len, _results;
      _results = [];
      for (_i = 0, _len = cities_data.length; _i < _len; _i++) {
        city = cities_data[_i];
        _results.push([city[0], 8, city[1], city[1], "Stad"]);
      }
      return _results;
    })();
    label_mapping = {};
    for (_i = 0, _len = control_data.length; _i < _len; _i++) {
      measure = control_data[_i];
      label_mapping[measure.type_index] = measure.type_indicator;
    }
    yticks = (function() {
      var _results;
      _results = [];
      for (key in label_mapping) {
        value = label_mapping[key];
        _results.push([key, value]);
      }
      return _results;
    })();
    console.log(yticks);
    selected_river = $("#blockbox-river .chzn-select")[0].value;
    d4 = void 0;
    d5 = void 0;
    pl_lines = void 0;
    options = {
      xaxis: {
        min: window.min_graph_value,
        max: window.max_graph_value,
        transform: function(v) {
          if (selected_river === 'Maas') {
            return -v;
          } else {
            return v;
          }
        },
        inverseTransform: function(v) {
          if (selected_river === 'Maas') {
            return -v;
          } else {
            return v;
          }
        },
        reserveSpace: true,
        position: "bottom"
      },
      yaxis: {
        reserveSpace: true,
        labelWidth: 21,
        position: "left",
        tickDecimals: 0,
        ticks: yticks
      },
      grid: {
        minBorderMargin: 20,
        clickable: true,
        hoverable: true,
        borderWidth: 1
      },
      legend: {
        container: $("#measures_legend")
      }
    };
    measures_controls = [
      {
        label: "Steden",
        data: cities,
        points: {
          show: true,
          symbol: "circle",
          radius: 3,
          fill: 1,
          fillColor: BLACK
        },
        lines: {
          show: false
        },
        color: BLACK
      }, {
        label: "Maatregelen",
        data: measures,
        points: {
          show: true,
          symbol: "square",
          radius: 2,
          fill: 1,
          fillColor: BLUE
        },
        lines: {
          show: false
        },
        color: BLUE
      }, {
        label: "Geselecteerde maatregelen",
        data: selected_measures,
        points: {
          show: true,
          symbol: "diamond",
          radius: 4,
          fill: true
        },
        lines: {
          show: false
        },
        color: RED
      }, {
        label: "Niet-selecteerbare maatregelen",
        data: non_selectable_measures,
        points: {
          show: true,
          symbol: "cross",
          radius: 4
        },
        lines: {
          show: false
        },
        color: GRAY
      }
    ];
    pl_control = $.plot($("#measure_graph"), measures_controls, options);
    $("#measure_graph").bind("plotclick", function(event, pos, item) {
      var callback, measure_id, result_id;
      if (item) {
        if (item.series.label === "Steden") return;
        pl_control.unhighlight(item.series, item.datapoint);
        result_id = item.series.data[item.dataIndex][1];
        measure_id = item.series.data[item.dataIndex][3];
        if (!graphTimer) {
          callback = function() {
            toggleMeasure(measure_id);
            return graphTimer = '';
          };
          return graphTimer = setTimeout(callback, 200);
        }
      }
    });
    previousPoint = null;
    return $("#measure_graph").bind("plothover", function(event, pos, item) {
      var x, y;
      if (item) {
        if (item.pageX > ($(window).width() - 300)) item.pageX = item.pageX - 300;
        if (previousPoint !== item.dataIndex) {
          previousPoint = item.dataIndex;
          $("#tooltip").remove();
          x = item.datapoint[0].toFixed(2);
          y = item.datapoint[1].toFixed(2);
          return showTooltip(item.pageX, item.pageY, item.series.data[item.dataIndex][2], item.series.data[item.dataIndex][4]);
        }
      } else {
        $("#tooltip").remove();
        return previousPoint = null;
      }
    });
  };

  resize_graphs = function() {
    var doit;
    clearTimeout(doit);
    return doit = setTimeout(function() {
      $('#measure_results_graph').empty();
      $('#measure_graph').empty();
      $('#measure_results_graph').css('width', '100%');
      $('#measure_graph').css('width', '100%');
      return setFlotSeries();
    }, 200);
  };

  $('.btn.collapse-sidebar').click(function() {
    return resize_graphs();
  });

  $('.btn.collapse-rightbar').click(function() {
    return resize_graphs();
  });

  doit = void 0;

  $(window).resize(function() {
    return resize_graphs();
  });

  $(".blockbox-toggle-measure").live('click', function(e) {
    e.preventDefault();
    return toggleMeasure($(this).data('measure-id'));
  });

  $(document).ready(function() {
    setFlotSeries();
    $("#blockbox-river .chzn-select").chosen().change(function() {
      selectRiver(this.value);
      return updateVertex();
    });
    updateVertex();
    $("#blockbox-vertex .chzn-select").chosen().change(function() {
      return selectVertex(this.value);
    });
    $('#measures-table-top').tablesorter();
    return this;
  });

}).call(this);
