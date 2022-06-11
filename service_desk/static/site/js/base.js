if (typeof jQuery === "undefined")
    console.error('jQuery not loaded')
else
    console.log('jQuery loaded')

$(document).ready(function(event){
    console.log('document ready')
})


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

function select2(){
    $('#id_type').select2({
        templateResult: function (option)  {
            return renderIconOption(option)
        },
        templateSelection: function (option)  {
            return renderIconOption(option)
        },
        placeholder: 'Select an issue type',
        minimumResultsForSearch: -1
    })
    $('#id_priority').select2({
        templateResult: function (option)  {
            return renderIconOption(option)
        },
        templateSelection: function (option)  {
            return renderIconOption(option)
        },
        placeholder: 'Select an priority',
        minimumResultsForSearch: -1
    })
    $('#id_assignee').select2({
        templateResult: function (option) {
            return renderIconOption(option)
        },
        templateSelection: function (option) {
            return renderIconOption(option)
            },
        placeholder: 'Select a person whose ticket will be assigned',
        allowClear: true
    })
    $('#id_reporter').select2({
        templateResult: function (option) {
            return renderIconOption(option)
        },
        templateSelection: function (option) {
            return renderIconOption(option)
            },
        placeholder: 'Select a reporter',
        allowClear: true
    })
    $('#id_labels').select2({
        placeholder: 'Categorize a ticket',
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

    $('#id_resolution').select2()
    $('#id_status').select2()

}

function renderIconOption(elem) {
    let iconElement = $(elem.element).attr('icon')
    if (iconElement !== undefined)
        return $("<span class='select-option'><img class='select-option-icon' src='/" + $(elem.element).attr('icon') + "'/><p class='select-option-text'>" +  elem.text + "</p></span>")
    else
        return elem.text
}

/*
.onChange(element.html('<option></option>').trigger('change'))
*/