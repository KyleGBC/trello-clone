let chatBox = document.getElementById("chat-box");

$(document).ready(function(){
    socket.on('message', function(data) {
        console.log(data);

        if(data.user === null)
        {
            createMessageElement(data.msg, 'system-msg');
        }
        else
        {   
            createMessageElement(data.user + ": " + data.msg, 'other-msg');
        }
    });
});

const createMessageElement = function(message, className)
{
    let tag  = document.createElement("p");
    let text = document.createTextNode(message);
    
    tag.appendChild(text);
    tag.className = className

    chatBox.contentEditable = true;
    chatBox.appendChild(tag);
    chatBox.contentEditable = false;

    $('#chat-box').scrollTop($('#chat-box')[0].scrollHeight);
}


const message = document.getElementById('message-input');
message.addEventListener('keyup', function(event) {
    if (event.code === 'Enter') {
        socket.emit('message', {msg: message.value, room: boardID});
        createMessageElement(message.value, 'self-msg');
        message.value = '';
    }
});