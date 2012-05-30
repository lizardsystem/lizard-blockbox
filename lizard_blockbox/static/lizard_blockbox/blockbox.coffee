# HEADSUP: This file needs to be compiled by hand:
# coffee -wc blockbox.coffee
#
# setFlotSeries() is the wrapper function you're looking for to
# draw the flot graph.

#######################################################
# Backbone part                                       #
#######################################################

ANIMATION_DURATION = 150

# Colors from main theme.
GRAY = "#c0c0bc"
BLUE = "#046F96"
LIGHTBLUE = "#bddfed"
# Triad color rules from http://kuler.adobe.com based on BLUE.
RED = "#A31535"
YELLOW = "#E2D611"
GREEN = "#635E0D"

# For shades in the map. The light one is the most extreme.
# Every shade has 25% lighter saturation.
LIGHTRED = "#A36775"
MIDDLERED = "#A33E56"
DARKRED = RED
LIGHTGREEN = "#63623F"
MIDDLEGREEN = "#636026"
DARKGREEN = GREEN

# Original colors
DIAMOND_COLOR = "#105987"
TRIANGLE_COLOR = "#E78B00"
SQUARE_COLOR = "#122F64"

# City dot color
PURPLE = "#E01B6A"
BLACK = "#000000"

STROKEWIDTH = 5

graphTimer = ''
hasTooltip = ''


toggleMeasure = (measure_id) ->
    $.ajax
        type: 'POST'
        url: $('#blockbox-table').data('measure-toggle-url')
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

selectRiver = (river_name) ->
    $.ajax
        type: 'POST'
        url: $('#blockbox-river').data 'select-river-url'
        data:
            'river_name': river_name
        success: (data) ->
            setFlotSeries()
            measuresMapView.render()
            @

class BlockboxRouter extends Backbone.Router
    routes:
        "map":      "map"
        "table":    "table"

    map: ->
        to_table_text = $('.toggle_map_and_table').parent().data('to-table-text')
        $('a.toggle_map_and_table span').text(to_table_text)
        $('a.toggle_map_and_table').attr("href", "#table")
        $('#blockbox-table').slideUp ANIMATION_DURATION, () ->
            $('#map').slideDown(ANIMATION_DURATION)

    table: ->
        to_map_text = $('.toggle_map_and_table').parent().data('to-map-text')
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
        $.getJSON @static_url + 'lizard_blockbox/measures.json', (json) =>
            @measures = JSONTooltip 'Maatregelen', json
            @render_measures(@measures)

    selected_items: ->
        ($(el).data "measure-shortname" for el in $("#selected-measures-list li a"))

    render_rivers: (rivers = @Rivers) ->
        json_url = $('#blockbox-table').data('calculated-measures-url')
        $.getJSON json_url, (data) ->
            target_difference = {}
            for num in data
                target_difference[num.location_reach] = num.target_difference
            for feature in rivers.features
                attributes = feature.attributes
                attributes.target_difference = target_difference[attributes.MODELKM]
            rivers.redraw()

    render_measures: (measures = @measures) ->
        selected_items = @selected_items()
        for feature in measures.features
            if feature.attributes.code in selected_items
                feature.attributes.selected = true
            else
                feature.attributes.selected = false
        measures.redraw()

    rivers: ->
        $.getJSON @static_url + 'lizard_blockbox/kilometers.json', (json) =>
            @Rivers = JSONRiverLayer 'Rivers', json
            @render_rivers(@Rivers)

    initialize: ->
        @static_url = $('#lizard-blockbox-graph').data 'static-url'
        # Dirty hack, the global 'map' variable doesn't exist early enough for IE.
        runDelayed = =>
            @measures()
            @rivers()
        # Delay in the hope that this is long enough for 'map' to exist.
        setTimeout(runDelayed, 500)

    render: ->
        @render_measures()
        @render_rivers()


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

onFeatureToggle = (feature) ->
    attr = feature.attributes
    short_name = attr["code"]
    toggleMeasure short_name

JSONLayer = (name, json) ->
    geojson_format = new OpenLayers.Format.GeoJSON()
    vector_layer = new OpenLayers.Layer.Vector(name)
    map.addLayer vector_layer
    vector_layer.addFeatures geojson_format.read(json)

RiverLayerRule = (from, to, color) ->
    rule = new OpenLayers.Rule(
        filter: new OpenLayers.Filter.Comparison
            type: OpenLayers.Filter.Comparison.BETWEEN,
            property: "target_difference"
            lowerBoundary: from
            upperBoundary: to
        symbolizer:
            fillColor: color
            strokeColor: color
            strokeWidth: STROKEWIDTH
    )
    rule

