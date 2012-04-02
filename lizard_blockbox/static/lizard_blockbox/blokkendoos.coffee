# Constants
FLOT_URL = "/"
JSON_COMBINATIONS_URL = "/"


# Initialization
current_reach_measure_ids = undefined
selected_measure_ids = undefined
available_measure_labels = {}
clicked = []
blockedList = {}
blockedByList = {}

processCompleted =
    'measuresLoaded': false
    'combinationsLoaded': false

diffArray = (bigArray, smallArray) ->
    $.grep bigArray, (bigArrayElement) ->
        $.inArray(bigArrayElement, smallArray) < 0
        
setupIfAllDataReady = ->
    if processCompleted.combinationsLoaded and processCompleted.measuresLoaded
        $(document).ready ->
            setFlotSeries FLOT_URL
            $("#selected_measures").updateMeasuresTable {}, []
            $("#other_selected_measures").updateOtherMeasuresTable {}, []




jQuery( ($) ->
    $.fn.updateMeasuresTable = (measure_ids, available_measure_labels) ->
        target = $(this)
        table = $("""
            <table class='generic-table' 'border='0' cellspacing='5' cellpadding='5' id='measure_table'>
                <thead>
                <tr class='header'>
                    <th>Maatregel</th>
                    <th>Code</th>
                    <th>Kosten &uarr;</th>
                </tr>
                </thead>
                <tbody/>
            </table>""")

        measure_labels = $.map(measure_ids, (id) ->
            available_measure_labels[id]
        )
        
        createSumRow = ->
            sum = 0
            _.each measure_labels, (label) ->
                sum = sum + label[2].cost

            target.find("tbody").children().last().parent().append """<tr class='sum'><td><strong>Totaal</strong></td><td></td><td>""" + sum.toFixed(1) + " mln</td></tr>"
        target.empty()
        target.html table
        _.each measure_labels, (label) ->
            target.find("tbody").append "<tr class='row'><td>" + label[2].title + "</td><td>" + label[2].code + "</td><td>" + label[2].cost + " mln</td></tr>"

        createSumRow()
        
        target.find("tbody").append """<tr class='row'><td>...</td><td>...</td><td>...</td></tr>"""  if _.isEmpty(measure_ids)
        @
)


jQuery( ($) ->
    $.fn.updateOtherMeasuresTable = (measure_ids, selected_measure_labels) ->
    
        target = $(this);
        table = $("""
            <table border='0' cellspacing='5' cellpadding='5' id='other_measure_table'>
                <thead>
                <tr class='header'>
                    <th>Maatregel</th>
                    <th>Code</th>
                    <th>Kosten &uarr;</th>
                </tr>
                </thead>
                <tbody/>
            </table>""")

        measure_labels = $.map(measure_ids, (id) ->
            available_measure_labels[id]
        )
        
        
        createSumRow = ->
            sum = 0
            _.each measure_labels, (label) ->
                sum = sum + label[2].cost
            target.find("tbody").children().last().parent().append """<tr class='sum'><td><strong>Totaal</strong></td><td></td><td>""" + sum.toFixed(1) + """ mln</td></tr>"""

        target.empty()
        target.html table
        _.each measure_labels, (label) ->
            target.find("tbody").append """<tr class='row'><td>""" + label[2].title + """</td><td>""" + label[2].code + """</td><td>""" + label[2].cost + """ mln</td></tr>"""
        createSumRow();

        target.find("tbody").append """<tr class='row'><td>...</td><td>...</td><td>...</td></tr>"""  if _.isEmpty(measure_labels)
        @
)



jQuery.getJSON FLOT_URL, {}, (json, textStatus) ->
    json_data = json
    
    current_reach_measure_ids = $.map(json_data.measure_control_data, (label) ->
        id = label[2].id
        available_measure_labels[id] = [ label ]
        id
    )
    selected_measure_ids = $.map(json_data.selected_measures, (label) ->
        id = label[2].id
        available_measure_labels[id] = [ label ]
        id
    )
    processCompleted.measuresLoaded = true
    setupIfAllDataReady()
    


jQuery.getJSON JSON_COMBINATIONS_URL, {}, (json, textStatus) ->
    combinations = json
    processCompleted.combinationsLoaded = true
    setupIfAllDataReady()


showTooltip = (x, y, contents) ->
    $("<div id=\"tooltip\">#{contents}</div>").css(
        opacity: "1.00"
        position: "absolute"
        display: "none"
        top: y - 35
        left: x + 5
        border: "1px solid #046f96"
        padding: "2px"
        backgroundcolor: "#fee"
    ).appendTo("body").fadeIn 200
  
