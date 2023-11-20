// const wlButton = document.getElementById('watchlistButton').value
const csrftoken = getCookie('csrftoken');
// // const bdButton = document.querySelector('#bidButton')
// // const comButton = document.querySelector('#commentButton')
const url = window.location.href

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


function handleWatchlist(form) {
    console.log(form)
    let body = {
        "doit": "toggle-watcher"
    }
    const sending = JSON.stringify(body)
    const options = {
        method: 'POST',
        headers: { 'X-CSRFToken': csrftoken },
        mode: 'same-origin',
        body: sending
    }
    fetch(url, options)
        .then(response => console.log(response))
        .then(data => {
            console.log(data)
        })
    // let watch = document.querySelector('#watchlistButton').value
    // watch = !watch;
    // console.log(watch)

}



document.addEventListener('DOMContentLoaded', () => {
    document.querySelector('#watchlistForm').addEventListener("submit", e => {
        const wlButton = document.getElementById('watchlistButton').value
        //const csrftoken = getCookie('csrftoken');
        //const bdButton = document.querySelector('#bidButton').value
        //const comButton = document.querySelector('#commentButton').value
        e.preventDefault();
        console.log(wlButton)
        const formData = new FormData(document.querySelector('#watchlistForm'))
        handleWatchlist(formData);
    })


})



