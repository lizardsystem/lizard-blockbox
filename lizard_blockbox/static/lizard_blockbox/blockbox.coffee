# HEADSUP: This file needs to be compiled by hand:
# coffee -wc blockbox.coffee
#
# setFlotSeries() is the wrapper function you're looking for to
# draw the flot graph.
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
RIVERLEVEL9 = "rgb(195, 0, 120)"
RIVERLEVEL8 = "rgb(203, 81, 145)"
RIVERLEVEL7 = "rgb(219, 155, 192)"
RIVERLEVEL6 = "rgb(214, 128, 25)"
RIVERLEVEL5 = "rgb(241, 205, 58)"
RIVERLEVEL4 = "rgb(247, 239, 212)"
RIVERLEVEL3 = "rgb(217, 235, 250)"
RIVERLEVEL2 = "rgb(177, 215, 245)"
RIVERLEVEL1 = "rgb(104, 184, 235)"
RIVERLEVEL0 = "rgb(0, 156, 223)"

# For measures in the map.
MEASURECOLOR = "rgb(128, 153, 140)"
SELECTEDMEASURECOLOR = "rgb(29, 82, 62)"

#MEASURECOLOR = "rgb(201, 218, 155)"
#SELECTEDMEASURECOLOR = "rgb(140, 182, 59)"


# Original colors
DIAMOND_COLOR = "#105987"
TRIANGLE_COLOR = "#E78B00"
SQUARE_COLOR = "#122F64"

# City dot color
PURPLE = "#E01B6A"
BLACK = "#000000"

# Note on colors: setup_map_legend() at the end helps put the right colors
# in the legend. See the legend usage in views.py. Let's try to keep the
# color definitions in one spot! :-)

STROKEWIDTH = 7

graphTimer = ''
hasTooltip = ''

#######################################################
# Backbone part                                       #
#######################################################

deselectAllMeasures = () ->
    $.get($('#blockbox-deselect-all-measures').data('deselect-url'), (data) =>
            updateMeasuresList()
            measuresMapView.render(true, true)
            @
    )

toggleMeasure = (measure_id) ->
    $.ajax
        type: 'POST'
        url: $('#blockbox-table').data('measure-toggle-url')
        data:
            'measure_id': measure_id
        # async: false
        success: (data) ->
            updateMeasuresList()
            measuresMapView.render(true, true)
            @

window.toggleMeasure = toggleMeasure

updateMeasuresList = () ->
    $holder = $('<div/>')
    $holder.load '. #page', () ->
        $("#selected-measures-list").html($('#selected-measures-list', $holder).html())
        $("#measures-table").html $('#measures-table', $holder).html()
        sort = $("#measures-table-top").get(0).config.sortList
        # trigger update for sortable table header.
        $("#measures-table-top").trigger "update"
        $("#measures-table-top").trigger "sorton", [sort]

selectRiver = (river_name) ->
    $.ajax
        type: 'POST'
        url: $('#blockbox-river').data 'select-river-url'
        data:
            'river_name': river_name
        success: (data) ->
            updateVertex()
            updateMeasuresList()
            measuresMapView.render(true, false)
            @

selectVertex = (vertex_id) ->
    $.ajax
        type: 'POST'
        url: $('#blockbox-vertex').data 'select-vertex-url'
        data:
            'vertex': vertex_id
        success: (data) ->
            measuresMapView.render(true, false)
            @

updateVertex = ->
    $.getJSON($('#blockbox-vertex').data('update-vertex-url') + '?' + new Date().getTime(), (data) ->

        groups = for header, values of data
            options =  ["<option value='#{field[0]}'>#{field[1]}</option>" for field in values]
            options_html = options.join ""
            "<optgroup label='#{header}'>#{options_html}</optgroup>"
        html=groups.join ""
        $('#blockbox-vertex select').html html
        $('#blockbox-vertex .chzn-select').trigger "liszt:updated"
        )

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
            $('#blockbox-table').slideDown(ANIMATION_DURATION)


window.app_router = new BlockboxRouter
Backbone.history.start()

