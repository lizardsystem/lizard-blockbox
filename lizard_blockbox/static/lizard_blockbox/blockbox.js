(function() {
  var ANIMATION_DURATION, BlockboxRouter, DIAMOND_COLOR, MeasuresMapView, SQUARE_COLOR, TRIANGLE_COLOR, doit, graphTimer, hasTooltip, measuresMapView, resize_placeholder, setFlotSeries, setMeasureSeries, setPlaceholderControl, setPlaceholderTop, showTooltip, toggleMeasure,
    __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; },
    __indexOf = Array.prototype.indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

  ANIMATION_DURATION = 150;

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
          $("#selected-measures-list").html($('#selected-measures-list', $holder).html());
          return measuresMapView.render();
        });
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
          return $('#blockbox-table').height($("#content").height() - 250);
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
        return _this.render_measure_IVM();
      });
      return $.getJSON(this.static_url + 'lizard_blockbox/QS.json', function(json) {
        _this.QS = JSONTooltip('QS', json);
        return _this.render_measure_QS();
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
    render_measure_IVM: function() {
      var feature, selected_items, _i, _len, _ref, _ref2;
      selected_items = this.selected_items();
      _ref = this.IVM.features;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        feature = _ref[_i];
        if (_ref2 = feature.attributes.Code_IVM, __indexOf.call(selected_items, _ref2) >= 0) {
          feature.attributes.selected = true;
        } else {
          feature.attributes.selected = false;
        }
      }
      return this.IVM.redraw();
    },
    render_measure_QS: function() {
      var feature, selected_items, _i, _len, _ref, _ref2;
      selected_items = this.selected_items();
      _ref = this.QS.features;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        feature = _ref[_i];
        if (_ref2 = feature.attributes.code_QS, __indexOf.call(selected_items, _ref2) >= 0) {
          feature.attributes.selected = true;
        } else {
          feature.attributes.selected = false;
        }
      }
      return this.QS.redraw();
    },
    rivers: function() {
      var _this = this;
      $.getJSON(this.static_url + 'lizard_blockbox/rijntakken.json', function(json) {
        return JSONLayer('Rijntak', json);
      });
      return $.getJSON("/blokkendoos/api/rivers/maas/", function(json) {
        return JSONLayer('Maas', json);
      });
    },
    initialize: function() {
      this.static_url = $('#lizard-blockbox-graph').attr('data-static-url');
      this.measures();
      return this.rivers();
    },
    render: function() {
      this.render_measure_IVM();
      return this.render_measure_QS();
    }
  });

  measuresMapView = new MeasuresMapView();

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
      window.data = data;
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
    var ed_data, measures, num, options, pl_lines, reference, target;
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
    ed_data = [
      {
        data: reference,
        points: {
          show: false
        },
        lines: {
          show: true
        },
        color: DIAMOND_COLOR
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
        color: DIAMOND_COLOR
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
        color: TRIANGLE_COLOR
      }
    ];
    options = {
      xaxis: {
        transform: function(v) {
          return -v;
        },
        inverseTransform: function(v) {
          return -v;
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
        alignTicksWithAxis: 1,
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
    return pl_lines = $.plot($("#placeholder_top"), ed_data, options);
  };

  setPlaceholderControl = function(control_data) {
    var d4, d5, measures, measures_controls, num, options, pl_control, pl_lines;
    measures = (function() {
      var _i, _len, _results;
      _results = [];
      for (_i = 0, _len = control_data.length; _i < _len; _i++) {
        num = control_data[_i];
        _results.push([num.km_from, num.type_index, num.name, num.short_name, num.measure_type]);
      }
      return _results;
    })();
    d4 = void 0;
    d5 = void 0;
    pl_lines = void 0;
    options = {
      xaxis: {
        transform: function(v) {
          return -v;
        },
        inverseTransform: function(v) {
          return -v;
        },
        min: window.data[0].location,
        max: window.data[window.data.length - 1].location,
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
        label: "Serie 2",
        data: measures,
        points: {
          show: true,
          symbol: "square",
          radius: 2
        },
        lines: {
          show: false
        },
        color: SQUARE_COLOR
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
    $(".chzn-select").chosen();
    $('#measures-table-top').tablesorter();
    return this;
  });

}).call(this);
