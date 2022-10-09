if (typeof jQuery === "undefined")
    console.warn('jQuery not loaded')
else
    console.log('jQuery loaded')


$(document).on('click', function(event) {
    if (($(event.target).is('#navbar-block_menu svg') || $(event.target).is('#navbar-block_menu path')) && !$('#navbar-block_menu > ul').is(':visible')){
        $('#navbar-block_menu > ul').toggle()
        $('.dialog-bg').css('display', 'block')
    }
    else if (!$(event.target).is('#navbar-block_menu ul li *') && !$(event.target).is('#navbar-block_menu ul li') && $('#navbar-block_menu > ul').is(':visible')){
        $('#navbar-block_menu > ul').hide()
        $('.dialog-bg').css('display', 'none')
    }
    showDialog(event, '#edit-ticket_button', '#edit-ticket_dialog')
    showDialog(event, '#edit-assignee_button', '#edit-assignee_dialog')
    showDialog(event, '#clone-ticket_button', '#clone-ticket_dialog')
    showDialog(event, '#add-relation_button', '#add-relation_dialog')
    showDialog(event, '#add-attachment_button', '#add-attachment_dialog')
    showDialog(event, '#add-comment_button', '#add-comment_dialog')
    showDialog(event, '#edit-comment_button', '#edit-comment_dialog', true)
})

setTimeout(function(){
    $('#message-list').animate({
        right: '-20%',
        opacity: 0
    }, 800)

}, 5000);

function bootstrapFilestyle(){
    $(":file").filestyle()
    console.log('boostrap-filestyle loaded')
}

function showDialog(event, button, dialog, initAttrs) {
    let dialogBackdrop = '.dialog-bg-full'
    if($(event.target).is(button) || $(event.target).is(button + ' > *')) {
        if (initAttrs) {
            tinyMCE.activeEditor.setContent($(event.target).attr('data-value'))
            $(dialog + ' input[initial=script]').val($(event.target).attr('data-id'))
        }
        $(dialog).toggle()
        $(dialogBackdrop).css('display', 'block')
    }
    else if($(event.target).is(dialogBackdrop) && $(dialog).is(':visible')) {
        $(dialog).hide()
        $(dialogBackdrop).css('display', 'none')
    }
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

function themeColor(userIsAuth, userIsAdmin, role){
    if (userIsAuth && userIsAdmin){
      $(':root').css({
        '--theme': '#6554C0', //purple
        '--theme-hover': 'rgba(101, 84, 192, 0.6)'
      })
    }
    else if (userIsAuth && role === 'customer') {
      $(':root').css({
        '--theme': '#4267B2', //blue
        '--theme-hover': 'rgba(66, 103, 178, 0.6)'
      })
    }
    else if (userIsAuth && role === 'operator') {
      $(':root').css({
        '--theme': '#36B37E', // green
        '--theme-hover': 'rgba(54, 179, 126, 0.6)'
      })
    }
    else if (userIsAuth && role === 'developer'){
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

/*
const resizeOps = () => {
    document.documentElement.style.setProperty("--vh", window.innerHeight * 0.01 + "px");
};
resizeOps();
window.addEventListener("resize", resizeOps);
*/

/*
$(document).on('select2:select', function (event) {
    if (event.target.id === 'sidebar-block_tenant-set') {
        $.ajax({
            type: 'POST',
            url: '/tenant/update',
            data: {'tenant_id': event.params.data.id},
            beforeSend: function(xhr) {
                xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest')
            },
            success: function(result){
                location.reload()
                console.log('active tenant changed')
            }
        })
    }
});
*/



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
