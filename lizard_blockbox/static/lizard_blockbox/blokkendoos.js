(function() {
  var Measure, MeasureList, MeasureListView, MeasureView, doit, measure_list, options, refreshGraph, setFlotSeries, setPlaceholderControl, setPlaceholderTop, showTooltip;

  Measure = Backbone.Model.extend({
    defaults: {
      name: "Untitled measure"
    }
  });

  MeasureList = Backbone.Collection.extend({
    model: Measure,
    url: "/blokkendoos/api/measures/list/"
  });

  MeasureView = Backbone.View.extend({
    tagName: 'li',
    initialize: function() {
      return this.model.bind('change', this.render, this);
    },
    render: function() {
      this.$el.html("<a href=\"#\" class=\"padded-sidebar-item workspace-acceptable has_popover\" data-content=\"" + (this.model.toJSON().short_name) + "\">" + (this.model.toJSON().short_name) + "</a>");
      return this;
    }
  });

  MeasureListView = Backbone.View.extend({
    el: $('#measures-list'),
    id: 'measures-view',
    addOne: function(measure) {
      var view;
      view = new MeasureView({
        model: measure
      });
      return this.$el.append(view.render().el);
    },
    addAll: function() {
      return measure_list.each(this.addOne);
    },
    initialize: function() {
      measure_list.bind('add', this.addOne, this);
      measure_list.bind('reset', this.addAll, this);
      measure_list.fetch({
        add: true
      });
      return this.render();
    },
    render: function() {
      return this;
    }
  });

  measure_list = new MeasureList();

  window.measureListView = new MeasureListView();

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

  setFlotSeries = function() {
    setPlaceholderTop(json_data.basecase_data, json_data.result_data);
    return setPlaceholderControl(json_data.measure_control_data);
  };

  refreshGraph = function() {
    return $.plot($("#placeholder_top"), ed_data, options);
  };

  setPlaceholderTop = function(basecase_data, result_data) {
    var ed_data, options, pl_lines;
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
      }, {
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
        color: "red"
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
        color: "green"
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
    return $("#placeholder_control").bind("plotclick", function(event, pos, item) {
      var result_id;
      if (item) {
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

  $(document).ready(function() {
    return setFlotSeries();
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

}).call(this);
