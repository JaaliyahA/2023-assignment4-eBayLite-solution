

// const wlButton = document.getElementById('watchlistButton').value
const csrftoken = getCookie('csrftoken');
// // const bdButton = document.querySelector('#bidButton')
// // const comButton = document.querySelector('#commentButton')


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


function handleWatchlist(id, url) {
    let body = {
        "doit": "toggle-watcher"
    }
    const sending = JSON.stringify(body)
    //console.log(sending)
    const options = {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json'
        },
        mode: 'same-origin',
        body: JSON.stringify(body)
    }
    console.log(options.body)
    fetch(url, options)
        .then(response => response.json())
        .then(data => {
            console.log(data)
            if (data['watching']) {
                document.querySelector(`[value="${id}"]`).innerHTML = `<i class="bi bi-heart-fill"></i>`
            } else {
                document.querySelector(`[value="${id}"]`).innerHTML = `<i class="bi bi-heart"></i>`
            }
        })
    // let watch = document.querySelector('#watchlistButton').value
    // watch = !watch;
    // console.log(watch)

}
function handleComments(id, form) {
    const url = window.location.href
    let formInp = {}

    for (const [key, value] of form) {
        console.log(`${key}: ${value}`);
        formInp[key] = value
    }
    let body = {
        "doit": "add-comment",
        'form': formInp
    }
    const options = {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json'
        },
        mode: 'same-origin',
        body: JSON.stringify(body)
    }
    console.log(options.body)
    fetch(url, options)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok')
            }
            return response.json()
        })
        .then(data => {
            console.log(data)
            if (data['success']) {
                document.querySelector('#commForm').classList.add("d-none")
                document.getElementById('commentButton').classList.remove("d-none")
            } else {
                alert('yet another error')
            }

        })
        .catch(error => {
            console.error('Problem with Fetch')
        })
}




document.addEventListener('DOMContentLoaded', () => {
    const wlButton = document.querySelectorAll('#watchlistButton')
    const listingWatchlist = document.querySelector('#watchlistForm')

    if (listingWatchlist) {
        const watchlist = document.querySelector('#watchlistButton')
        const comment = document.getElementById('commentButton')

        if (wlButton.length != 0 && !listingWatchlist) {
            wlButton.forEach(link => link.addEventListener('click', e => {
                let id = link.value
                let url = `listing/${id}`
                handleWatchlist(id, url);
            }))

        }

        if (watchlist && comment) {
            watchlist.addEventListener('click', e => {
                e.preventDefault();
                const url = window.location.href
                handleWatchlist(watchlist.value, url)
            })

            comment.addEventListener('click', e => {
                e.preventDefault();
                document.querySelector('#commForm').classList.remove("d-none")
                comment.classList.add("d-none")
                let id = comment.value
                const textarea = document.querySelector('#id_comment')

                if (textarea) {
                    document.getElementById('addCommForm').addEventListener('submit', e => {
                        e.preventDefault();
                        console.log("do we get here")
                        const form = document.getElementById("addCommForm")
                        console.log(form)
                        const f = new FormData(form)
                        console.log(f)

                        handleComments(id, f)
                    })
                }
            })
        }
    }
})



