if (typeof jQuery === "undefined")
    console.error('jQuery not loaded')
else
    console.log('jQuery loaded')

$(document).on('click', function(event) {
    if($(event.target).is('#navbar-block_menu svg') || $(event.target).is('#navbar-block_menu path')){
        $('#navbar-block_menu > ul').toggle()
        if ($('.dialog-bg').is(":visible"))
            $('.dialog-bg').css('display', 'none')
        else
            $('.dialog-bg').css('display', 'block')
    }
    else if(!$(event.target).is('#navbar-block_menu > ul') && $('#navbar-block_menu > ul').is(':visible')){
        $('#navbar-block_menu > ul').hide()
        $('.dialog-bg').css('display', 'none')
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
}, 5000);

function bootstrapFilestyle(){
    $(":file").filestyle()
    console.log('boostrap-filestyle loaded')
}

function customCheckbox(){
    //$('input[type=checkbox]').after($('<span class="checkbox-icon"></span>'))
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


