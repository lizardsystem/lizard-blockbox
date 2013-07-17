$("table#last-commands-table").on("click", "tr td a.toggle-visibility", function (event) {
    var $a = $(this);
    var $span = $("#" + $a.attr("data-span-id"));

    if ($span.attr("data-visible") === "0") {
        $span.css("display", "block");
        $span.attr("data-visible", "1");
        $a.text('verberg output');
    } else {
        $span.css("display", "none");
        $span.attr("data-visible", "0");
        $a.text("toon output");
    }
    event.preventDefault();
});


/* Constantly rebuild the last imports table, if there is something
 * still happening */
var automatic_import = (function () {

    var update_on_next_ticks = 1;

    var request_updates = function (n) {
        if (n === null) {
            n = 1;
        }
        update_on_next_ticks += n;
    };

    var tick = function () {
        if (update_on_next_ticks > 0) {
            update_on_next_ticks--;
            update_table();
        }
        setTimeout(tick, 1000);
    };

    var update_table = function () {
        var url = $("#last-commands-table").attr("data-update-url");
        $.getJSON(url, function (data) {
            var ids_to_keep = {}; // Track imports we are still showing

            $.each(data, function (i, commandrun) {
                // commandrun is an object with attributes:
                // runid, command, time, finished, success, user, output
                ids_to_keep[commandrun.runid] = true;

                var output_visible = "0";
                var output_display = "none";
                var output_text = "toon output";

                // If this run's tr element already exists, we remove it and
                // replace it by a new one, but keeping the state of the old one
                // (mostly whether output is already open).
                var $tr = $("table#last-commands-table > tbody > tr#" + commandrun.runid);
                if ($tr.length > 0) {
                    var $span = $tr.find("td > span#output-run-"+commandrun.runid);
                    output_visible = $span.attr("data-visible");
                    output_display = $span.css("display");
                    var $a = $tr.find("td > a.toggle-visibility");
                    output_text = $a.contents();
                    $tr.remove();
                }

                var $to_append_to = $("table#last-commands-table");

                var $new_tr = ($("<tr>").attr("id", commandrun.runid)
                       .append($("<td>").append(commandrun.command))
                       .append($("<td>").append(commandrun.time))
                       .append($("<td>").append(commandrun.user))
                       .append($("<td>").append(commandrun.finished ? "Ja" : "Nee"))
                       .append($("<td>").append(commandrun.finished ?
                                                (commandrun.success ? "Ja" : "Nee") : ""))
                       .append($("<td>").append(
                           ($("<a>")
                            .attr("data-span-id", "output-run-"+commandrun.runid)
                            .attr("class", "toggle-visibility")
                            .attr("href", "").append(output_text)))
                               .append($("<span>")
                                       .attr("id", "output-run-"+commandrun.runid)
                                       .attr("data-visible", output_visible)
                                       .css("display", output_display)
                                       .append($("<pre>")
                                               .append(commandrun.output))))
                      );

                $to_append_to.append($new_tr);

                request_updates(commandrun.finished ? 0 : 1);
            });

            $("#last-commands-table > tbody > tr").each(function (i, tr) {
                tr = $(tr);

                if (ids_to_keep[tr.attr("id")] !== true) {
                    tr.remove();
                }
            });
        });
    };

    tick();

    return {
        request_updates: request_updates
    };
})();

$("button.start-import-button").click(function () {
    var url = $(this).attr("data-url");
    $.post(url, function () {
        automatic_import.request_updates(5);
    });
    return 0;
});
