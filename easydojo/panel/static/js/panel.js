$(document).ready(function () {
    var ws = new WebSocket("ws://" + document.location.host + "/ws");
    ws.onmessage = function(evt) {
        if (evt.data == 'S') {
            $('#signal').attr('class', 'green');
        }
        else if (evt.data == 'E') {
            $('#signal').attr('class', 'red');
        }
        else {
            $('#countdown').html(evt.data);
        }
    };
});


