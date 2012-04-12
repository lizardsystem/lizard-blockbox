# HEADSUP: This file needs to be compiled by hand:
# coffee -wc blockbox.coffee
#
# setFlotSeries() is the wrapper function you're looking for to
# draw the flot graph.

#######################################################
# Backbone part                                       #
#######################################################

ANIMATION_DURATION = 150
DIAMOND_COLOR = "#105987"
TRIANGLE_COLOR = "#E78B00"
SQUARE_COLOR = "#122F64"

class BlockboxRouter extends Backbone.Router
    routes:
        "map":      "map"
        "table":    "table"

    map: ->
        to_table_text = $('.toggle_map_and_table').parent().attr('data-to-table-text')
        $('a.toggle_map_and_table span').text(to_table_text)
        $('a.toggle_map_and_table').attr("href", "#table")
        $('#blockbox-table').slideUp ANIMATION_DURATION, () ->
            $('#map').slideDown(ANIMATION_DURATION)

    table: ->
        to_map_text = $('.toggle_map_and_table').parent().attr('data-to-map-text')
        $('a.toggle_map_and_table span').text(to_map_text)
        $('a.toggle_map_and_table').attr("href", "#map")
        $('#map').slideUp ANIMATION_DURATION, () ->
            $('#blockbox-table').slideDown ANIMATION_DURATION, () ->
                $('#blockbox-table').height($("#content").height() - 250)


# Currently renders the measures on the left...

# Model
class Measure extends Backbone.Model
    defaults:
        name: "Untitled measure"


# Collections
class MeasureList extends Backbone.Collection
    model: Measure
    url: $('#blockbox-table').attr('data-measure-list-url')

# SelectedMeasuresList = Backbone.Collection.extend
#     model: Measure



# View for single measure table element
class MeasureView extends Backbone.View
    tagName: 'tr'

    events:
        click: 'toggleMeasure'

    toggleMeasure: (e) ->
        e.preventDefault()
        $.ajax
            type: 'POST'
            url: $('#blockbox-table').attr('data-measure-toggle-url')
            data:
                # 'measure_id': @$el.find('td:first a').data('measure-id')
                'measure_id': @model.get('short_name')
            async: false
            success: (data) ->
                # window.location.reload()
                # window.measure_list.reset()
                # window.measure_list.fetch({add:true})
                measure_list.fetch()
                setFlotSeries()
                # Hack hack hack
                #$(".sidebar-measure").each ->
                #    console.log $(@).attr('data-measure-id')
                #    if $.inArray($(@).attr('data-measure-id'), data) == -1
                #        console.log "hiding " + $(@)
                #        $(@).hide()
                #    else
                #        console.log "showing " + $(@)
                #        $(@).show()
                $holder = $('<div/>')
                $holder.load '. #page', () ->
                    $("#selected-measures-list").html($('#selected-measures-list', $holder).html())


    initialize: ->
        @model.bind 'change', @render, @
        @


    render: ->
        @$el.html """
            <td style="cursor:pointer;">
                <a href="#"
                   class="blockbox-toggle-measure"
                   data-measure-id="#{@model.get('short_name')}">
                        #{@model.get('name') or @model.get('short_name')}
                </a>
            </td>
            <td>
               #{@model.get('measure_type') or 'Onbekend'}
            </td>
            <td>
                #{@model.get('km_from') or 'Onbekend'}
            </td>
        """
        @


# View for single *selected* measure li element
class SelectedMeasureView extends Backbone.View
    tagName: 'li'

    initialize: ->
        @model.bind 'change', @render, @
        measure_list.bind 'reset', @render, @

    render: ->
        @$el.html """
            <a
            href="#"
            class="sidebar-measure blockbox-toggle-measure padded-sidebar-item"
            data-measure-id="#{@model.get('short_name')}"
            data-measure-shortname="#{@model.get('short_name')}">
                #{@model.get('name') or @model.get('short_name')}
            </a>
        """

        if not @model.attributes.selected
            @$el.hide()
        else
            @$el.show()

        @


# View for measures list

