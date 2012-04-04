# Model
Measure = Backbone.Model.extend
    defaults:
        name: "Untitled measure"


# Collection
MeasureList = Backbone.Collection.extend
    model: Measure
    url: "/blokkendoos/api/measures/list/"


# View for single measure li element
MeasureView = Backbone.View.extend
    tagName: 'li'
    
    # template: _.template $('#measure-template').html()
    
    initialize: ->
        @model.bind('change', @render, @)
    
    render: ->
        @$el.html """<a href="#" class="padded-sidebar-item workspace-acceptable has_popover" data-content="#{@model.toJSON().short_name}">#{@model.toJSON().short_name}</a>"""
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








showTooltip = (x, y, contents) ->
    $("<div id=\"tooltip\">#{contents}</div>").css(
        position: "absolute"
        display: "none"
        top: y - 35
        left: x + 5
        border: "1px solid #fdd"
        padding: "2px"
        backgroundcolor: "#fee"
    ).appendTo("body").fadeIn 200



setFlotSeries = ->
    setPlaceholderTop json_data.basecase_data, json_data.result_data
    setPlaceholderControl json_data.measure_control_data


refreshGraph = ->
    $.plot $("#placeholder_top"), ed_data, options


setPlaceholderTop = (basecase_data, result_data) ->

    ed_data = [
        data: json_data.basecase_data
        points:
            show: true
            symbol: "diamond"

        lines:
            show: true

        color: "blue"
    ,
        label: "Serie 1"
        data: json_data.result_data
        points:
            show: true
            symbol: "triangle"
            radius: 1

        lines:
            show: true
            lineWidth: 2

        color: "red"
    ]

    options =
        xaxis:
            position: "top"

    grid:
        clickable: true
        borderWidth: 1

    legend:
        show: true
        noColumns: 4
        container: $("#placeholder_top_legend")
        labelFormatter: (label, series) ->
            cb = label
            cb

    pl_lines = $.plot($("#placeholder_top"), ed_data, options)



setPlaceholderControl = (control_data) ->
    d4 = undefined
    d5 = undefined
    pl_lines = undefined
    
    options =
        xaxis:
            position: "bottom"

        grid:
            clickable: true
            borderWidth: 1

        legend:
            show: true
            noColumns: 4
            container: $("#placeholder_control_legend")
            labelFormatter: (label, series) ->
                cb = label
                cb

    measures_controls = [
        label: "Serie 2"
        data: control_data
        points:
            show: true
            symbol: "square"
            radius: 2

        lines:
            show: false

        color: "red"
    ,
        label: "Serie 3"
        data: d4
        points:
            show: true
            symbol: "triangle"
            radius: 1

        lines:
            show: false

        color: "green"
    ,
        data: d5
        points:
            show: false

        lines:
            show: true
            lineWidth: 1
            radius: 1

        color: "gray"
        shadowSize: 0
    ]

    pl_control = $.plot($("#placeholder_control"), measures_controls, options)

    $("#placeholder_control").bind "plotclick", (event, pos, item) ->
        if item
            pl_lines.unhighlight item.series, item.datapoint
            result_id = item.series.data[item.dataIndex][2].id
            refreshGraph()



options =
    xaxis:
        position: "top"

    grid:
        clickable: true
        borderWidth: 1

    legend:
        show: true
        noColumns: 4
        container: $("#placeholder_top_legend")
        labelFormatter: (label, series) ->
            cb = label
            cb

$(document).ready ->
    setFlotSeries()