RiverLayerBorderRule = (to, color) ->
    rule = new OpenLayers.Rule(
        filter: new OpenLayers.Filter.Comparison
            type: OpenLayers.Filter.Comparison.EQUAL_TO,
            property: "target_difference"
            value: to
        symbolizer:
            fillColor: color
            strokeColor: color
    )
    rule

JSONRiverLayer = (name, json) ->
    console.log "json:", json
    console.log "name:", name
    rules = [
        RiverLayerRule 1.00, 1.50, DARKRED
        RiverLayerRule 0.50, 1.00, MIDDLERED
        RiverLayerRule 0.10, 0.50, LIGHTRED
        RiverLayerRule -0.10, 0.10, BLUE
        RiverLayerRule -0.50, -0.10, LIGHTGREEN
        RiverLayerRule -1.00, -0.50, MIDDLEGREEN
        RiverLayerRule -1.50, -1.00, DARKGREEN
        new OpenLayers.Rule
            elseFilter: true
            symbolizer:
                fillColor: GRAY
                strokeColor: GRAY
                strokeWidth: STROKEWIDTH
    ]

    styleMap = new OpenLayers.StyleMap(OpenLayers.Util.applyDefaults(
            fillColor: GRAY
            strokeColor: GRAY
            strokeWidth: STROKEWIDTH
        OpenLayers.Feature.Vector.style["default"]))

    styleMap.styles["default"].addRules(rules)

    geojson_format = new OpenLayers.Format.GeoJSON()
    vector_layer = new OpenLayers.Layer.Vector(name,
        styleMap: styleMap
    )
    map.addLayer(vector_layer)
    vector_layer.addFeatures(geojson_format.read(json))
    vector_layer

