if (typeof jQuery === "undefined")
    console.error('jQuery not loaded')
else
    console.log('jQuery loaded')

$(document).ready(function () {
    console.log('document ready')
})

$(document).on('click', function(event) {
    if($(event.target).is('#navbar-account > img')) {
        $('#navbar-account > ul').toggle();
    }
    else if(!$(event.target).is('#navbar-account > ul') && ($('#navbar-account > ul').is(':visible'))) {
        $('#navbar-account > ul').hide();
    }
})

/*window.onload = function() {
    $(function(){
        console.log("jQuery + DOM loaded.")
    })
}*/