/*
  Paul Hubbard
  11/22/10

  See https://github.com/phubbard/logwtf

 references --
 http://getfirebug.com/wiki/index.php/Console_API
 http://en.wikipedia.org/wiki/Javascript
 http://en.wikipedia.org/wiki/JavaScript_syntax
 https://developer.mozilla.org/En/XMLHttpRequest/Using_XMLHttpRequest
 http://getfirebug.com/wiki/index.php/Console_API
 http://developer.apple.com/library/safari/#documentation/AppleApplications/Conceptual/Safari_Developer_Guide/DebuggingYourWebsite/DebuggingYourWebsite.html%23//apple_ref/doc/uid/TP40007874-CH8-SW2
 http://diveintohtml5.org/canvas.html
 http://en.wikipedia.org/wiki/Json
 http://jslint.com/
 https://developer.mozilla.org/en/drawing_text_using_a_canvas
 http://uupaa-js-spinoff.googlecode.com/svn/trunk/uuCanvas.js/demo.canvas/8_2_canvas_measureText.htm
*/

logwtf = {};
//logwtf.base_url = 'http://137.110.111.241:2200';
logwtf.base_url = 'http://localhost:2200';
logwtf.text_height = 10; // pixels
logwtf.column_width = 100; //pixels, will be overriden at first load
logwtf.debug_color = '#0f0';
logwtf.info_color = '#00f';
logwtf.warn_color = '#ff0';
logwtf.error_color = '#f00';

function configure_slider(max_time)
{
    $( "#slider" ).bind("slidestop", function(event, ui) {on_slide(10.0);})
    //alert(max_time);
}

function on_slide(value)
{
    // Slider callback, eventually
    alert(value);
}

function main()
{
    // Top-level orchestration routine for the system.
    var config = pull_base_logpage();

    configure_slider(config.timespan);
    draw_basic_canvas(config.num_cols, config.column_names);
    console.info('span: ' + config.timespan);
    console.info('max : ' + config.max_messages);
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
        alert('Unable to read base configuration from REST server! Check ' + logwtf.base_url);
}

function draw_basic_canvas(num_cols, column_names)
{
    var canvas = document.getElementById("log_canvas");
    var context = canvas.getContext("2d");

    // Resize to fill window, side effect is to clear content
    canvas.height = $(window).height() * 0.98;
    canvas.width = $(window).width() * 0.98;

    // Figure how many rows we have and save
    logwtf.num_rows = $(window).height() / 10;
    // And column width too
    logwtf.column_width = $(window).width() / num_cols;

    // Draw column markers, simple vertical lines
    if (num_cols > 1)
    {
        for (var idx = 1; idx < num_cols; idx++)
        {
            var x = idx * logwtf.column_width;
            context.moveTo(x, 0);
            context.lineTo(x, $(window).height());
        }
        context.strokeStyle = "#000";
        context.stroke();

        // Now print column names
        context.font = "bold 10px";
        context.textBaseline = "top";

        for (var idx = 0; idx < num_cols; idx++)
            context.fillText(column_names[idx], (idx * logwtf.column_width) + 2, 0);
    }
}

function get_logfile(log_name)
{
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
    // Iterate over the column_names, pulling each from the server and rendering it.

    // We will hold all of the logfiles in an array
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
        for (var row = 0; row < Math.min(logwtf.num_rows, logs[cur_column].length); row++)
        {
            var col = ($(window).width() / num_cols) * cur_column;
            //console.info("cur_column: %d row: %d col: %d", cur_column, row, col);

            var cur_col = logs[cur_column];
            var cur_row = cur_col[row];
            // Abs pixel-relative timestamp for now
            //draw_log_message(cur_row.delta_t * 10, col, cur_row.msg);
            draw_log_message((row + 2) * logwtf.text_height, col, cur_row.msg, cur_row.level)
        }
    }

}

function draw_log_message(row, col, msg, level)
{
    var canvas = document.getElementById("log_canvas");
    var context = canvas.getContext("2d");

    context.font = logwtf.text_height + "px";
    context.textBaseline="top"
    if (level=='DEBUG')
        context.fillStyle = logwtf.debug_color;
    else if (level=='INFO')
        context.fillStyle = logwtf.info_color;
    else if (level=='WARNING')
        context.fillStyle = logwtf.warn_color;
    else if (level=='ERROR')
        context.fillStyle = logwtf.error_color;
    else
    {
        console.error('Unknown log level ' + level);
        context.fillStyle = logwtf.error_color;
    }

    // Figure out clipping
    //tl = context.measureText(msg);
    //console.info(tl);
    // Given canvas coordinates, display a message
    context.fillText(msg, col+2, row);
    //console.debug(row, col, msg);
}