#View for the OpenLayersMap
MeasuresMapView = Backbone.View.extend

    selected_items: ->
        ($(el).data "measure-shortname" for el in $("#selected-measures-list li a"))

    render_rivers: (data) ->
        target_difference = {}
        for num in data
            target_difference[num.location_reach] = num.measures_level
        for feature in @rivers.features
            attributes = feature.attributes
            attributes.target_difference = target_difference[attributes.label]
        @rivers.redraw()

    render_measures: ->
        selected_items = @selected_items()
        for feature in @measures.features
            if feature.attributes.code in selected_items
                feature.attributes.selected = true
            else
                feature.attributes.selected = false
        @measures.redraw()

    initialize: ->
        numResponses = 0
        @static_url = $('#lizard-blockbox-graph').data 'static-url'
        $.getJSON @static_url + 'lizard_blockbox/measures.json' + '?' + new Date().getTime(), (json) =>
            @measures = JSONTooltip 'Maatregelen', json
            numResponses++
            if numResponses == 2
                @render()
            @
        $.getJSON @static_url + 'lizard_blockbox/kilometers.json' + '?' + new Date().getTime(), (json) =>
            @rivers = JSONRiverLayer 'Rivers', json
            # Dirty hack, the global 'map' variable doesn't exist early enough for IE.
            # Delay in the hope that this is long enough for 'map' to exist.
            numResponses++
            if numResponses == 2
                @render()
            @

    render: (updateRivers = true, updateMeasures = true) ->
        json_url = $('#blockbox-table').data('calculated-measures-url')
        $.getJSON json_url + '?' + new Date().getTime(), (data) =>
            setFlotSeries(data)
            if updateRivers
                @render_rivers(data)
        if updateMeasures
            @render_measures()


measuresMapView = new MeasuresMapView()

#######################################################
# Popup                                               #
#######################################################

# UGLY DUCKLING HACK with javascript in the onclick
# to change the text in the popup dynamically.

showPopup = (feature) ->
    href_text = if feature.attributes['selected'] then 'Deselecteer' else 'Selecteer'
    popup = new OpenLayers.Popup.FramedCloud(
        "chicken"
        feature.geometry.getBounds().getCenterLonLat()
        null
        "<div style='font-size:.8em'>" + feature.data.titel + "<br/><a onclick='window.toggleMeasure(\"" + feature.attributes['code']  + "\"); if (this.innerHTML === \"Selecteer\") { this.innerHTML=\"Deselecteer\"} else {this.innerHTML=\"Selecteer\"}' href='#'>" + href_text +  "</a></div>"
        null
        true
        false
    )
    feature.popup = popup
    map.addPopup popup


#######################################################
# OpenLayers GeoJSON graph                            #
#######################################################


RiverLayerRule = (from, to, color) ->
    rule = new OpenLayers.Rule(
        filter: new OpenLayers.Filter.Comparison
            type: OpenLayers.Filter.Comparison.BETWEEN
            property: "target_difference"
            lowerBoundary: from
            upperBoundary: to
        symbolizer:
            fillColor: color
            strokeColor: color
            strokeWidth: STROKEWIDTH
    )
    rule

