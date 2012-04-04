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
        # @model.bind('add', @render, @)
    
    render: ->
        console.log "MeasureView.render()"
        console.log "model.view.el:", @el
        @$el.html "<a href='#' class='padded-sidebar-item workspace-acceptable has_popover' data-content='"+ @model. +"'>" + @model.toJSON().name + "</a>"
        # @$el.html(@template(@model.toJSON()))
        @


# View for measures list
MeasureListView = Backbone.View.extend
    el: $('#measures-list')
    
    id: 'measures-view'

    addOne: (measure) ->
        console.log "MeasureListView.addOne()"
        view = new MeasureView(model:measure)
        @$el.append(view.render().el)
        console.log @
        console.log "--->", @$el
        
    addAll: ->
        # console.log "MeasureListView.addAll()"
        measure_list.fetch()
        measure_list.each @addOne

    initialize: ->
        # console.log "MeasureListView.init()"
        # console.log "@el:", @el
        measure_list.bind 'add', @addOne, @
        measure_list.bind 'reset', @addAll, @
        measure_list.fetch({add:true})
        @render()

    render: ->
        # console.log "MeasureListView.render()"
        # console.log "Hello from Backbone!"        
        @


# Instance of collection
measure_list = new MeasureList()

# Instance of measure list
window.measureListView = new MeasureListView();

