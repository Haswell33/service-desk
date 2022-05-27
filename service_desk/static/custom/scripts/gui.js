if (typeof jQuery === "undefined")
    console.error('jQuery not loaded')
else
    console.log('jQuery loaded')

$(document).on('click', function(event) {
    if($(event.target).is('#navbar-account svg') || $(event.target).is('#navbar-account path'))
        $('#navbar-account > ul').toggle()
    else if(!$(event.target).is('#navbar-account > ul') && $('#navbar-account > ul').is(':visible'))
        $('#navbar-account > ul').hide()
    console.log(event.target)
    console.log($('#sidebar-content').not(':visible'))
    if ($(event.target).is('#sidebar-toggle') && !$('#sidebar-content').hasClass('hidden')){
        $('#sidebar-content').addClass('hidden')
        $(event.target).removeClass('arrow-left')
        $(event.target).addClass('arrow-right')
        /*$('#sidebar-content').css({
            'margin-left': '0px',
            'visibility': 'visible'
        })*/
    }
    else if ($(event.target).is('#sidebar-toggle') && $('#sidebar-content').hasClass('hidden')){
        $('#sidebar-content').removeClass('hidden')
        $(event.target).addClass('arrow-left')
        $(event.target).removeClass('arrow-right')
        /*$('#sidebar-content').css({
            'margin-left': '-328px',
            'visibility': 'hidden'
        })*/
    }
})



setTimeout(function(){
    $('.errornote').fadeOut()
    $('.messagelist').fadeOut()
}, 5000);

function startFuns(){
    $(":file").filestyle()
    console.log('boostrap-filestyle loaded')
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