JSONRiverLayer = (name, json) ->
    rules = [
        new OpenLayers.Rule
            filter: new OpenLayers.Filter.Comparison
                type: OpenLayers.Filter.Comparison.GREATER_THAN
                property: "target_difference"
                value: 2.00
            symbolizer:
                fillColor: RIVERLEVEL9
                strokeColor: RIVERLEVEL9
                strokeWidth: STROKEWIDTH

        RiverLayerRule 1.00, 2.00, RIVERLEVEL8
        RiverLayerRule 0.80, 1.00, RIVERLEVEL7
        RiverLayerRule 0.60, 0.80, RIVERLEVEL6
        RiverLayerRule 0.40, 0.60, RIVERLEVEL5
        RiverLayerRule 0.20, 0.40, RIVERLEVEL4
        RiverLayerRule 0.00, 0.20, RIVERLEVEL3
        RiverLayerRule -0.20, -0.00, RIVERLEVEL2
        RiverLayerRule -0.40, -0.20, RIVERLEVEL1

        new OpenLayers.Rule
            filter: new OpenLayers.Filter.Comparison
                type: OpenLayers.Filter.Comparison.LESS_THAN
                property: "target_difference"
                value: -0.40
            symbolizer:
                fillColor: RIVERLEVEL0
                strokeColor: RIVERLEVEL0
                strokeWidth: STROKEWIDTH
        # Keep in sync with the legend in views.py!
        new OpenLayers.Rule
            elseFilter: true
            symbolizer:
                strokeOpacity: 0.0
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
            fillColor: MEASURECOLOR
            strokeColor: MEASURECOLOR
            fillOpacity: 0.7
        OpenLayers.Feature.Vector.style["default"]))

    styleMap.styles["default"].addRules [ new OpenLayers.Rule(
        filter: new OpenLayers.Filter.Comparison(
            type: OpenLayers.Filter.Comparison.EQUAL_TO
            property: "selected"
            value: true
        )
        symbolizer:
          fillColor: SELECTEDMEASURECOLOR
          strokeColor: SELECTEDMEASURECOLOR
          fillOpacity: 0.7
    ), new OpenLayers.Rule(elseFilter: true) ]


    geojson_format = new OpenLayers.Format.GeoJSON()
    vector_layer = new OpenLayers.Layer.Vector(name,
        styleMap: styleMap
    )

    map.addLayer vector_layer
    vector_layer.addFeatures geojson_format.read(json)
    selectCtrl = new OpenLayers.Control.SelectFeature(vector_layer,
        clickout: true
        callbacks:
            click: (feature) -> showPopup feature
    )

    map.addControl selectCtrl
    selectCtrl.activate()


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


showCityTooltip = (x, y, contents) ->
  $("<div class=\"citytooltip\">" + contents + "</div>").css(
    position: "absolute"
    display: "none"
    top: y
    left: x
    color: "#262626"
    padding: "2px"
  ).appendTo("body").fadeIn 200


setFlotSeries = (data) ->
    if data.length > 0
        window.min_graph_value = data[0].location
        window.max_graph_value = data[data.length-1].location

        setMeasureResultsGraph data
        setMeasureSeries()


setMeasureSeries = () ->
    json_url = $('#blockbox-table').data('measure-list-url')
    cities_list_url = $('#blockbox-table').data('cities-list-url')
    $.getJSON json_url + '?' + new Date().getTime(), (data) ->
        setMeasureGraph data.measures, data.cities


