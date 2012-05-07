(function() {
  var ANIMATION_DURATION, BLUE, BlockboxRouter, DARKGREEN, DARKRED, DIAMOND_COLOR, GRAY, GREEN, JSONLayer, JSONRiverLayer, JSONTooltip, LIGHTBLUE, LIGHTGREEN, LIGHTRED, MIDDLEGREEN, MIDDLERED, MeasuresMapView, RED, RiverLayerBorderRule, RiverLayerRule, SQUARE_COLOR, TRIANGLE_COLOR, YELLOW, doit, graphTimer, hasTooltip, measuresMapView, onFeatureHighlight, onFeatureToggle, onFeatureUnhighlight, onPopupClose, resize_placeholder, selectRiver, setFlotSeries, setMeasureSeries, setPlaceholderControl, setPlaceholderTop, showTooltip, toggleMeasure,
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

  graphTimer = '';

  hasTooltip = '';

  toggleMeasure = function(measure_id) {
    return $.ajax({
      type: 'POST',
      url: $('#blockbox-table').attr('data-measure-toggle-url'),
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
      to_table_text = $('.toggle_map_and_table').parent().attr('data-to-table-text');
      $('a.toggle_map_and_table span').text(to_table_text);
      $('a.toggle_map_and_table').attr("href", "#table");
      return $('#blockbox-table').slideUp(ANIMATION_DURATION, function() {
        return $('#map').slideDown(ANIMATION_DURATION);
      });
    };

    BlockboxRouter.prototype.table = function() {
      var to_map_text;
      to_map_text = $('.toggle_map_and_table').parent().attr('data-to-map-text');
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
      $.getJSON(this.static_url + 'lizard_blockbox/IVM_deel1.json', function(json) {
        _this.IVM = JSONTooltip('IVM deel 1', json);
        return _this.render_measure_IVM(_this.IVM);
      });
      $.getJSON(this.static_url + 'lizard_blockbox/QS.json', function(json) {
        _this.QS = JSONTooltip('QS', json);
        return _this.render_measure_QS(_this.QS);
      });
      return $.getJSON(this.static_url + 'lizard_blockbox/PKB_LT.json', function(json) {
        _this.PKB = JSONTooltip('PKB', json);
        return _this.render_measure_PKB(_this.PKB);
      });
    },
    selected_items: function() {
      var el, _i, _len, _ref, _results;
      _ref = $("#selected-measures-list li a");
      _results = [];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        el = _ref[_i];
        _results.push($(el).attr("data-measure-shortname"));
      }
      return _results;
    },
    render_rivers: function(rivers) {
      var json_url;
      if (rivers == null) rivers = this.Rivers;
      json_url = $('#blockbox-table').attr('data-calculated-measures-url');
      return $.getJSON(json_url, function(data) {
        var attributes, feature, num, target_difference, _i, _j, _len, _len2, _ref;
        target_difference = {};
        for (_i = 0, _len = data.length; _i < _len; _i++) {
          num = data[_i];
          target_difference[num.location_reach] = num.target_difference;
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
    render_measure_IVM: function(IVM) {
      var feature, selected_items, _i, _len, _ref, _ref2;
      if (IVM == null) IVM = this.IVM;
      selected_items = this.selected_items();
      _ref = IVM.features;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        feature = _ref[_i];
        if (_ref2 = feature.attributes.Code_IVM, __indexOf.call(selected_items, _ref2) >= 0) {
          feature.attributes.selected = true;
        } else {
          feature.attributes.selected = false;
        }
      }
      return IVM.redraw();
    },
    render_measure_QS: function(QS) {
      var feature, selected_items, _i, _len, _ref, _ref2;
      if (QS == null) QS = this.QS;
      selected_items = this.selected_items();
      _ref = QS.features;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        feature = _ref[_i];
        if (_ref2 = feature.attributes.code_QS, __indexOf.call(selected_items, _ref2) >= 0) {
          feature.attributes.selected = true;
        } else {
          feature.attributes.selected = false;
        }
      }
      return QS.redraw();
    },
    render_measure_PKB: function(PKB) {
      var feature, selected_items, _i, _len, _ref, _ref2;
      if (PKB == null) PKB = this.PKB;
      selected_items = this.selected_items();
      _ref = PKB.features;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        feature = _ref[_i];
        if (_ref2 = feature.attributes.code, __indexOf.call(selected_items, _ref2) >= 0) {
          feature.attributes.selected = true;
        } else {
          feature.attributes.selected = false;
        }
      }
      return PKB.redraw();
    },
    rivers: function() {
      var _this = this;
      return $.getJSON("/blokkendoos/api/rivers/", function(json) {
        _this.Rivers = JSONRiverLayer('Rivers', json);
        return _this.render_rivers(_this.Rivers);
      });
    },
    initialize: function() {
      var runDelayed,
        _this = this;
      this.static_url = $('#lizard-blockbox-graph').attr('data-static-url');
      runDelayed = function() {
        _this.measures();
        return _this.rivers();
      };
      return setTimeout(runDelayed, 500);
    },
    render: function() {
      this.render_measure_IVM();
      this.render_measure_QS();
      this.render_measure_PKB();
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
    short_name = attr["Code_IVM"] ? attr["Code_IVM"] : attr["code_QS"];
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
        strokeColor: color
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
          strokeColor: GRAY
        }
      })
    ];
    styleMap = new OpenLayers.StyleMap(OpenLayers.Util.applyDefaults({
      fillColor: GRAY,
      strokeColor: GRAY
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

  showTooltip = function(x, y, name, type_name) {
    return $("<div id=\"tooltip\" class=\"popover top\">\n  <div class=\"popover-inner\">\n    <div class=\"popover-title\"><h3>" + name + "</h3></div>\n    <div class=\"popover-content\">Type: " + type_name + "</div>\n  </div>\n</div>").css({
      top: y - 35,
      left: x + 5
    }).appendTo("body").fadeIn(200);
  };

  setFlotSeries = function() {
    var json_url;
    json_url = $('#blockbox-table').attr('data-calculated-measures-url');
    return $.getJSON(json_url, function(data) {
      window.min_graph_value = data[0].location;
      window.max_graph_value = data[data.length - 1].location;
      setPlaceholderTop(data);
      return setMeasureSeries();
    });
  };

  setMeasureSeries = function() {
    var json_url;
    json_url = $('#blockbox-table').attr('data-measure-list-url');
    return $.getJSON(json_url, function(data) {
      return setPlaceholderControl(data);
    });
  };

  setPlaceholderTop = function(json_data) {
    var ed_data, measures, num, options, pl_lines, reference, selected_river, target;
    reference = (function() {
      var _i, _len, _results;
      _results = [];
      for (_i = 0, _len = json_data.length; _i < _len; _i++) {
        num = json_data[_i];
        _results.push([num.location, num.reference_value]);
      }
      return _results;
    })();
    target = (function() {
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
    selected_river = $("#blockbox-river .chzn-select")[0].value;
    ed_data = [
      {
        data: reference,
        points: {
          show: false
        },
        lines: {
          show: true
        },
        color: GRAY
      }, {
        label: "Doelwaarde",
        data: target,
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
      }
    };
    ({
      legend: {
        show: true,
        noColumns: 4,
        container: $("#placeholder_top_legend"),
        labelFormatter: function(label, series) {
          var cb;
          cb = label;
          return cb;
        }
      }
    });
    pl_lines = $.plot($("#placeholder_top"), ed_data, options);
    return window.topplot = pl_lines;
  };

  setPlaceholderControl = function(control_data) {
    var d4, d5, measures, measures_controls, non_selectable_measures, num, options, pl_control, pl_lines, selected_measures, selected_river;
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
        tickDecimals: 0
      },
      grid: {
        minBorderMargin: 20,
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
    measures_controls = [
      {
        label: "Maatregelen",
        data: measures,
        points: {
          show: true,
          symbol: "square",
          radius: 2
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
          radius: 4
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
    pl_control = $.plot($("#placeholder_control"), measures_controls, options);
    $("#placeholder_control").bind("plotclick", function(event, pos, item) {
      var callback, measure_id, result_id;
      if (item) {
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
    return $("#placeholder_control").bind("plothover", function(event, pos, item) {
      if (item && !hasTooltip) {
        showTooltip(item.pageX, item.pageY, item.series.data[item.dataIndex][2], item.series.data[item.dataIndex][4]);
        return hasTooltip = 'yep';
      } else {
        hasTooltip = '';
        return $('#tooltip').remove();
      }
    });
  };

  resize_placeholder = function() {
    var doit;
    clearTimeout(doit);
    return doit = setTimeout(function() {
      $('#placeholder_top_legend').empty();
      $('#placeholder_top').empty();
      $('#placeholder_control').empty();
      $('#placeholder_control_legend').empty();
      $('#placeholder_top_legend').css('width', '100%');
      $('#placeholder_top').css('width', '100%');
      $('#placeholder_control').css('width', '100%');
      $('#placeholder_control_legend').css('width', '100%');
      $('#placeholder_top_legend').css('height', '0px');
      $('#placeholder_top').css('height', '150px');
      $('#placeholder_control').css('height', '100px');
      $('#placeholder_control_legend').css('height', '100px');
      return setFlotSeries();
    }, 100);
  };

  $('.btn.collapse-sidebar').click(function() {
    return resize_placeholder();
  });

  $('.btn.collapse-rightbar').click(function() {
    return resize_placeholder();
  });

  doit = void 0;

  $(window).resize(function() {
    return resize_placeholder();
  });

  $(".blockbox-toggle-measure").live('click', function(e) {
    e.preventDefault();
    return toggleMeasure($(this).attr('data-measure-id'));
  });

  $(document).ready(function() {
    setFlotSeries();
    $("#blockbox-river .chzn-select").chosen().change(function() {
      return selectRiver(this.value);
    });
    $('#measures-table-top').tablesorter();
    return this;
  });

}).call(this);
