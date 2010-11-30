// references --
// http://getfirebug.com/wiki/index.php/Console_API
// http://en.wikipedia.org/wiki/Javascript
// http://en.wikipedia.org/wiki/JavaScript_syntax
// https://developer.mozilla.org/En/XMLHttpRequest/Using_XMLHttpRequest
// http://getfirebug.com/wiki/index.php/Console_API
// http://developer.apple.com/library/safari/#documentation/AppleApplications/Conceptual/Safari_Developer_Guide/DebuggingYourWebsite/DebuggingYourWebsite.html%23//apple_ref/doc/uid/TP40007874-CH8-SW2
// http://diveintohtml5.org/canvas.html
// http://en.wikipedia.org/wiki/Json
// http://jslint.com/

logwtf = {};
logwtf.base_url = 'http://localhost:2200';
logwtf.text_height = 10;

function main()
{
    // Top-level orchestration routine for the system.
    var config = pull_base_logpage();

    draw_basic_canvas(config.num_cols, config.column_names);
    write_logs(config.num_cols, config.column_names);
}

function pull_base_logpage()
{
    // Grab json-encoded config from webserver
    var http = new XMLHttpRequest();

    http.open("GET", logwtf.base_url + '/get_configuration', false);
    http.send(null);
    if (http.status == 200)
        return(JSON.parse(http.responseText))
    else
        alert('Unable to read base configuration from REST server!');
}

function draw_basic_canvas(num_cols, column_names)
{
    var canvas = document.getElementById("log_canvas");
    var context = canvas.getContext("2d");

    // Resize to fill window, side effect is to clear content
    canvas.height = $(window).height();
    canvas.width = $(window).width();

    // Draw column markers, simple vertical lines
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

function get_logfile(log_name)
{
    var result = "";
    var http = new XMLHttpRequest();
    // Blocking read
    var url = logwtf.base_url + '/' + log_name;
    http.open("GET", url, false);
    http.send(null);

    if (http.status == 200)
        return(JSON.parse(http.responseText));
    else
        return(null);
}

function write_logs(num_cols, column_names)
{
    // Pull the logs
    var logs = [];

    // get the logs
    for (var idx = 0; idx < num_cols; idx++)
    {
        var cur_log = get_logfile(column_names[idx]);
        logs.push(cur_log);
    }
    // Display the logfiles, columnwise indexing
    for (var cur_column = 0; cur_column < num_cols; cur_column++)
    {
        for (var row = 0; row < logs[cur_column].length; row++)
        {
            var col = ($(window).width() / num_cols) * cur_column;
            //console.info("cur_column: %d row: %d col: %d", cur_column, row, col);

            var cur_col = logs[cur_column];
            var cur_row = cur_col[row];
            // Abs pixel-relative timestamp for now
            draw_log_message(cur_row.delta_t * 10, col, cur_row.msg);
        }
    }

}

function draw_log_message(row, col, msg)
{
    var canvas = document.getElementById("log_canvas");
    var context = canvas.getContext("2d");

    context.font = "10px";
    context.textBaseline="top"

    // Given canvas coordinates, display a message
    context.fillText(msg, col, row);
    //console.debug(row, col, msg);
}
