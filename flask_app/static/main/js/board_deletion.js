$(document).ready(function(){
    socket.on('delete_board', data => {
        console.log(socket.id, 'responding to delete_board')
        console.log('data:', data)
        const board = document.getElementById(data.boardID);
        board.remove();
    });
});

boardContainer.querySelectorAll('.board-card-delete').forEach(deleteButton => {
    deleteButton.addEventListener('click', function(event) {
        event.preventDefault();
        const parentBoard = deleteButton.parentElement;
        const boardID = parentBoard.id;

        socket.emit('delete_board', { boardID: boardID }, function(response) {
            if(response.success === 1) {
                parentBoard.remove();
            }
        });
    });
});