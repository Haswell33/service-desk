function generateStatic(page) {
    switch(page) {
        case 'login':
            disableStaticLinksLoginPage()
            break
        case 'create-ticket':
            break
        case 'home':
            break
        case 'filter-view':
            break
        case 'ticket-view':
            break
        default:
            console.error('not found provided page, can not load select2 fields')
    }
}

function disableStaticLinksLoginPage() {
    document.querySelector("#select2-css").setAttribute('disabled')
    document.querySelector("#select2-custom-css").setAttribute('disabled')
    document.querySelector("#tinymce-custom-css").setAttribute('disabled')
}