$(document).ready(function(){
    socket.on('edit_task', data => {
        console.log(socket.id, 'responding to edit_task')
        console.log('data:', data)
        const task = document.getElementById(data.taskID);
        const taskName = task.querySelector('.task-name');
        const taskDescription = task.querySelector('.task-description');

        taskName.value = data.taskName;
        taskDescription.innerText = data.taskDescription;
    });
})

const setTaskFieldsDisabled = function(task, disabled) {
    task.querySelector('.task-name').disabled = disabled
    task.querySelector('.task-description').contentEditable = !disabled;
}

const addTaskEditEvents = function(task) {
    const editButton = task.querySelector('.task-edit');
    const taskFields = task.querySelectorAll('.task-name, .task-description');

    // Add event listener to the buttons
    editButton.addEventListener('click', function(event) {
        event.preventDefault();
        const parentTask = editButton.parentElement.parentElement;

        setTaskFieldsDisabled(parentTask, false);
    });

    // Add event listener to the fields
    taskFields.forEach(field => {
        field.addEventListener('keyup', function(event) { 
            if(event.key === 'Enter') {
                const parentTask = event.target.parentElement;
                const taskName = parentTask.querySelector('.task-name').value;  
                const taskDescriptionEle = parentTask.querySelector('.task-description');

                event.preventDefault();
                taskDescriptionEle.innerText = taskDescriptionEle.innerText.trim();

                socket.emit('edit_task', { 
                    taskID: parentTask.id, 
                    taskName: taskName, 
                    taskDescription: taskDescriptionEle.innerText,
                    room: boardID
                });

                setTaskFieldsDisabled(parentTask, true);
            }
        });
    });
}

tasks.forEach(task => {
    addTaskEditEvents(task);
});






