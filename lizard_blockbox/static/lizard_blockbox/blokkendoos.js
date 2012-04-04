(function() {
  var Measure, MeasureList, MeasureListView, MeasureView, measure_list;

  Measure = Backbone.Model.extend({
    defaults: {
      name: "Untitled measure"
    }
  });

  MeasureList = Backbone.Collection.extend({
    model: Measure,
    url: "/static_media/lizard_blockbox/measures.json"
  });

  MeasureView = Backbone.View.extend({
    tagName: 'li',
    initialize: function() {
      return this.model.bind('change', this.render, this);
    },
    render: function() {
      this.$el.html("<a href=\"#\" class=\"padded-sidebar-item workspace-acceptable has_popover\" data-content=\"" + (this.model.toJSON().description) + "\"'>\n    " + (this.model.toJSON().name) + "\n</a>");
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

}).call(this);