JSONTooltip = (name, json) ->
    styleMap = new OpenLayers.StyleMap(OpenLayers.Util.applyDefaults(
            fillColor: GREEN
            strokeColor: GREEN
        OpenLayers.Feature.Vector.style["default"]))

    styleMap.styles["default"].addRules [ new OpenLayers.Rule(
        filter: new OpenLayers.Filter.Comparison(
            type: OpenLayers.Filter.Comparison.EQUAL_TO
            property: "selected"
            value: true
        )
        symbolizer:
          fillColor: RED
          strokeColor: RED
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

    # ToDo: Fix selectCtrl, it has problems with hoover and selecting
    #selectCtrl = new OpenLayers.Control.SelectFeature(vector_layer,
    #    hover: false
    #    click: true
    #    onSelect: onFeatureToggle
    #)
    #map.addControl(selectCtrl)
    #selectCtrl.activate()

    map.addControl highlightCtrl
    highlightCtrl.activate()

    vector_layer


#######################################################
# Graph part                                          #
#######################################################

showLabel = (x, y, contents) ->
    $('<div id="label">#{contents}</div>').css(
        position: 'absolute',
        display: 'none',
        top: y + 5,
        left: x + 250,
        border: '1px solid #fdd',
        padding: '2px',
        'background-color': '#fee',
        opacity: 0.80
    )




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
    json_url = $('#blockbox-table').data('calculated-measures-url')
    $.getJSON json_url, (data) ->
        window.min_graph_value = data[0].location
        window.max_graph_value = data[data.length-1].location

        setPlaceholderTop data
        setMeasureSeries()


setMeasureSeries = () ->
    json_url = $('#blockbox-table').data('measure-list-url')
    cities_list_url = $('#blockbox-table').data('cities-list-url')
    $.getJSON json_url, (data) ->
        $.getJSON cities_list_url, (cities) ->
            setPlaceholderControl data, cities



setPlaceholderTop = (json_data) ->
    reference = ([num.location, num.reference_value] for num in json_data)
    target = ([num.location, num.reference_target] for num in json_data)
    measures = ([num.location, num.measures_level] for num in json_data)
    cities = ([num.location, num.city] for num in json_data)

    selected_river = $("#blockbox-river .chzn-select")[0].value

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

        color: BLUE
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

        color: RED

    ]

    # tickFormatter = (val, axis) ->
    #     val+10
    # 

    options =
        xaxis:
            min: window.min_graph_value
            max: window.max_graph_value
            transform: (v) -> if selected_river == 'Maas' then -v else v
            inverseTransform: (v) -> if selected_river == 'Maas' then -v else v
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
            container: $("#placeholder_top_legend")
            labelFormatter: (label, series) ->
                cb = label
                cb

    pl_lines = $.plot($("#placeholder_top"), ed_data, options)
    window.topplot = pl_lines

    # $("#placeholder_top").bind "plotclick", (event, pos, item) ->
    #     if item
    #         refreshGraph()


setPlaceholderControl = (control_data, cities_data) ->

    measures = ([num.km_from, num.type_index, num.name, num.short_name, num.measure_type] for num in control_data when num.selectable and not num.selected)
    selected_measures = ([num.km_from, num.type_index, num.name, num.short_name, num.measure_type] for num in control_data when num.selected)
    non_selectable_measures = ([num.km_from, num.type_index, num.name, num.short_name, num.measure_type] for num in control_data when not num.selectable)
    cities = ([city[0], 15, city[1], city[1], "Stad"] for city in cities_data)

    selected_river = $("#blockbox-river .chzn-select")[0].value

    d4 = undefined
    d5 = undefined
    pl_lines = undefined

    options =
        xaxis:
            min: window.min_graph_value
            max: window.max_graph_value
            transform: (v) -> if selected_river == 'Maas' then -v else v
            inverseTransform: (v) -> if selected_river == 'Maas' then -v else v
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
            container: $("#measures_legend")
            labelFormatter: (label, series) ->
                cb = label
                cb

    measures_controls = [

        label: "Steden"
        data: cities
        points:
            show: true
            symbol: "circle"
            radius: 3
            fill: 1
            fillColor: BLACK
        lines:
            show: false
        color: BLACK
    ,
        
        label: "Maatregelen"
        data: measures
        points:
            show: true
            symbol: "square"
            radius: 2
            fill: 1
            fillColor: BLUE
        lines:
            show: false
        color: BLUE
    ,
        label: "Geselecteerde maatregelen"
        data: selected_measures
        points:
            show: true
            symbol: "diamond"
            radius: 4
            fill: true
        lines:
            show: false
        color: RED
    ,
        label: "Niet-selecteerbare maatregelen"
        data: non_selectable_measures
        points:
            show: true
            symbol: "cross"
            radius: 4
        lines:
            show: false
        color: GRAY
    ]
    pl_control = $.plot($("#placeholder_control"), measures_controls, options)
    
    
    # (city[0], city[1], city[2]) for city in pl_control.getData()[0].data
    # showLabel(city[0], city[1], city[2]) for city in pl_control.getData()[0].data

    # showLabel(city[0], city[1], city[2]) for city in pl_control.getData()[0].data

    $("#placeholder_control").bind "plotclick", (event, pos, item) ->
        if item
            if item.series.label is "Steden"
                return
            pl_control.unhighlight item.series, item.datapoint
            result_id = item.series.data[item.dataIndex][1]
            measure_id = item.series.data[item.dataIndex][3]
            if not graphTimer
                callback = ->
                    toggleMeasure measure_id
                    graphTimer = ''
                graphTimer = setTimeout(callback, 200)


    # This trick with previousPoint is neccessary to prevent tooltip flickering!
    previousPoint = null
    $("#placeholder_control").bind "plothover", (event, pos, item) ->

        if item

            # Shuffles the tooltip to the left when it gets too close to
            # the right of the browser window:
            if item.pageX > ($(window).width() - 300)
                item.pageX = item.pageX - 300
            
            if previousPoint != item.dataIndex
                previousPoint = item.dataIndex

                $("#tooltip").remove()
                x = item.datapoint[0].toFixed(2)
                y = item.datapoint[1].toFixed(2)

                showTooltip(
                    item.pageX,
                    item.pageY,
                    item.series.data[item.dataIndex][2]
                    item.series.data[item.dataIndex][4]
                )
        else
            $("#tooltip").remove()
            previousPoint = null



resize_placeholder = ->
    clearTimeout doit
    doit = setTimeout(->
        $('#placeholder_top').empty()
        $('#placeholder_control').empty()

        $('#placeholder_top').css('width', '100%')
        $('#placeholder_control').css('width', '100%')

        $('#placeholder_top').css('height', '150px')
        $('#placeholder_control').css('height', '100px')

        setFlotSeries()
    ,200)

$('.btn.collapse-sidebar').click ->
    resize_placeholder()

$('.btn.collapse-rightbar').click ->
    resize_placeholder()

doit = undefined
$(window).resize ->
    resize_placeholder()

$(".blockbox-toggle-measure").live 'click', (e) ->
    e.preventDefault()
    toggleMeasure $(@).data('measure-id')

$(document).ready ->
    setFlotSeries()
    $("#blockbox-river .chzn-select").chosen().change(
        () -> selectRiver @value )

    $('#measures-table-top').tablesorter()
    @
