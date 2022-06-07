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
        $('#content').addClass('full-width')
        $(event.target).removeClass('arrow-left')
        $(event.target).addClass('arrow-right')

        $('#create-ticket-form').addClass('left-content-full-width')
    }
    else if ($(event.target).is('#sidebar-toggle') && $('#sidebar-content').hasClass('hidden')){
        $('#sidebar-content').removeClass('hidden')
        $('#content').removeClass('full-width')
        $(event.target).addClass('arrow-left')
        $(event.target).removeClass('arrow-right')

        $('#create-ticket-form').removeClass('left-content-full-width')
    }
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

function select2(){
    $('#id_type').select2({
        templateResult: function (option) {
            return $("<span class='select-option'><img class='select-option-icon' src='../" + $(option.element).attr('icon') + "'/><p class='select-option-text'>" +  option.text + "</p></span>")
        },
        templateSelection: function (option) {
            return $("<span class='select-option'><img class='select-option-icon' src='../" + $(option.element).attr('icon') + "'/><p class='select-option-text'>" +  option.text + "</p></span>")
        },
        placeholder: 'Select an issue type',
        minimumResultsForSearch: -1
    })
    $('#id_priority').select2({
        templateResult: function (option) {
            return $("<span class='select-option'><img class='select-option-icon' src='../" + $(option.element).attr('icon') + "'/><p class='select-option-text'>" +  option.text + "</p></span>")
        },
        templateSelection: function (option) {
            return $("<span class='select-option'><img class='select-option-icon' src='../" + $(option.element).attr('icon') + "'/><p class='select-option-text'>" +  option.text + "</p></span>")
        },
        placeholder: 'Select an priority',
        minimumResultsForSearch: -1
    })
    $('#id_assignee').select2({
        templateResult: function (option) {
            return $("<span class='select-option'><img class='select-option-icon' src='../" + $(option.element).attr('icon') + "'/><p class='select-option-text'>" +  option.text + "</p></span>")
        },
        templateSelection: function (option) {
            return $("<span class='select-option'><img class='select-option-icon' src='../" + $(option.element).attr('icon') + "'/><p class='select-option-text'>" +  option.text + "</p></span>")
        },
        placeholder: 'Select a person whose ticket will be assigned',
    })
    $('#id_label').select2({
        placeholder: 'Categorize a ticket',
        minimumResultsForSearch: -1,
        multiple: true
    })
    $('#id_groups').select2({
        multiple: true,
        width: '590px'
    })
    $('#id_user_permissions').select2({
        multiple: true,
        width: '590px',
    })
    $('#id_permissions').select2({
        multiple: true,
        width: '590px',
    })
}



$('.select').on('select2:open', function () {
    $('.select__dropdown .select2-results__options').mCustomScrollbar('destroy');
    $('.select__dropdown .select2-results__options').mCustomScrollbar('update');
    setTimeout(function() {
        $('.select__dropdown .select2-results__options').mCustomScrollbar({
            axis: 'y',
            scrollbarPosition: 'inside',
            advanced:{
                updateOnContentResize: true
            },
            live: true
        });
    }, 0);
});










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