setMeasureResultsGraph = (json_data) ->
    vertex = ([num.location, num.vertex_level] for num in json_data)
    reference = ([num.location, num.reference_target] for num in json_data)
    measures = ([num.location, num.measures_level] for num in json_data)
    window.vertex = vertex
    window.measures = measures
    selected_river = $("#blockbox-river .chzn-select")[0].value

    ed_data = [
        label: "MHW-opgave"
        # Vertex is in NAP, reference too. Reference is zero, by definition,
        # so from both we subtract the vertex.
        data: vertex
        points:
            show: false

        lines:
            show: true

        color: GRAY
    ,
        label: "Doelwaarde"
        # This one is always, per definition, zero. This is what we should
        # reach.
        data: reference
        points:
            show: false

        lines:
            show: true
            lineWidth: 2

        color: BLUE
    ,
        label: "Effect maatregelen"
        # All measures are mostly negative, so we add them to the vertex,
        # which pulls it downwards in the direction of the reference value.
        data: measures
        points:
            show: false

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
            container: $("#measure_results_graph_legend")
            labelFormatter: (label, series) ->
                cb = label
                cb

    pl_lines = $.plot($("#measure_results_graph"), ed_data, options)
    window.topplot = pl_lines

    # $("#measure_results_graph").bind "plotclick", (event, pos, item) ->
    #     if item
    #         refreshGraph()


setMeasureGraph = (control_data, cities_data) ->

    measures = ([num.km_from, num.type_index, num.name, num.short_name, num.measure_type] for num in control_data when num.selectable and not num.selected and num.show)
    selected_measures = ([num.km_from, num.type_index, num.name, num.short_name, num.measure_type] for num in control_data when num.selected and num.show)
    non_selectable_measures = ([num.km_from, num.type_index, num.name, num.short_name, num.measure_type] for num in control_data when not num.selectable and num.show)
    cities = ([city[0], 8, city[1]] for city in cities_data)

    label_mapping = {}
    for measure in control_data
        label_mapping[measure.type_index] = measure.type_indicator
    yticks = ([key, value] for key, value of label_mapping)
    yticks = _.sortBy yticks, (u) -> u[0]

    selected_river = $("#blockbox-river .chzn-select")[0].value
    d4 = undefined
    d5 = undefined
    pl_lines = undefined

    options =
        xaxis:
            min: window.min_graph_value
            max: window.max_graph_value
            reserveSpace: true
            position: "bottom"

        yaxis:
            reserveSpace: true
            labelWidth: 21
            position: "left"
            tickDecimals: 0
            ticks: yticks

        grid:
            minBorderMargin: 20
            clickable: true
            hoverable: true
            borderWidth: 1
            # labelMargin:-50

        legend:
            container: $("#measures_legend")

    measures_controls = [

        data: cities
        points:
            show: true
            fillColor: BLACK
        lines:
            show: false
        color: BLACK
        hoverable: false
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
    pl_control = $.plot($("#measure_graph"), measures_controls, options)

    $("#measure_graph").bind "plotclick", (event, pos, item) ->
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
    $("#measure_graph").bind "plothover", (event, pos, item) ->

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

    # Cleanup city tool tips
    $('.citytooltip').remove()
    city_points = pl_control.getData()[0]
    offset = $("#measure_graph").offset()
    graphx = offset.left
    graphy = offset.top - 10

    width = $(window).width() - 400
    for point in city_points.data
        # Filter on cities that are in the km range of the river.
        if window.min_graph_value <= point[0] <= window.max_graph_value
            px = graphx + city_points.xaxis.p2c(point[0])
            py = graphy + city_points.yaxis.p2c(point[1])
            text = point[2]
            if px > width and text.length > 5
                # Don't let the text overflow into the legend/end of screen.
                px -= (text.length * 4)
            showCityTooltip(px, py, text)

resize_graphs = ->
    clearTimeout doit
    doit = setTimeout(->
        $('#measure_results_graph').empty()
        $('#measure_graph').empty()

        $('#measure_results_graph').css('width', '100%')
        $('#measure_graph').css('width', '100%')

        measuresMapView.render(false, false)
    ,300)

$('.btn.collapse-sidebar').click ->
    resize_graphs()

$('.btn.collapse-rightbar').click ->
    resize_graphs()

doit = undefined
$(window).resize ->
    resize_graphs()

window.resize_graphs = resize_graphs

$(".blockbox-toggle-measure").live 'click', (e) ->
    e.preventDefault()
    toggleMeasure $(@).data('measure-id')

$("#blockbox-deselect-all-measures").live 'click', (e) ->
    e.preventDefault()
    deselectAllMeasures()

setup_map_legend = ->
    $('.legend-riverlevel-9').css("background-color", RIVERLEVEL9)
    $('.legend-riverlevel-8').css("background-color", RIVERLEVEL8)
    $('.legend-riverlevel-7').css("background-color", RIVERLEVEL7)
    $('.legend-riverlevel-6').css("background-color", RIVERLEVEL6)
    $('.legend-riverlevel-5').css("background-color", RIVERLEVEL5)
    $('.legend-riverlevel-4').css("background-color", RIVERLEVEL4)
    $('.legend-riverlevel-3').css("background-color", RIVERLEVEL3)
    $('.legend-riverlevel-2').css("background-color", RIVERLEVEL2)
    $('.legend-riverlevel-1').css("background-color", RIVERLEVEL1)
    $('.legend-riverlevel-0').css("background-color", RIVERLEVEL0)
    $('.legend-measure').css("background-color", MEASURECOLOR)
    $('.legend-selected-measure').css("background-color", SELECTEDMEASURECOLOR)


km_line_layer = ->
    console.log "WMS"
    wms = new OpenLayers.Layer.WMS("5KM layer", "http://test-geoserver1.lizard.net/geoserver/deltaportaal/wms"
        layers: "deltaportaal:5km_rivieren"
        transparent: true,
    ,
        opacity: 1
    )
    map.addLayer wms
    `undefined`

$(document).ready ->
    setup_map_legend()
    $("#blockbox-river .chzn-select").chosen().change(
        () ->
            selectRiver @value
            @
        )
    updateVertex()
    $("#blockbox-vertex .chzn-select").chosen().change(
        () ->
            selectVertex @value
            @
        )
    km_line_layer()
    $('#measures-table-top').tablesorter()
    @
