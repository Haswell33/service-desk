if (typeof jQuery === "undefined")
    console.error('jQuery not loaded')
else
    console.log('jQuery loaded')

$(document).on('click', function(event) {
    if($(event.target).is('#navbar-account svg') || $(event.target).is('#navbar-account path'))
        $('#navbar-account > ul').toggle()
    else if(!$(event.target).is('#navbar-account > ul') && $('#navbar-account > ul').is(':visible'))
        $('#navbar-account > ul').hide()
})

setTimeout(function(){
    $('.errornote').fadeOut()
    $('.messagelist').fadeOut()
}, 5000);

function bootstrapFilestyle(){
    $(":file").filestyle()
    console.log('boostrap-filestyle loaded')
}

function themeColor(userIsAuth, userIsAdmin, userTenantType){
    if (userIsAuth && userIsAdmin){
      $(':root').css({
        '--theme': '#6554C0', //purple
        '--theme-transparent': 'rgba(101, 84, 192, 0.6)'
      })
    }
    else if (userIsAuth && userTenantType === 'customer') {
      $(':root').css({
        '--theme': '#4267B2', //blue
        '--theme-transparent': 'rgba(66, 103, 178, 0.6)'
      })
    }
    else if (userIsAuth && userTenantType === 'operator') {
      $(':root').css({
        '--theme': '#36B37E', // green
        '--theme-transparent': 'rgba(54, 179, 126, 0.6)'
      })
    }
    else if (userIsAuth && userTenantType === 'developer'){
      $(':root').css({
        '--theme': '#c57117', //orange
        '--theme-transparent': 'rgba(197, 113, 23, 0.6)'
      })
    }
    else if(!userIsAuth){
      $(':root').css({
        '--theme': '#777777', //gray
        '--theme-transparent': 'rgba(119, 119, 119, 0.6)'
      })
    }
}



/*
.onChange(element.html('<option></option>').trigger('change'))
*/