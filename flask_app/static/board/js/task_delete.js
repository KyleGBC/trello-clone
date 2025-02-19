$(document).ready(function(){
    socket.on('delete_task', data => {
        console.log(socket.id, 'responding to edit_task')
        console.log('data:', data)

        const task = document.getElementById(data.taskID);
        task.remove();
    });
})


const addTaskDeleteEvents = function(task) {
    const deleteButton = task.querySelector('.task-delete');

    // Add event listener to the delete button
    deleteButton.addEventListener('click', function(event) {
        event.preventDefault();
        const parentTask = deleteButton.parentElement.parentElement;

        socket.emit('delete_task', { taskID: parentTask.id, room: boardID });
        socket.emit('refresh_board_stats', { boardID: boardID } );

        parentTask.remove();
    });
}

tasks.forEach(task => { 
    addTaskDeleteEvents(task); 
});

