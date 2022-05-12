if (typeof jQuery === "undefined")
    console.error('jQuery not loaded')
else
    console.log('jQuery loaded')

$(document).on('click', function(event) {
    if($(event.target).is('#navbar-account svg') || $(event.target).is('#navbar-account path'))
        $('#navbar-account > ul').toggle()
    else if(!$(event.target).is('#navbar-account > ul') && ($('#navbar-account > ul').is(':visible')))
        $('#navbar-account > ul').hide()
})

function colorElems(mainColor){
    $('.main-color-border').css('border-color', mainColor)
    $('.main-color-background-hover').hover(function(){
        $(this).css("background-color", mainColor)
    },function() {
        $(this).css("background-color", 'inherit')
    })
}

/*window.onload = function() {
    $(function(){
        console.log("jQuery + DOM loaded.")
    })
}*/