remove_item_from_array = (array, removeItem) ->
    $.grep array, (value) ->
        value isnt removeItem



draw_point = (datapoint, plotobj, fillcolor, radius, linewidth, linecolor) ->
    axes = plotobj.getAxes()
    ctx = plotobj.getCanvas().getContext("2d")
    offset = plotobj.getPlotOffset()
    x = offset.left + axes.xaxis.p2c(datapoint[0])
    y = offset.top + axes.yaxis.p2c(datapoint[1])
    ctx.lineWidth = linewidth
    ctx.beginPath()
    ctx.arc x, y, radius, 0, Math.PI * 2, false
    ctx.closePath()
    ctx.fillStyle = fillcolor
    ctx.strokeStyle = linecolor
    ctx.fill()
    ctx.stroke()
    true
    
    
getIndicesForCombinations = (series_data, combos) ->
    indices = []
    _.each series_data, (value, counter) ->
        indices.push counter  if _.include(_.flatten(combos), value[2].code)

    indices    
  
  
  
refreshGraph = (data) ->
    pl_lines.setData [
        data: data.basecase_data
        points:
            show: true
            symbol: "diamond"

        lines:
            show: true

        color: "blue"
    ,
        data: data.result_data
        points:
            show: true
            symbol: "circle"

        lines:
            show: true

        color: "yellow"
    ]
    pl_lines.setupGrid()
    pl_lines.draw()
    pl_linesx
    
    
    
window.setFlotSeries = (url) ->
    data = undefined
    $.ajax
        type: "POST"
        url: url
        dataType: "json"
        success: (data) ->
            if data.basecase_data.length
                setPlaceholderTop data.basecase_data, data.result_data
                setPlaceholderControl data.measure_control_data
                refreshGraph data
            else
                $("#graph_errors").html """
                    <p class=\"error\">
                        Geen basis data beschikbaar voor deze raai.
                    </p>"""

    error: (data) ->
        $("#graph_errors").html """
            <p class=\"error\">
                Geen data gevonden voor deze raai en dit toekomstbeeld
            </p>"""
            
            
            
            
setPlaceholderTop = (basecase_data, result_data) ->
    options = undefined
    ed_data = undefined

    options =
        xaxis:
            transform: (v) -> -v
            position: "top"

        yaxis:
            min: -1
            max: 1
            reserveSpace: true
            labelWidth: 21

        grid:
            clickable: true
            borderWidth: 1

        legend:
            show: true
            noColumns: 4
            container: $("#placeholder_top_legend")

    ed_data = [
        data: json_data.basecase_data
        label: "Uitgangssituatie"
        points:
            show: true
            symbol: "diamond"
        lines:
            show: true

        color: "blue"
    ]
    pl_lines = $.plot($("#placeholder_top"), ed_data, options)
    
    
    
getTicks = ->
    ticks = []
    _.each json_data.measure_control_data, (val, count) ->
        ticks[val[1]] = [ val[1], val[2].type ]

    ticks = remove_item_from_array(ticks, `undefined`)
    ticks
    
    
    
    
    
    
    
    
