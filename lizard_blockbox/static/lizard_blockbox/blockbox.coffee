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
GRAY = "#c0c0bc"
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
                measuresMapView.render()
            @


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
                # -39 to not have the table scrollbar behind the footer.
                # ToDo: Fix this for real in lizard-ui.
                $('#blockbox-table').height($("#content").height() - 250 - 39)


window.app_router = new BlockboxRouter
Backbone.history.start()

#View for the OpenLayersMap
MeasuresMapView = Backbone.View.extend

    measures: ->
        $.getJSON @static_url + 'lizard_blockbox/IVM_deel1.json', (json) =>
            @IVM = JSONTooltip 'IVM deel 1', json
            @render_measure_IVM()
        $.getJSON @static_url + 'lizard_blockbox/QS.json', (json) =>
            @QS = JSONTooltip 'QS', json
            @render_measure_QS()

    selected_items: ->
        ($(el).attr "data-measure-shortname" for el in $("#selected-measures-list li a"))

    render_measure_IVM: ->
        selected_items = @selected_items()
        for feature in @IVM.features
            if feature.attributes.Code_IVM in selected_items
                feature.attributes.selected = true
            else
                feature.attributes.selected = false
        @IVM.redraw()

    render_measure_QS: ->
        selected_items = @selected_items()
        for feature in @QS.features
            if feature.attributes.code_QS in selected_items
                feature.attributes.selected = true
            else
                feature.attributes.selected = false
        @QS.redraw()

    rivers: ->
        $.getJSON @static_url + 'lizard_blockbox/rijntakken.json', (json) =>
            JSONLayer 'Rijntak', json
        $.getJSON "/blokkendoos/api/rivers/maas/", (json) =>
            JSONLayer 'Maas', json

    initialize: ->
        @static_url = $('#lizard-blockbox-graph').attr 'data-static-url'
        @measures()
        @rivers()

    render: ->
        @render_measure_IVM()
        @render_measure_QS()


measuresMapView = new MeasuresMapView()

#######################################################
# OpenLayers GeoJSON graph                            #
#######################################################

onPopupClose = (evt) ->
    selectControl.unselect selectedFeature

onFeatureHighlight = (feature) ->
    selectedFeature = feature
    ff = feature.feature
    popup = new OpenLayers.Popup.FramedCloud(
        "chicken"
        ff.geometry.getBounds().getCenterLonLat()
        null
        "<div style='font-size:.8em'>" + ff.data.titel + "</div>"
        null
        false
        false
    )
    feature.feature.popup = popup
    map.addPopup popup

onFeatureUnhighlight = (feature) ->
    map.removePopup feature.feature.popup
    feature.feature.popup.destroy()
    feature.feature.popup = null

JSONLayer = (name, json) ->
    geojson_format = new OpenLayers.Format.GeoJSON()
    vector_layer = new OpenLayers.Layer.Vector(name)
    map.addLayer(vector_layer)
    vector_layer.addFeatures(geojson_format.read(json))


JSONTooltip = (name, json) ->
    styleMap = new OpenLayers.StyleMap(OpenLayers.Util.applyDefaults(
            fillColor: 'blue'
            strokeColor: 'blue'
        OpenLayers.Feature.Vector.style["default"]))
    styleMap.styles["default"].addRules [ new OpenLayers.Rule(
        filter: new OpenLayers.Filter.Comparison(
            type: OpenLayers.Filter.Comparison.EQUAL_TO
            property: "selected"
            value: true
        )
        symbolizer:
          fillColor: "red"
          strokeColor: "red"
    ), new OpenLayers.Rule(elseFilter: true) ]
    geojson_format = new OpenLayers.Format.GeoJSON()
    vector_layer = new OpenLayers.Layer.Vector(name,
        styleMap: styleMap
    )
    map.addLayer vector_layer
    vector_layer.addFeatures geojson_format.read(json)
    highlightCtrl = new OpenLayers.Control.SelectFeature(vector_layer,
        hover: true
        highlightOnly: true
        renderIntent: "temporary"
        eventListeners:
          featurehighlighted: onFeatureHighlight
          featureunhighlighted: onFeatureUnhighlight
    )
    map.addControl highlightCtrl
    highlightCtrl.activate()
    vector_layer


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



setFlotSeries = () ->
    json_url = $('#blockbox-table').attr('data-calculated-measures-url')
    $.getJSON json_url, (data) ->
        window.min_graph_value = data[0].location
        window.max_graph_value = data[data.length-1].location

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

        color: GRAY
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
            min: window.min_graph_value
            max: window.max_graph_value
            position: "top"

        yaxis:
            labelWidth: 21
            reserveSpace: true
            position: "left"
            tickDecimals: 1

        grid:
            minBorderMargin: 20
            #alignTicksWithAxis: 1
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
    window.topplot = pl_lines

    # $("#placeholder_top").bind "plotclick", (event, pos, item) ->
    #     if item
    #         refreshGraph()


setPlaceholderControl = (control_data) ->

    measures = ([num.km_from, num.type_index, num.name, num.short_name, num.measure_type] for num in control_data when num.selectable and not num.selected)
    selected_measures = ([num.km_from, num.type_index, num.name, num.short_name, num.measure_type] for num in control_data when num.selected)
    non_selectable_measures = ([num.km_from, num.type_index, num.name, num.short_name, num.measure_type] for num in control_data when not num.selectable)

    d4 = undefined
    d5 = undefined
    pl_lines = undefined

    options =
        xaxis:
            transform: (v) -> -v
            inverseTransform: (v) -> -v
            min: window.min_graph_value
            max: window.max_graph_value
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
        label: "Maatregelen"
        data: measures
        points:
            show: true
            symbol: "square"
            radius: 2
        lines:
            show: false
        color: SQUARE_COLOR
    ,
        label: "Geselecteerde maatregelen"
        data: selected_measures
        points:
            show: true
            symbol: "square"
            radius: 4
        lines:
            show: false
        color: SQUARE_COLOR
    ,
        label: "Niet-selecteerbare maatregelen"
        data: non_selectable_measures
        points:
            show: true
            symbol: "square"
            radius: 2
        lines:
            show: false
        color: GRAY
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


resize_placeholder = ->
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
    ,100)

$('.btn.collapse-sidebar').click ->
    resize_placeholder()

$('.btn.collapse-rightbar').click ->
    resize_placeholder()

doit = undefined
$(window).resize ->
    resize_placeholder()

$(".blockbox-toggle-measure").live 'click', (e) ->
    e.preventDefault()
    toggleMeasure $(@).attr('data-measure-id')


$(document).ready ->
    setFlotSeries()
    $(".chzn-select").chosen()
    $('#measures-table-top').tablesorter()
    @
