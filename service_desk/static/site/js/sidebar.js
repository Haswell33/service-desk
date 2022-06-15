SIDEBAR_TOGGLE = '#sidebar-block_toggle'
SIDEBAR_TRANSITION = 'sidebar-transition' // class
SIDEBAR_CONTENT = '#sidebar-block_content'
CONTENT_PAGE = '#content-page'
CREATE_TICKET_FORM = '#create-ticket-form'

$(document).ready(function(event) {
    if (localStorage.siteSidebarOpen === null || localStorage.siteSidebarOpen === undefined)
        localStorage.siteSidebarOpen = 'true'
    else if (localStorage.siteSidebarOpen === 'false'){
        $(SIDEBAR_CONTENT).removeClass(SIDEBAR_TRANSITION)
        $(CONTENT_PAGE).removeClass(SIDEBAR_TRANSITION)
        sidebar(event, 'hide')
    }
    else if (localStorage.siteSidebarOpen === 'true'){
        $(SIDEBAR_CONTENT).removeClass(SIDEBAR_TRANSITION)
        $(CONTENT_PAGE).removeClass(SIDEBAR_TRANSITION)
        sidebar(event, 'show')
    }
})

$(document).on('click', function(event) {
    if ($(event.target).is(SIDEBAR_TOGGLE)) {
        $(SIDEBAR_CONTENT).addClass(SIDEBAR_TRANSITION)
        $(CONTENT_PAGE).addClass(SIDEBAR_TRANSITION)
        if ($(event.target).is(SIDEBAR_TOGGLE) && localStorage.siteSidebarOpen === 'true')
            sidebar(event, 'hide')
        else if ($(event.target).is(SIDEBAR_TOGGLE) && localStorage.siteSidebarOpen === 'false')
            sidebar(event, 'show')
    }
})

function sidebar(event, operation) {
    switch (operation) {
        case 'show':
            localStorage.siteSidebarOpen = 'true'
            $(SIDEBAR_CONTENT).addClass('passed')
            $(CONTENT_PAGE).addClass('passed-width')
            $(SIDEBAR_TOGGLE).addClass('arrow-left')
            $(SIDEBAR_TOGGLE).removeClass('arrow-right')
            $(CREATE_TICKET_FORM).removeClass('create-ticket-form-60vw')
            break
        case 'hide':
            localStorage.siteSidebarOpen = 'false'
            $(SIDEBAR_CONTENT).removeClass('passed')
            $(CONTENT_PAGE).removeClass('passed-width')
            $(SIDEBAR_TOGGLE).removeClass('arrow-left')
            $(SIDEBAR_TOGGLE).addClass('arrow-right')
            $(CREATE_TICKET_FORM).addClass('create-ticket-form-60vw')
            break
    }
}
