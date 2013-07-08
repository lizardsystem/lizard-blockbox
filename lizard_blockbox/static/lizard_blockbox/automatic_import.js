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
                ids_to_keep[commandrun.runid] = true;

                // import is an object with attributes:
                // runid, command, time, finished, success, user, output
                var $tr = $("table#last-commands-table > tbody > tr#" + commandrun.runid);
                $tr.remove();

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
                            .attr("href", "").append("toon output")))
                               .append($("<span>")
                                       .attr("id", "output-run-"+commandrun.runid)
                                       .attr("data-visible", "0")
                                       .css("display", "none")
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

$("#start-import-button").click(function () {
    var url = $(this).attr("data-url");
    $.post(url, function () {
        automatic_import.request_updates(5);
    });
    return 0;
});
