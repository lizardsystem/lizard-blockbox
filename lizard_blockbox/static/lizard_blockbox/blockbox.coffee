# HEADSUP: This file needs to be compiled by hand:
# coffee -wc blockbox.coffee


#######################################################
# Backbone part                                       #
#######################################################

ANIMATION_DURATION = 150
DIAMOND_COLOR = "#105987"
TRIANGLE_COLOR = "#E78B00"
SQUARE_COLOR = "#122F64"

BlockboxRouter = Backbone.Router.extend
    routes:
        "map":      "map"
        "table":    "table"

    map: ->
        $('#blockbox-table').slideUp ANIMATION_DURATION, () ->
            $('#map').slideDown(ANIMATION_DURATION)
            $('a.toggle_map_and_table span').text("Show table")
            $('a.toggle_map_and_table').attr("href", "#table")

    table: ->
        $('#map').slideUp ANIMATION_DURATION, () ->
            $('#blockbox-table').slideDown(ANIMATION_DURATION)
            $('a.toggle_map_and_table span').text("Show map")
            $('a.toggle_map_and_table').attr("href", "#map")


# Currently renders the measures on the left...

# Model
Measure = Backbone.Model.extend
    defaults:
        name: "Untitled measure"


# Collections
MeasureList = Backbone.Collection.extend
    model: Measure
    url: "/blokkendoos/api/measures/list/"

SelectedMeasuresList = Backbone.Collection.extend
    model: Measure


# View for single measure table element
MeasureView = Backbone.View.extend
    tagName: 'tr'

    events:
        click: 'addRow'

    addRow: ->
        console.log "Adding #{@model.toJSON().short_name} to selection!"

    initialize: ->
        @model.bind('change', @render, @)
        @

    render: ->
        @$el.html """
            <td style="cursor:pointer;">
                <a href="#" 
                   class="blockbox-toggle-measure" 
                   data-measure-id="#{@model.get('short_name')}">
                        #{@model.get('short_name')}
                </a>
            </td>
            <td>
               #{@model.toJSON().measure_type}
            </td>
            <td>
                #{@model.toJSON().km_from}
            </td>"""
        @


# View for single *selected* measure li element
SelectedMeasureView = Backbone.View.extend
    tagName: 'li'

    initialize: ->
        @model.bind('change', @render, @)

    render: ->
        @$el.html """
            <a 
            href="#" 
            class="sidebar-measure blockbox-toggle-measure padded-sidebar-item" 
            data-measure-id="#{@model.get('short_name')}" 
            data-measure-shortname="#{@model.get('short_name')}">
                #{@model.get('short_name')}
            </a>
        """
        if not @model.attributes.selected
            @$el.hide()

        @


# View for measures list
MeasureListView = Backbone.View.extend
    el: $('#measures-table')

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

    render: ->
        @


# View for *selected* measures list
SelectedMeasureListView = Backbone.View.extend
    el: $('#selected-measures-list')

    id: 'selected-measures-view'

    addOne: (measure) ->
        view = new SelectedMeasureView(model:measure)
        @$el.append(view.render().el)

    addAll: ->
        window.selected_measures_list.each @addOne

    initialize: ->
        measure_list.bind 'add', @addOne, @
        measure_list.bind 'reset', @addAll, @
        @
        # measure_list.fetch({add:true})

    render: ->
        @


# Instance of Measures collection
measure_list = new MeasureList()

# Instance of SelectedMeasuresList model
# window.selected_measures_list = new SelectedMeasuresList()

# Instance of measure list
window.measureListView = new MeasureListView();
window.selectedMeasureListView = new SelectedMeasureListView();

window.app_router = new BlockboxRouter
Backbone.history.start()




$('.blockbox-toggle-measure').live 'click', ->
    # e.preventDefault()
    measure_id = $(@).attr('data-measure-id')
    url = $('#blockbox-table').attr('data-measure-toggle-url')
    $.ajax({
            type: 'POST',
            url: url,
            data: {'measure_id': measure_id},
            async: false,
            success: (data) ->
                window.location.reload()
                #$(".sidebar-measure").each ->
                #    measure = $(@)
                #    console.log(data)
                #    console.log("" + measure.attr('data-measure-shortname'))
                #    if $.inArray("" + measure.attr('data-measure-shortname'), data) isnt -1
                #        console.log("Showing")
                #        measure.parent().show()
                #    else
                #        console.log("Hiding")
                #        measure.parent().hide()
        })
    #measure_list.reset()
    #measure_list.fetch()
    #window.selectedMeasureListView.render()






#######################################################
# Graph part                                          #
#######################################################

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



setFlotSeries = (json_url="/blokkendoos/api/measures/calculated/") ->
    $.getJSON json_url, (data) ->
        setPlaceholderTop data
        #setPlaceholderControl data.measure_control_data




