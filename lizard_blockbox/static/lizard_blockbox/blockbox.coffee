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

graphTimer = ''
hasTooltip = ''


toggleMeasure = (measure_id) ->
    $.ajax
        type: 'POST'
        url: $('#blockbox-table').attr('data-measure-toggle-url')
        data:
            'measure_id': measure_id
        # async: false
        success: (data) ->
            setFlotSeries()
            # TODO: Update checkmark for selected measures in main table.
            $holder = $('<div/>')
            $holder.load '. #page', () ->
                $("#selected-measures-list").html($('#selected-measures-list', $holder).html())


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


window.app_router = new BlockboxRouter

Backbone.history.start()



#######################################################
# Graph part                                          #
#######################################################

showTooltip = (x, y, name, type_name) ->
    $("""<div id="tooltip" class="popover top">
           <div class="popover-inner">
             <div class="popover-title"><h3>#{name}</h3></div>
             <div class="popover-content">Type: #{type_name}</div>
           </div>
         </div>""").css(
        top: y - 35
        left: x + 5
    ).appendTo("body").fadeIn 200



# TODO: url from data attr
setFlotSeries = () ->
    json_url = $('#blockbox-table').attr('data-calculated-measures-url')
    $.getJSON json_url, (data) ->
        window.data = data
        setPlaceholderTop data
        setMeasureSeries()


setMeasureSeries = () ->
    json_url = $('#blockbox-table').attr('data-measure-list-url')
    $.getJSON json_url, (data) ->
        setPlaceholderControl data


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
            show: false
            # show: true
            # symbol: "triangle"
            # radius: 1

        lines:
            show: true
            lineWidth: 2

        color: DIAMOND_COLOR
    ,
        label: "Effect maatregelen"
        data: measures
        points:
            show: false
            # show: true
            # symbol: "triangle"
            # radius: 2

        lines:
            show: true
            lineWidth: 2

        color: TRIANGLE_COLOR

    ]

    options =
        xaxis:
            transform: (v) -> -v
            inverseTransform: (v) -> -v
            position: "top"

        yaxis:
            labelWidth: 21
            reserveSpace: true
            position: "left"
            tickDecimals: 1

        grid:
            minBorderMargin: 20
            alignTicksWithAxis: 1
            clickable: true
            borderWidth: 1
            axisMargin: 10
            # labelMargin:-50

    legend:
        show: true
        noColumns: 4
        container: $("#placeholder_top_legend")
        labelFormatter: (label, series) ->
            cb = label
            cb

    pl_lines = $.plot($("#placeholder_top"), ed_data, options)

    # $("#placeholder_top").bind "plotclick", (event, pos, item) ->
    #     if item
    #         refreshGraph()


setPlaceholderControl = (control_data) ->

    measures = ([num.km_from, num.type_index, num.name, num.short_name, num.measure_type] for num in control_data)

    d4 = undefined
    d5 = undefined
    pl_lines = undefined

    options =
        xaxis:
            transform: (v) -> -v
            inverseTransform: (v) -> -v
            min: window.data[0].location
            max: window.data[window.data.length-1].location
            reserveSpace: true
            position: "bottom"

        yaxis:
            reserveSpace: true
            labelWidth: 21
            position: "left"
            tickDecimals: 0

        grid:
            minBorderMargin: 20
            clickable: true
            hoverable: true
            borderWidth: 1
            # labelMargin:-50


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

    $("#placeholder_control").bind "plotclick", (event, pos, item) ->
        if item
            pl_control.unhighlight item.series, item.datapoint
            result_id = item.series.data[item.dataIndex][1]
            measure_id = item.series.data[item.dataIndex][3]
            if not graphTimer
                callback = ->
                    toggleMeasure measure_id
                    graphTimer = ''
                graphTimer = setTimeout(callback, 200)

    $("#placeholder_control").bind "plothover", (event, pos, item) ->

        if item and not hasTooltip
            showTooltip(
                item.pageX,
                item.pageY,
                item.series.data[item.dataIndex][2]
                item.series.data[item.dataIndex][4]
            )
            hasTooltip = 'yep'
        else
            hasTooltip = ''
            $('#tooltip').remove()




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
        #setMeasureSeries()
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
        #setMeasureSeries()
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
        #setMeasureSeries()
    , 100)


$(".blockbox-toggle-measure").live 'click', (e) ->
    e.preventDefault()
    toggleMeasure $(@).attr('data-measure-id')


$(document).ready ->
    setFlotSeries()
    #setMeasureSeries()
    $(".chzn-select").chosen()
    $('#measures-table-top').tablesorter()
