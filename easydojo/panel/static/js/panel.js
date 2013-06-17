counter_start = function () {
    $('#counter').html("");
    $('#counter').countdown({
        image: '/static/img/digits.png',
        startTime: '05:00',
        timerEnd: counter_start,
        format: 'mm:ss'
    });
}
$(document).ready(function () {
    counter_start();
    var ws = new WebSocket("ws://" + document.location.host + "/ws");
    ws.onmessage = function(evt) {
        if (evt.data == 'S') {
            $('#signal').attr('class', 'green');
        }
        else if (evt.data == 'E') {
            $('#signal').attr('class', 'red');
        }
    };
});


