(function() {
  var ANIMATION_DURATION, BlockboxRouter, DIAMOND_COLOR, Measure, MeasureList, MeasureListView, MeasureView, SQUARE_COLOR, SelectedMeasureListView, SelectedMeasureView, SelectedMeasuresList, TRIANGLE_COLOR, doit, measure_list, options, refreshGraph, setFlotSeries, setPlaceholderControl, setPlaceholderTop, showTooltip;

  ANIMATION_DURATION = 150;

  DIAMOND_COLOR = "#105987";

  TRIANGLE_COLOR = "#E78B00";

  SQUARE_COLOR = "#122F64";

  BlockboxRouter = Backbone.Router.extend({
    routes: {
      "map": "map",
      "table": "table"
    },
    map: function() {
      var to_table_text;
      to_table_text = $('.toggle_map_and_table').parent().attr('data-to-table-text');
      $('a.toggle_map_and_table span').text(to_table_text);
      $('a.toggle_map_and_table').attr("href", "#table");
      return $('#blockbox-table').slideUp(ANIMATION_DURATION, function() {
        return $('#map').slideDown(ANIMATION_DURATION);
      });
    },
    table: function() {
      var to_map_text;
      to_map_text = $('.toggle_map_and_table').parent().attr('data-to-map-text');
      $('a.toggle_map_and_table span').text(to_map_text);
      $('a.toggle_map_and_table').attr("href", "#map");
      return $('#map').slideUp(ANIMATION_DURATION, function() {
        return $('#blockbox-table').slideDown(ANIMATION_DURATION, function() {
          return $('#blockbox-table').height($("#content").height() - 250);
        });
      });
    }
  });

  Measure = Backbone.Model.extend({
    defaults: {
      name: "Untitled measure"
    }
  });

  MeasureList = Backbone.Collection.extend({
    model: Measure,
    url: "/blokkendoos/api/measures/list/"
  });

  SelectedMeasuresList = Backbone.Collection.extend({
    model: Measure
  });

  MeasureView = Backbone.View.extend({
    tagName: 'tr',
    events: {
      click: 'addMeasure'
    },
    addMeasure: function() {
      console.log("Adding " + (this.model.get('short_name')) + " to selection!");
      return $.ajax({
        type: 'POST',
        url: $('#blockbox-table').attr('data-measure-toggle-url'),
        data: {
          'measure_id': this.model.get('short_name')
        },
        async: false,
        success: function(data) {
          return window.location.reload();
        }
      });
    },
    initialize: function() {
      this.model.bind('change', this.render, this);
      return this;
    },
    render: function() {
      this.$el.html("<td style=\"cursor:pointer;\">\n    <a href=\"#\"\n       class=\"blockbox-toggle-measure\"\n       data-measure-id=\"" + (this.model.get('short_name')) + "\">\n            " + (this.model.get('name') || this.model.get('short_name')) + "\n    </a>\n</td>\n<td>\n   " + (this.model.get('measure_type') || 'Onbekend') + "\n</td>\n<td>\n    " + (this.model.get('km_from') || 'Onbekend') + "\n</td>");
      return this;
    }
  });

  SelectedMeasureView = Backbone.View.extend({
    tagName: 'li',
    initialize: function() {
      return this.model.bind('change', this.render, this);
    },
    render: function() {
      this.$el.html("<a\nhref=\"#\"\nclass=\"sidebar-measure blockbox-toggle-measure padded-sidebar-item\"\ndata-measure-id=\"" + (this.model.get('short_name')) + "\"\ndata-measure-shortname=\"" + (this.model.get('short_name')) + "\">\n    " + (this.model.get('short_name')) + "\n</a>");
      if (!this.model.attributes.selected) this.$el.hide();
      return this;
    }
  });

  MeasureListView = Backbone.View.extend({
    el: $('#measures-table'),
    id: 'measures-view',
    addOne: function(measure) {
      var view;
      view = new MeasureView({
        model: measure
      });
      this.$el.append(view.render().el);
      $('#measures-table').tablesorter();
      return this;
    },
    addAll: function() {
      return measure_list.each(this.addOne);
    },
    initialize: function() {
      measure_list.bind('add', this.addOne, this);
      measure_list.bind('reset', this.addAll, this);
      return measure_list.fetch({
        add: true
      });
    },
    render: function() {
      return this;
    }
  });

  SelectedMeasureListView = Backbone.View.extend({
    el: $('#selected-measures-list'),
    id: 'selected-measures-view',
    addOne: function(measure) {
      var view;
      view = new SelectedMeasureView({
        model: measure
      });
      return this.$el.append(view.render().el);
    },
    addAll: function() {
      return window.selected_measures_list.each(this.addOne);
    },
    initialize: function() {
      measure_list.bind('add', this.addOne, this);
      measure_list.bind('reset', this.addAll, this);
      return this;
    },
    render: function() {
      return this;
    }
  });

  measure_list = new MeasureList();

  window.measureListView = new MeasureListView();

  window.selectedMeasureListView = new SelectedMeasureListView();

  console.log(window.sele);

  window.app_router = new BlockboxRouter;

  Backbone.history.start();

  showTooltip = function(x, y, contents) {
    return $("<div id=\"tooltip\">" + contents + "</div>").css({
      position: "absolute",
      display: "none",
      top: y - 35,
      left: x + 5,
      border: "1px solid #fdd",
      padding: "2px",
      backgroundcolor: "#fee"
    }).appendTo("body").fadeIn(200);
  };

  setFlotSeries = function(json_url) {
    return $.getJSON(json_url, function(data) {
      return setPlaceholderTop(data);
    });
  };

  refreshGraph = function() {
    return $.plot($("#placeholder_top"), ed_data, options);
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
        label: "Doel waarde",
        data: target,
        points: {
          show: true,
          symbol: "triangle",
          radius: 1
        },
        lines: {
          show: true,
          lineWidth: 2
        },
        color: DIAMOND_COLOR
      }, {
        label: "Measurements",
        data: measures,
        points: {
          show: true,
          symbol: "triangle",
          radius: 2
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
        position: "top"
      }
    };
    ({
      grid: {
        clickable: true,
        borderWidth: 1
      },
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
    var d4, d5, measures_controls, options, pl_control, pl_lines;
    d4 = void 0;
    d5 = void 0;
    pl_lines = void 0;
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
          var cb;
          cb = label;
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
        color: SQUARE_COLOR
      }, {
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
        color: TRIANGLE_COLOR
      }, {
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
    $("#placeholder_top").bind("plotclick", function(event, pos, item) {
      if (item) {
        console.log(item);
        return refreshGraph();
      }
    });
    return $("#placeholder_control").bind("plotclick", function(event, pos, item) {
      var result_id;
      if (item) {
        console.log(item);
        pl_lines.unhighlight(item.series, item.datapoint);
        result_id = item.series.data[item.dataIndex][2].id;
        return refreshGraph();
      }
    });
  };

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
        var cb;
        cb = label;
        return cb;
      }
    }
  };

  $('.btn.collapse-sidebar').click(function() {
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
    }, 500);
  });

  $('.btn.collapse-rightbar').click(function() {
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
    }, 500);
  });

  doit = void 0;

  $(window).resize(function() {
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
  });

  $(document).ready(function() {
    window.table_or_map = "map";
    setFlotSeries("/blokkendoos/api/measures/calculated/");
    return $(".chzn-select").chosen();
  });

}).call(this);
