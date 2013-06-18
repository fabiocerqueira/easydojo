$(document).ready(function () {
    var ws = new WebSocket("ws://" + document.location.host + "/ws");
    ws.onmessage = function(evt) {
        if (evt.data == 'S') {
            $('#signal').attr('class', 'green');
        }
        else if (evt.data == 'E') {
            $('#signal').attr('class', 'red');
        }
        else if (evt.data == 'pause') {
            if ($("#resume_pause").html() != "Resume")
                $("#resume_pause").html('Resume');
        }
        else if (evt.data == 'resume') {
            if ($("#resume_pause").html() != "Pause")
                $("#resume_pause").html('Pause');
        }
        else {
            $('#countdown').html(evt.data);
        }
    };

    $("#resume_pause").click(function() {
        ws.send('resume_pause');
    });
    $("#restart").click(function() {
        ws.send('restart');
    });

});


