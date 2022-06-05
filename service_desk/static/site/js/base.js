if (typeof jQuery === "undefined")
    console.error('jQuery not loaded')
else
    console.log('jQuery loaded')

$(document).on('click', function(event) {
    if($(event.target).is('#navbar-account svg') || $(event.target).is('#navbar-account path'))
        $('#navbar-account > ul').toggle()
    else if(!$(event.target).is('#navbar-account > ul') && $('#navbar-account > ul').is(':visible'))
        $('#navbar-account > ul').hide()
    if ($(event.target).is('#sidebar-toggle') && !$('#sidebar-content').hasClass('hidden')){
        $('#sidebar-content').addClass('hidden')
        $('#content-page').addClass('full-width')
        $(event.target).removeClass('arrow-left')
        $(event.target).addClass('arrow-right')

        $('#create-ticket-form').addClass('left-content-full-width')
    }
    else if ($(event.target).is('#sidebar-toggle') && $('#sidebar-content').hasClass('hidden')){
        $('#sidebar-content').removeClass('hidden')
        $('#content-page').removeClass('full-width')
        $(event.target).addClass('arrow-left')
        $(event.target).removeClass('arrow-right')

        $('#create-ticket-form').removeClass('left-content-full-width')
    }
})

setTimeout(function(){
    $('.errornote').fadeOut()
    $('.messagelist').fadeOut()
}, 5000);

function startFuns(){
    $(":file").filestyle()
    console.log('boostrap-filestyle loaded')
    select2Fields()
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

function select2Fields(){
    $('#id_type').select2({
        /*templateResult: function (idioma) {
            return $("<span><img src='https://www.free-country-flags.com/countries/" +idioma.id+ "/1/tiny/" + idioma.id + ".png'/> " + idioma.text + "</span>");
        },
        templateSelection: function (idioma) {
            return $("<span><img src='https://www.free-country-flags.com/countries/" + idioma.id + "/1/tiny/" + idioma.id + ".png'/> " + idioma.text + "</span>");
        },*/
        placeholder: 'Select an issue type',
    })
    $('#id_priority').select2({
        /*templateResult: function (idioma) {
            return $("<span><img src='https://www.free-country-flags.com/countries/" +idioma.id+ "/1/tiny/" + idioma.id + ".png'/> " + idioma.text + "</span>");
        },
        templateSelection: function (idioma) {
            return $("<span><img src='https://www.free-country-flags.com/countries/" + idioma.id + "/1/tiny/" + idioma.id + ".png'/> " + idioma.text + "</span>");
        },*/
        placeholder: 'Select a priority',
    })
    $('#id_assignee').select2({
        /*templateResult: function (idioma) {
            return $("<span><img src='https://www.free-country-flags.com/countries/" +idioma.id+ "/1/tiny/" + idioma.id + ".png'/> " + idioma.text + "</span>");
        },
        templateSelection: function (idioma) {
            return $("<span><img src='https://www.free-country-flags.com/countries/" + idioma.id + "/1/tiny/" + idioma.id + ".png'/> " + idioma.text + "</span>");
        },*/
        placeholder: 'Select a person whose ticket will be assigned',
    })
    $('#id_label').select2({
        /*templateResult: function (idioma) {
            return $("<span><img src='https://www.free-country-flags.com/countries/" +idioma.id+ "/1/tiny/" + idioma.id + ".png'/> " + idioma.text + "</span>");
        },
        templateSelection: function (idioma) {
            return $("<span><img src='https://www.free-country-flags.com/countries/" + idioma.id + "/1/tiny/" + idioma.id + ".png'/> " + idioma.text + "</span>");
        },*/
        placeholder: 'Select a category of ticket',
        multiple: true
    })
}














/*function colorElems(mainColor){
    $('.main-color-border').css('border-color', mainColor)
    $('.main-color-background-hover').hover(function(){
        $(this).css("background-color", mainColor)
    },function() {
        $(this).css("background-color", 'inherit')
    })
}*/

/*window.onload = function() {
    $(function(){
        console.log("jQuery + DOM loaded.")
    })
}*/