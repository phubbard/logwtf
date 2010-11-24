
function pull_base_logpage()
{
    // Grab json-encoded config from webserver
    var http = new XMLHttpRequest();

    http.open("GET", "http://localhost:2200/get_configuration");
    http.onreadystatechange = function() {
        if (http.readyState == 4) {
            kickoff(http.responseText);
            return(null);
        }
        else return(null);
    }
    http.send(null);
    return(null);
}

function kickoff(respText)
{
    // Decode configuration and pass to next step
    // See http://en.wikipedia.org/wiki/Json
    var json_config = JSON.parse(respText);

    draw_basic_canvas(json_config.num_cols, json_config.column_names);
}

function draw_basic_canvas(num_cols, column_names)
{
    var canvas = document.getElementById("log_canvas");
    var context = canvas.getContext("2d");

    // Resize to fill window, side effect is to clear content
    canvas.height = $(window).height();
    canvas.width = $(window).width();

    // See http://diveintohtml5.org/canvas.html
    if (num_cols > 1)
    {
        var cwidth = $(window).width() / num_cols;
        for (var idx = 1; idx < num_cols; idx++)
        {
            var x = idx * cwidth;
            context.moveTo(x, 0);
            context.lineTo(x, $(window).height());
        }
        context.strokeStyle = "#000";
        context.stroke();

        // Now print column names
        context.font = "bold 10px";
        context.textBaseline = "top";

        for (var idx = 0; idx < num_cols; idx++)
        {
            context.fillText(column_names[idx], idx * cwidth, 0);
        }
    }
}

function draw_log_message(row, col, msg)
{
    var canvas = document.getElementById("log_canvas");
    var context = canvas.getContext("2d");

    context.font = "bold 10px";
    context.textBaseline="top"

    // Given canvas coordinates, display a message
    context.fillText(msg, row, col);
}
