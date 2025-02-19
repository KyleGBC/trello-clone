const createTaskButtons = document.querySelectorAll('.create-task-button');  

$(document).ready(function(){
    socket.on('create_task', data => {
        console.log(socket.id, 'responding to create_task')
        console.log('data:', data)
        const list = document.getElementById(data.listID);
        newTask = createTaskElement(list, data.taskID);
    });
    
});

const createTaskElement = function(list, taskID) {
    const task = document.createElement('div');   
    task.classList.add('task');
    task.setAttribute('draggable', 'true');
    task.id = 'task-' + taskID;

    const task_name = document.createElement('input');
    task_name.type = 'text';
    task_name.placeholder = 'Task name';
    task_name.disabled = true;
    task_name.classList.add('task-name', 'form-field');
    task_name.title = "Task name";

    const task_description = document.createElement('div');
    task_description.setAttribute('fake-placeholder', 'Task description');
    task_description.contenteditable = false;
    task_description.classList.add('task-description', 'form-field');
    task_description.title = "Task description"

    const task_buttons = document.createElement('div');
    task_buttons.classList.add('task-buttons');

    const task_delete = document.createElement('button');
    task_delete.innerHTML = 'Delete';
    task_delete.classList.add('task-delete', 'form-button');
    
    const task_edit = document.createElement('button');
    task_edit.innerHTML = 'Edit';
    task_edit.classList.add('task-edit', 'form-button');
    
    task.appendChild(task_name);
    task.appendChild(task_description);
    task_buttons.appendChild(task_delete);
    task_buttons.appendChild(task_edit);
    task.appendChild(task_buttons);
    list.querySelector('.board-list').appendChild(task);

    addTaskDragEvents(task);
    addTaskEditEvents(task);
    addTaskDeleteEvents(task);

    return task;
}


createTaskButtons.forEach(button => {
    button.addEventListener('click', function() {
        const list = button.parentElement;

        socket.emit('create_task', { boardID: boardID, listID: list.id, room: boardID}, (newTaskID) => { 
            newTask = createTaskElement(list, newTaskID);
            newTask.focus();
        });

        socket.emit('refresh_board_stats', { boardID: boardID } );
    });
});

