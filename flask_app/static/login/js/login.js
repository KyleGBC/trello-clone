let count = 0 
let failReason = ""
let failureText = document.getElementById('login-error')

const updateFailureCount = function()
{
    if(count > 0)
    {
        failureText.textContent =  failReason + " (" + "Failed login attempts: " + count + ")"
    }
    else
    {
        failureText.textContent = ""
    }
}

const checkCredentials = function(event) {
    // prevent the form from submitting the normal way
    event.preventDefault();

    // package data in an object
    let form = new FormData(event.target, event.submitter);
    let data = Object.fromEntries(form.entries()); 
    console.log('data_d', data)

    // SEND DATA TO SERVER VIA jQuery.ajax({})
    jQuery.ajax({
        url: "/process_login",
        data: data,
        type: "POST",
        success:function(returned_data){
                returned_data = JSON.parse(returned_data);

                if(returned_data['success'] === 1)
                {
                    window.location.href = "/home";
                }
                else
                {
                    count += 1
                    failReason = returned_data['message']
                    updateFailureCount()
                }
            }
    });
}               

// Get the form the user is filling out and register an event listener for when the form is submitted
let login_form = document.getElementById('login-form')
login_form.addEventListener('submit', checkCredentials);