setPlaceholderControl = (control_data) ->
    add_code_to_blockedlist = (key, value) ->
        blockedList[key] = []  unless blockedList[key]
        blockedList[key].push value  unless _.include(blockedList[key], [ value ])
        blockedList
    add_code_to_bbl = (key, value) ->
        blockedByList[key] = []  unless blockedByList[key]
        blockedByList[key].push value  unless _.include(blockedByList[key], [ value ])
        blockedByList
    highlight_initial = (item, id) ->
        if _.include(selected_measure_ids, item[2].id)
            clicked.push id
            code = item[2].code
            combos = [ combinations[0][code] ]
            indices = getIndicesForCombinations(pl_control.getData()[0].data, combos)
            _.each indices, (value, count) ->
                loopcode = pl_control.getData()[0].data[value][2].code
                add_code_to_blockedlist code, loopcode
                add_code_to_bbl loopcode, code
                draw_point pl_control.getData()[0].data[value], pl_control, "orange", pl_control.getData()[0].points.radius, pl_control.getData()[0].points.lineWidth, pl_control.getData()[0].color
            draw_point item, pl_control, "blue", pl_control.getData()[0].points.radius, pl_control.getData()[0].points.lineWidth, pl_control.getData()[0].color

    highlight_point_on_click = (item) ->
        clicked.push item.dataIndex
        other_measures = []
        current_reach_selected_measures = []
        current_reach_selected_measure_ids = []
        _.each clicked, (val, counter) ->
            current_reach_selected_measures.push item.series.data[val][2]
            current_reach_selected_measure_ids.push item.series.data[val][2].id

        $("#selected_measures").updateMeasuresTable current_reach_selected_measure_ids, available_measure_labels
        code = item.series.data[item.dataIndex][2].code
        combos = [ combinations[0][code] ]
        indices = getIndicesForCombinations(item.series.data, combos)
        _.each indices, (value, count) ->
            loopcode = item.series.data[value][2].code
            add_code_to_blockedlist code, loopcode
            add_code_to_bbl loopcode, code
            draw_point item.series.data[value], pl_control, "orange", item.series.points.radius, item.series.points.lineWidth, item.series.color

        draw_point item.datapoint, pl_control, "blue", item.series.points.radius, item.series.points.lineWidth, item.series.color

    options = undefined
    ed_data = undefined
    x_min = undefined
    x_max = undefined
    y_min = undefined
    y_max = undefined
    options =
        xaxis:
            transform: (v) -> -v
            inverseTransform: (v) -> -v
            show: true
            position: "bottom"
            labelWidth: 50
            min: pl_lines.getAxes().xaxis.min
            max: pl_lines.getAxes().xaxis.max

        yaxis:
            reserveSpace: true
            labelWidth: 21
            position: "left"
            show: false

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

    measure_controls = [
        label: "Serie 2"
        data: control_data
        points:
            show: true
            symbol: "circle"
            radius: 5
            lineWidth: 2

        lines:
            show: false

        color: "red"
    ]

    pl_control = $.plot($("#placeholder_control"), measure_controls, options)

    $("#placeholder_control").bind "plothover", (event, pos, item) ->
        if item
            $("#tooltip").remove()
            showTooltip item.pageX, item.pageY, item.series.data[item.dataIndex][2].code + " (" + item.series.data[item.dataIndex][2].title + ")"
        else
            $("#tooltip").remove()

    other_measures = []
    _.each pl_control.getData()[0].data, (val, id) ->
        highlight_initial val, id

    current_reach_selected_measure_ids = $.map(clicked, (i) ->
        pl_control.getData()[0].data[i][2].id
    )

    $("#selected_measures").updateMeasuresTable current_reach_selected_measure_ids, available_measure_labels
    other_reach_measure_ids_selected = _.difference(selected_measure_ids, current_reach_selected_measure_ids)
    $("#other_selected_measures").updateOtherMeasuresTable other_reach_measure_ids_selected, json_data.selected_measures
    $("#placeholder_control").bind "plotclick", (event, pos, item) ->
        return false unless item
        return false if _.include(_.keys(blockedByList), item.series.data[item.dataIndex][2].code)
        point_is_selected = _.include(clicked, item.dataIndex)
        unless point_is_selected
            highlight_point_on_click item
        else
            idx = $.inArray(item.dataIndex, clicked)
            clicked.splice idx, 1  if idx isnt -1
            axes = pl_control.getAxes()
            ctx = pl_control.getCanvas().getContext("2d")
            offset = pl_control.getPlotOffset()
            code = item.series.data[item.dataIndex][2].code
            draw_point item.datapoint, pl_control, "white", item.series.points.radius, item.series.points.lineWidth, item.series.color
            current_reach_selected_measure_ids = $.map(clicked, (id) ->
                item.series.data[id][2].id
            )
            $("#selected_measures").updateMeasuresTable current_reach_selected_measure_ids, available_measure_labels
            _.each blockedList[code], (blocked_item, counter) ->
                different = _.difference(blockedByList[blocked_item], [ code ])
                if different.length is 0
                    _.each item.series.data, (datapoint, counter) ->
                        if datapoint[2].code is blocked_item
                            draw_point datapoint, pl_control, "white", item.series.points.radius, item.series.points.lineWidth, item.series.color
                            blockedByList[blocked_item] = remove_item_from_array(blockedByList[blocked_item], code)
                            delete blockedByList[blocked_item]  if blockedByList[blocked_item].length is 0

          delete blockedList[code]
    result_ids = []
    _.each clicked, (value, counter) ->
        result_ids.push item.series.data[value][2].id

    result_ids = result_ids.join(",")
    current_reach_measure_ids_clicked = []
    _.each clicked, (i) ->
        current_reach_measure_ids_clicked.push item.series.data[i][2].id

    current_reach_measure_ids_unclicked = _.difference(current_reach_measure_ids, current_reach_measure_ids_clicked)
    all_selected_measure_ids = _.difference(_.union(selected_measure_ids, current_reach_measure_ids_clicked), current_reach_measure_ids_unclicked)
    $.post FLOT_URL,
        has_measures: true
        measures: all_selected_measure_ids
        , ((data) ->
        refreshGraph data
        ), "json"