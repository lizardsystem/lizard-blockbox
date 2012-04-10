(function() {
  var Measure, MeasureList, MeasureListView, MeasureView, SelectedMeasureListView, SelectedMeasureView, doit, measure_list, options, refreshGraph, setFlotSeries, setPlaceholderControl, setPlaceholderTop, showTooltip;

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
    tagName: 'tr',
    initialize: function() {
      return this.model.bind('change', this.render, this);
    },
    render: function() {
      this.$el.html("<td><a href=\"#\" class=\"blockbox-toggle-measure\" data-measure-id=\"" + (this.model.toJSON().short_name) + "\">" + (this.model.toJSON().short_name) + "</a></td><td>(type)</td><td>(start km)</td>");
      return this;
    }
  });

  SelectedMeasureView = Backbone.View.extend({
    tagName: 'li',
    initialize: function() {
      return this.model.bind('change', this.render, this);
    },
    render: function() {
      this.$el.html("<a href=\"#\" class=\"sidebar-measure blockbox-toggle-measure padded-sidebar-item\" data-measure-id=\"" + (this.model.toJSON().short_name) + "\" data-measure-shortname=\"" + (this.model.toJSON().short_name) + "\">" + (this.model.toJSON().short_name) + "</a>");
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
      return this.$el.append(view.render().el);
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
    addOne: function(measure) {
      var view;
      view = new SelectedMeasureView({
        model: measure
      });
      return this.$el.append(view.render().el);
    },
    addAll: function() {
      return measure_list.each(this.addOne);
    },
    initialize: function() {
      measure_list.bind('add', this.addOne, this);
      return measure_list.bind('reset', this.addAll, this);
    },
    render: function() {
      return this;
    }
  });

  measure_list = new MeasureList();

  window.measureListView = new MeasureListView();

  window.selectedMeasureListView = new SelectedMeasureListView();

  $('.blockbox-toggle-measure').live('click', function() {
    var measure_id, url;
    measure_id = $(this).attr('data-measure-id');
    url = $('#blockbox-table').attr('data-measure-toggle-url');
    return $.ajax({
      type: 'POST',
      url: url,
      data: {
        'measure_id': measure_id
      },
      async: false,
      success: function(data) {
        return window.location.reload();
      }
    });
  });

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
    if (json_url == null) json_url = "/static_media/lizard_blockbox/sample.json";
    return $.getJSON(json_url, function(data) {
      setPlaceholderTop(data.basecase_data, data.result_data);
      return setPlaceholderControl(data.measure_control_data);
    });
  };

  refreshGraph = function() {
    return $.plot($("#placeholder_top"), ed_data, options);
  };

  setPlaceholderTop = function(basecase_data, result_data) {
    var DIAMOND_COLOR, SQUARE_COLOR, TRIANGLE_COLOR, ed_data, options, pl_lines;
    DIAMOND_COLOR = "#105987";
    TRIANGLE_COLOR = "#E78B00";
    SQUARE_COLOR = "#122F64";
    ed_data = [
      {
        data: basecase_data,
        points: {
          show: true,
          symbol: "diamond"
        },
        lines: {
          show: true
        },
        color: DIAMOND_COLOR
      }, {
        label: "Serie 1",
        data: result_data,
        points: {
          show: true,
          symbol: "triangle",
          radius: 1
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
    var DIAMOND_COLOR, SQUARE_COLOR, TRIANGLE_COLOR, d4, d5, measures_controls, options, pl_control, pl_lines;
    DIAMOND_COLOR = "#105987";
    TRIANGLE_COLOR = "#E78B00";
    SQUARE_COLOR = "#122F64";
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

  $('.toggle_map_and_table').click(function(e) {
    var link, parent, to_map_text, to_table_text,
      _this = this;
    e.preventDefault();
    link = $('.toggle_map_and_table');
    parent = link.parent();
    to_table_text = parent.attr('data-to-table-text');
    to_map_text = parent.attr('data-to-map-text');
    if (window.table_or_map === 'map') {
      $('#map').hide(500, function() {
        $('#blockbox-table').show(500);
        return $('.action-text', link).text(to_map_text);
      });
      window.table_or_map = 'table';
      return $('#blockbox-table').height($("#content").height() - 250);
    } else {
      $('#blockbox-table').hide(500, function() {
        $('#map').show(500);
        return $('.action-text', link).text(to_table_text);
      });
      return window.table_or_map = 'map';
    }
  });

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
    return setFlotSeries("/static_media/lizard_blockbox/sample.json");
  });

}).call(this);
