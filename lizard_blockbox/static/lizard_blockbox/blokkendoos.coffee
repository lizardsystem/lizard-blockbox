# Model
Measure = Backbone.Model.extend
    defaults:
        name: "Untitled measure"


# Collection
MeasureList = Backbone.Collection.extend
    model: Measure
    url: "/static_media/lizard_blockbox/measures.json"


# View for single measure li element
MeasureView = Backbone.View.extend
    tagName: 'li'
    
    # template: _.template $('#measure-template').html()
    
    initialize: ->
        @model.bind('change', @render, @)
    
    render: ->
        @$el.html """
            <a href="#" class="padded-sidebar-item workspace-acceptable has_popover" data-content="#{@model.toJSON().description}"'>
                #{@model.toJSON().name}
            </a>
        """
        # @$el.html(@template(@model.toJSON()))
        @


# View for measures list
MeasureListView = Backbone.View.extend
    el: $('#measures-list')
    
    id: 'measures-view'

    addOne: (measure) ->
        view = new MeasureView(model:measure)
        @$el.append(view.render().el)
        
    addAll: ->
        measure_list.each @addOne

    initialize: ->
        measure_list.bind 'add', @addOne, @
        measure_list.bind 'reset', @addAll, @
        measure_list.fetch({add:true})
        @render()

    render: ->
        @


# Instance of collection
measure_list = new MeasureList()

# Instance of measure list
window.measureListView = new MeasureListView();