class MeasureListView extends Backbone.View

    addOne: (measure) ->
        view = new MeasureView(model:measure)
        @$el.append(view.render().el)
        @

    addAll: ->
        measure_list.each @addOne

    tablesort: ->
        $('#measures-table-top').tablesorter()

    initialize: ->
        measure_list.bind 'add', @addOne, @
        # measure_list.bind 'reset', @addAll, @
        measure_list.fetch({add:true, success: @tablesort})

    render: ->
        @


# View for *selected* measures list
SelectedMeasureListView = Backbone.View.extend

    addOne: (measure) ->
        view = new SelectedMeasureView(model:measure)
        $(@el).append(view.render().el)

    #redraw: ->
    #    measure_list.each @addOne

    initialize: ->
        measure_list.bind 'add', @addOne, @
        #measure_list.bind 'reset', @redraw, @
        @

    render: ->
        @



measure_list = new MeasureList()

window.measure_list = measure_list


window.measureListView = new MeasureListView({el: $('#measures-table')});
#window.selectedMeasureListView = new SelectedMeasureListView({el: $('#selected-measures-list')});
window.app_router = new BlockboxRouter
Backbone.history.start()







#######################################################
# Graph part                                          #
#######################################################

# This was an attempt to make the flot graph into a jQ plugin,
# but time didn't allow it... here's the skeleton:

# $ = jQuery
#
# $.fn.flotGraph = (options) ->
#
#     defaults =
#         someDefault: '#ccc'
#
#     options = $.extend(defaults, options)
#
#     console.log "Bound to", @
#
#     initialize: ->

showTooltip = (x, y, contents) ->
    $("""<div id="tooltip">#{contents}</div>""").css(
        position: "absolute"
        display: "none"
        top: y - 35
        left: x + 5
        border: "1px solid #fdd"
        padding: "2px"
        background: "#fee"
    ).appendTo("body").fadeIn 200



setFlotSeries = (json_url="/blokkendoos/api/measures/calculated/") ->
    $.getJSON json_url, (data) ->
        setPlaceholderTop data
        setPlaceholderControl window.measure_list.toJSON()


# refreshGraph = ->
#     $.plot $("#placeholder_top"), ed_data, options


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
        label: "Doelwaarde"
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
        label: "Effect maatregelen"
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
    measures = ([num.km_from, num.type_index, num.measure_graph_name, num.short_name] for num in control_data)

    d4 = undefined
    d5 = undefined
    pl_lines = undefined

    options =
        xaxis:
            position: "bottom"

        grid:
            clickable: true
            hoverable: true
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
        data: measures
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
            refreshGraph()


    $("#placeholder_control").bind "plotclick", (event, pos, item) ->
        if item
            pl_control.unhighlight item.series, item.datapoint
            $.ajax
                type: 'POST'
                url: $('#blockbox-table').attr('data-measure-toggle-url')
                data:
                    'measure_id': item.series.data[item.dataIndex][3]
                async: false
                success: (data) ->
                    measure_list.fetch()
                    setFlotSeries()
                    $holder = $('<div/>')
                    $holder.load '. #page', () ->
                        $("#selected-measures-list").html($('#selected-measures-list', $holder).html())
            
            

    $("#placeholder_control").bind "plothover", (event, pos, item) ->

        if item
            $('#tooltip').remove()
            showTooltip(
                item.pageX,
                item.pageY,
                item.series.data[item.dataIndex][2]
            )
        else
            $('#tooltip').remove()

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



$(".sidebar-measure").live 'click', (e) ->
    e.preventDefault()
    $.ajax
        type: 'POST'
        url: $('#blockbox-table').attr('data-measure-toggle-url')
        data:
            'measure_id': $(@).attr('data-measure-id')
        async: false
        success: (data) ->
            measure_list.fetch()
            setFlotSeries()
            # Hack hack hack
            $holder = $('<div/>')
            $holder.load '. #page', () ->
                $("#selected-measures-list").html($('#selected-measures-list', $holder).html())


$(document).ready ->
    window.table_or_map = "map"
    setFlotSeries()
    $(".chzn-select").chosen()

