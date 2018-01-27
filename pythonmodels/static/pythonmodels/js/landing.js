
$(document).ready(function() {

    // Set active navigation li
    // Change path if active li is create model tab
    var path = window.location.pathname;
        if (path.match(/create/i)) {
            path = path.replace(/\d+$/, "0")
        }
    var activeTab = $("a[href='" + path + "']").parent();
    activeTab.addClass('active');

    // Hide collapsed navigation after click
    $('.nav a').click(function(){
        $('#myNavbar').collapse('hide');
    });

    var $lh = $('.landing').height();
    var $hh = $('.header').height();
    var $fh = $('footer').height();
    $('.landing').height($lh - $hh - $fh - 30);

});
