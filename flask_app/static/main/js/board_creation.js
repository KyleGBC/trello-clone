const createBoardButton = document.getElementById('create-board-button');
const createBoardDialog = document.getElementById('create-board-dialog');
const createBoardDialogForm = document.getElementById('create-board-dialog-form');
const createBoardError = document.getElementById('create-board-error');
const closeCreateBoardDialog = document.getElementById('close-create-board-dialog');    
const submitCreateBoardDialog = document.getElementById('submit-create-board-dialog');
const boardContainer = document.getElementById('board-container');

$(document).ready(function(){
    socket = io.connect(window.location.protocol + '//' + document.domain + ':' + location.port);
 
    // Join a room created just for this user, so we can address them directly from the server. That way users will receive create_board events only for their authorized boards
    socket.emit('join', {email: null});

    socket.on('create_board', data => {
        console.log(socket.id, 'responding to create_board')
        console.log('data:', data)
        createBoardElement(data.board_id, data.name, data.todo_tasks, data.in_progress_tasks, data.done_tasks)
    });

    socket.on('refresh_board_stats', data => {
        console.log(socket.id, 'responding to refresh_board_stats');
        console.log('data:', data);
        const boardCard = document.getElementById(data.board_id);
        boardCard.querySelector('.board-card-todo').textContent = data.todo_tasks.length;
        boardCard.querySelector('.board-card-in-progress').textContent = data.in_progress_tasks.length;
        boardCard.querySelector('.board-card-done').textContent = data.done_tasks.length;
    });
});


const createBoardElement = function(boardID, boardName, todoTasks, inProgressTasks, doneTasks) {
    // This needs to mirror and be in sync with the home.html template :( The price you pay for having a live updating main menu
    const boardCard = document.createElement('div');
    boardCard.classList.add('board-card');
    boardCard.id = boardID;

    const boardCardDelete = document.createElement('div');
    boardCardDelete.classList.add('board-card-delete');

    const boardLink = document.createElement('a');
    boardLink.classList.add('board-link');
    boardLink.href = '/board/' + boardID;

    const boardCardClickable = document.createElement('div');
    boardCardClickable.classList.add('board-card-clickable');

    const boardCardName = document.createElement('div');
    boardCardName.classList.add('board-card-name');
    boardCardName.textContent = boardName;

    const boardCardStats = document.createElement('div');
    boardCardStats.classList.add('board-card-stats');

    const todoCount = document.createElement('p');
    todoCount.classList.add('board-card-todo');
    todoCount.textContent = todoTasks ? todoTasks.length : '0';

    const inProgressCount = document.createElement('p');
    inProgressCount.classList.add('board-card-in-progress');
    inProgressCount.textContent = inProgressTasks ? inProgressTasks.length : '0';

    const doneCount = document.createElement('p');
    doneCount.classList.add('board-card-done');
    doneCount.textContent = doneTasks ? doneTasks.length : '0';

    boardCard.appendChild(boardCardDelete);
    boardCard.appendChild(boardLink);
    boardLink.appendChild(boardCardClickable);
    boardCardClickable.appendChild(boardCardName);
    boardCardClickable.appendChild(boardCardStats);
    boardCardStats.appendChild(todoCount);
    boardCardStats.appendChild(inProgressCount);
    boardCardStats.appendChild(doneCount);

    boardContainer.insertBefore(boardCard, createBoardButton);
}


const showDialog = function(event) {
    createBoardDialog.showModal();
}

const submitDialog = function(event) {
    // Don't cause a get or post request, but still use type="submit" for form validation
    // check via which button the event was submitted

    event.preventDefault();
    console.log(event.target);
    const boardName = event.target.parentElement.querySelector('#board-name-field').value;    
    const boardMembers = event.target.parentElement.querySelector('#board-members-field').value;

    socket.emit('create_board', { boardName: boardName, boardMembers: boardMembers }, function(response) {
        if(response['success'] === 1) {
            createBoardDialog.close();
            window.location.href = window.location.href = "/board/" + response['board_id'];
        }
        else {
            createBoardError.textContent = response['message'];
        }
    });

}
createBoardButton.addEventListener('click', showDialog);

submitCreateBoardDialog.addEventListener('click', submitDialog);

closeCreateBoardDialog.addEventListener('click', function(e) {
    createBoardDialog.close();
    createBoardDialogForm.reset();    
});


