if (typeof jQuery === "undefined")
    console.error('jQuery not loaded')
else
    console.log('jQuery loaded')


$(document).on('click', function(event) {
    if($(event.target).is('#navbar-block_menu svg') || $(event.target).is('#navbar-block_menu path')){
        $('#navbar-block_menu > ul').toggle()
        dialogBg()
    }
    else if(!$(event.target).is('#navbar-block_menu > ul') && $('#navbar-block_menu > ul').is(':visible')){
        $('#navbar-block_menu > ul').hide()
        dialogBg()
    }

    if($(event.target).is('#button_ticket-assignee')) {
        $('#navbar-block_assignee-dialog').toggle()
        dialogBg()
    }
    else if(!$(event.target).is('#navbar-block_assignee-dialog') && !$(event.target).is('#navbar-block_assignee-dialog *') && !$(event.target).is('.select2-dropdown *') && $('#navbar-block_assignee-dialog').is(':visible')) {
        $('#navbar-block_assignee-dialog').hide()
        dialogBg()
    }

    if($(event.target).is('#button_ticket-attachment-add') || $(event.target).is('#button_ticket-attachment-add svg')) {
        $('#navbar-block_attachment-add-dialog').toggle()
        dialogBg('.attachment-dialog-bg')
    }
    else if(!$(event.target).is('#navbar-block_attachment-add-dialog') && !$(event.target).is('#navbar-block_attachment-add-dialog *') && $('#navbar-block_attachment-add-dialog').is(':visible')) {
        $('#navbar-block_attachment-add-dialog').hide()
        dialogBg('.attachment-dialog-bg')
    }

    if($(event.target).is('#button_ticket-relation-add') || $(event.target).is('#button_ticket-relation-add svg')) {
        $('#navbar-block_relation-add-dialog').toggle()
        dialogBg('.relation-dialog-bg')
    }
    else if(!$(event.target).is('#navbar-block_relation-add-dialog') && !$(event.target).is('#navbar-block_relation-add-dialog *') && $('#navbar-block_relation-add-dialog').is(':visible')) {
        $('#navbar-block_relation-add-dialog').hide()
        dialogBg('.relation-dialog-bg')
    }

    if($(event.target).is('#button_ticket-edit')) {
        $('#navbar-block_edit-dialog').toggle()
        dialogBg()
    }
    else if(!$(event.target).is('#navbar-block_edit-dialog') && !$(event.target).is('#navbar-block_edit-dialog *') && !$(event.target).is('.select2-dropdown *') && !$(event.target).is('.select2-selection__choice__remove') && !$(event.target).is('.tox-dialog-wrap *') && $('#navbar-block_edit-dialog').is(':visible')) {
        $('#navbar-block_edit-dialog').hide()
        dialogBg()
    }
    if($(event.target).is('#add-comment_button')) {
        $('#add-comment_dialog').toggle()
        dialogBg()
    }
    else if(!$(event.target).is('#add-comment_dialog') && !$(event.target).is('#add-comment_dialog *') && !$(event.target).is('.select2-dropdown *') && !$(event.target).is('.select2-selection__choice__remove') && !$(event.target).is('.tox-dialog-wrap *') && $('#add-comment_dialog').is(':visible')) {
        $('#add-comment_dialog').hide()
        dialogBg()
    }
   // else if($(event.target).is('#content-header #icon-hint svg') || $(event.target).is('#navbar-account path')){
//
   // }
   // else if(!$(event.target).is('#content-header #icon-hint .tooltip') && $('#content-header #icon-hint .tooltip').is(':visible')){
//
   // }
})

setTimeout(function(){
    $('.errornote').fadeOut()
    $('.messagelist').fadeOut()
    $('.message').fadeOut()
}, 5000);

function bootstrapFilestyle(){
    $(":file").filestyle()
    console.log('boostrap-filestyle loaded')
}

function dialogBg(dialogClass) {
    let dialogElem
    if (dialogClass)
        dialogElem= dialogClass
    else
        dialogElem = '.dialog-bg'
    if ($(dialogElem).is(":visible"))
        $(dialogElem).css('display', 'none')
    else
        $(dialogElem).css('display', 'block')
}

function sortTable(newOrderValue, currOrderValue){
    let url = window.location.href
    let paramValue
    if (newOrderValue === currOrderValue)
        paramValue = '-' + newOrderValue // desc
    else
        paramValue = newOrderValue // asc
    url = replaceUrlParam(url, 'ordering', paramValue)
    window.location.href = url
}

function replaceUrlParam(url, paramName, paramValue) {
    if (paramValue == null)
        paramValue = ''
    let pattern = new RegExp('\\b('+paramName+'=).*?(&|#|$)')
    if (url.search(pattern) >= 0)
        return url.replace(pattern, '$1' + paramValue + '$2')
    url = url.replace(/[?#]$/, '')
    return url + (url.indexOf('?')>0 ? '&' : '?') + paramName + '=' + paramValue
}

function themeColor(userIsAuth, userIsAdmin, userType){
    if (userIsAuth && userIsAdmin){
      $(':root').css({
        '--theme': '#6554C0', //purple
        '--theme-hover': 'rgba(101, 84, 192, 0.6)'
      })
    }
    else if (userIsAuth && userType === 'customer') {
      $(':root').css({
        '--theme': '#4267B2', //blue
        '--theme-hover': 'rgba(66, 103, 178, 0.6)'
      })
    }
    else if (userIsAuth && userType === 'operator') {
      $(':root').css({
        '--theme': '#36B37E', // green
        '--theme-hover': 'rgba(54, 179, 126, 0.6)'
      })
    }
    else if (userIsAuth && userType === 'developer'){
      $(':root').css({
        '--theme': '#c57117', //orange
        '--theme-hover': 'rgba(197, 113, 23, 0.6)'
      })
    }
    else if(!userIsAuth){
      $(':root').css({
        '--theme': '#777777', //gray
        '--theme-hover': 'rgba(119, 119, 119, 0.6)'
      })
    }
}


/*function sortFilterView(data){
    console.log(data)
    $.ajax({
            type: 'GET',
            url: '/ticket/filter',
            data: {
                'ordering': data
            },
            beforeSend: function(xhr) {
                xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest')
            },
            success: function(result){
                console.log(result)
                console.log('sorted')
            }
        })
}

*/