refreshGraph = ->
    $.plot $("#placeholder_top"), ed_data, options


setPlaceholderTop = (json_data) ->

    reference = ([num.location, num.reference_value] for num in json_data)
    target = ([num.location, num.reference_target] for num in json_data)
    measures = ([num.location, num.measures_level] for num in json_data)

    ed_data = [
        data: reference
        points:
            show: false

        lines:
            show: true

        color: DIAMOND_COLOR
    ,
        label: "Doel waarde"
        data: target
        points:
            show: true
            symbol: "triangle"
            radius: 1

        lines:
            show: true
            lineWidth: 2

        color: DIAMOND_COLOR
    ,
        label: "Measurements"
        data: measures
        points:
            show: true
            symbol: "triangle"
            radius: 2

        lines:
            show: true
            lineWidth: 2

        color: TRIANGLE_COLOR

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
    DIAMOND_COLOR = "#105987"
    TRIANGLE_COLOR = "#E78B00"
    SQUARE_COLOR = "#122F64"

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

        color: SQUARE_COLOR
    ,
        label: "Serie 3"
        data: d4
        points:
            show: true
            symbol: "triangle"
            radius: 1

        lines:
            show: false

        color: TRIANGLE_COLOR
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

    $("#placeholder_top").bind "plotclick", (event, pos, item) ->
        if item
            console.log item
            # pl_lines.unhighlight item.series, item.datapoint
            # result_id = item.series.data[item.dataIndex][2].id
            refreshGraph()


    $("#placeholder_control").bind "plotclick", (event, pos, item) ->
        if item
            console.log item
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


# $('.toggle_map_and_table').click (e) ->
#     e.preventDefault()
#     link = $('.toggle_map_and_table')
#     parent = link.parent()
#     to_table_text = parent.attr('data-to-table-text')
#     to_map_text = parent.attr('data-to-map-text')
#     if window.table_or_map == 'map'
#         $('#map').hide 500, () =>
#             $('#blockbox-table').show(500)
#             $('.action-text', link).text(to_map_text)
#         window.table_or_map = 'table'
#         $('#blockbox-table').height($("#content").height() - 250)
#     else
#         $('#blockbox-table').hide 500, () =>
#             $('#map').show(500)
#             $('.action-text', link).text(to_table_text)
#         window.table_or_map = 'map'


$('.btn.collapse-sidebar').click ->
    clearTimeout doit
    doit = setTimeout(->
        $('#placeholder_top_legend').empty()
        $('#placeholder_top').empty()
        $('#placeholder_control').empty()
        $('#placeholder_control_legend').empty()

        $('#placeholder_top_legend').css('width', '100%')
        $('#placeholder_top').css('width', '100%')
        $('#placeholder_control').css('width', '100%')
        $('#placeholder_control_legend').css('width', '100%')

        $('#placeholder_top_legend').css('height', '0px')
        $('#placeholder_top').css('height', '150px')
        $('#placeholder_control').css('height', '100px')
        $('#placeholder_control_legend').css('height', '100px')

        setFlotSeries()
    ,500)


$('.btn.collapse-rightbar').click ->
    clearTimeout doit
    doit = setTimeout(->
        $('#placeholder_top_legend').empty()
        $('#placeholder_top').empty()
        $('#placeholder_control').empty()
        $('#placeholder_control_legend').empty()

        $('#placeholder_top_legend').css('width', '100%')
        $('#placeholder_top').css('width', '100%')
        $('#placeholder_control').css('width', '100%')
        $('#placeholder_control_legend').css('width', '100%')

        $('#placeholder_top_legend').css('height', '0px')
        $('#placeholder_top').css('height', '150px')
        $('#placeholder_control').css('height', '100px')
        $('#placeholder_control_legend').css('height', '100px')

        setFlotSeries()
    ,500)


doit = undefined
$(window).resize ->
    clearTimeout doit
    doit = setTimeout(->
        $('#placeholder_top_legend').empty()
        $('#placeholder_top').empty()
        $('#placeholder_control').empty()
        $('#placeholder_control_legend').empty()

        $('#placeholder_top_legend').css('width', '100%')
        $('#placeholder_top').css('width', '100%')
        $('#placeholder_control').css('width', '100%')
        $('#placeholder_control_legend').css('width', '100%')

        $('#placeholder_top_legend').css('height', '0px')
        $('#placeholder_top').css('height', '150px')
        $('#placeholder_control').css('height', '100px')
        $('#placeholder_control_legend').css('height', '100px')

        setFlotSeries()
    , 100)


$(document).ready ->
    window.table_or_map = "map"
    setFlotSeries( "/blokkendoos/api/measures/calculated/")
    $(".chzn-select").chosen()
