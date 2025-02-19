$(document).ready(function(){
    socket.on('move_task', data => {

        console.log(socket.id, 'responding to move_task')
        console.log('data:', data)
        // Find all involved elements on this client
        const destList = document.getElementById(data.destListID);
        const moved_task = document.getElementById(data.taskID);
        const afterTask = data.afterTaskID != null ? document.getElementById(data.afterTaskID) : null;
        
        moveTask(moved_task, destList, afterTask);
    });
});

const lists = document.querySelectorAll('.board-list-container');
let taskStartList = null;
let lastAfterTask = null;
let lastBeforeTask = null;

const getDragAdjacentElement = function(list, yPos, before=false) {
   const containerTasks = [...list.querySelectorAll('.task:not(.dragging)')];

    return containerTasks.reduce((current, candidate) => {
        const boundBox = candidate.getBoundingClientRect();
        const offset = yPos - boundBox.top - boundBox.height / 2;

        if(!before && offset < 0 && offset > current.offset) {
            return { offset: offset, element: candidate };
        }
        else if(before && offset > 0 && offset < current.offset) {
            return { offset: offset, element: candidate };
        }
        else {  
            return current;
        }
   }, { offset: before ? Number.POSITIVE_INFINITY : Number.NEGATIVE_INFINITY }).element; 
}

const moveTask = function(task, destList, afterTask){
    const innerList = destList.querySelector('.board-list');
    afterTask != null ? innerList.insertBefore(task, afterTask) : innerList.appendChild(task);
}

const moveDraggingToContainer = function(list, yPos) {
    const draggingTask = document.querySelector('.dragging');
    // The task before is required for updating ordering in the database
    const afterTask = getDragAdjacentElement(list, yPos);
    const beforeTask = getDragAdjacentElement(list, yPos, true);
    lastAfterTask = afterTask;
    lastBeforeTask = beforeTask;

    // Move task and store enough information to send to other clients to move the task
    moveTask(draggingTask, list, afterTask);    
};


const addTaskDragEvents = function(task) {
    task.addEventListener('dragstart', () => { 
        task.classList.add('dragging'); 
        taskStartList = task.parentElement; 
    });

    task.addEventListener('dragend', () => { 
        task.classList.remove('dragging')
        socket.emit('move_task', { 
            taskID: task.id, 
            srcListID: taskStartList.id, 
            destListID: task.parentElement.parentElement.id, 
            afterTaskID: lastAfterTask != null ? lastAfterTask.id : null, 
            beforeTaskID: lastBeforeTask != null ? lastBeforeTask.id : null,
            room: boardID
        });
        socket.emit('refresh_board_stats', { boardID: boardID } );
     });
}

tasks.forEach(task => {
    addTaskDragEvents(task);
});

lists.forEach(list => {
    list.addEventListener('dragover', e => { 
        e.preventDefault(); 
        moveDraggingToContainer(list, e.clientY);
        lastDragOverList = list;
    });
});

