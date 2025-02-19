const tasks = document.querySelectorAll('.task');
const boardID = document.querySelector('.board').id;

$(document).ready(function(){
    socket = io.connect(window.location.protocol + '//' + location.hostname + ':' + location.port);

    socket.on('connect', function() {
        socket.emit('join', {room: boardID});
    });

    socket.on('delete_board', function() {
        window.location.href = '/home';
    });
});

window.onbeforeunload = function () {
    socket.emit('leave', {room: boardID});
}


