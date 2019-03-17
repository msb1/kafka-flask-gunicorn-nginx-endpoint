var producer_socket;
var consumer_socket;
var epd_socket;


$(document).ready(function(){
    //connect to the socket server.
    producer_socket = io.connect('http://' + document.domain + ':' + location.port + '/producer');
    var msg_received = [];

    //receive details from server
    producer_socket.on('newMessage', function(msg) {
        console.log("Received producer: " + msg.msg);
        //maintain a list of ten numbers
        if (msg_received.length >= 4){
            msg_received.shift()
        }            
        msg_received.push(msg.msg);
        msg_string = '';
        for (var i = 0; i < msg_received.length; i++){
            msg_string = msg_string + '<p>' + msg_received[i].toString() + '</p>';
        }
        $('#producer').html(msg_string);
    });
});

$(document).ready(function(){
    //connect to the socket server.
    consumer_socket = io.connect('http://' + document.domain + ':' + location.port + '/consumer');
    var msg_received = [];

    //receive details from server
    consumer_socket.on('newMessage', function(msg) {
        console.log("Received consumer: " + msg.msg);
        //maintain a list of ten numbers
        if (msg_received.length >= 4){
            msg_received.shift()
        }            
        msg_received.push(msg.msg);
        msg_string = '';
        for (var i = 0; i < msg_received.length; i++){
            msg_string = msg_string + '<p>' + msg_received[i].toString() + '</p>';
        }
        $('#consumer').html(msg_string);
    });
});

$(document).ready(function(){
    //connect to the socket server.
    epd_socket = io.connect('http://' + document.domain + ':' + location.port + '/epd');

    //receive details from server
    epd_socket.on('newMessage', function(msg) {
        console.log("Received status: " + msg.msg);
        $('#status').html(msg.msg.toString());
    });
});


function start_producer() {
	producer_socket.emit('message', 'start');
}

function start_consumer() {
	consumer_socket.emit('message', 'start');
}

function stop_producer() {
	producer_socket.emit('message', 'stop');
}

function stop_consumer() {
	consumer_socket.emit('message', 'stop');
}


