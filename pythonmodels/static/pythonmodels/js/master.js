$(document).ready(function () {


    /**
     * Set active navigation li
     * Change path if active li is view dataset tab
     */
    var path = window.location.pathname;
    if (path.match(/dataset/i)) {
        var activeTab = $("a[href='" + path + "']").closest('li');
    } else {
        var activeTab = $("a[href='" + path + "']").parent();

    }
    activeTab.addClass('active');

    // Hide collapsed navigation after click
    $('.nav a').click(function () {
        $('#myNavbar').collapse('hide');
    });

    // Extend minimum height of master to body to at least minimum of window
    var wh = $(window).height();
    var hh = $('.header').height();
    var fh = $('footer').height();
    $('#masterBody').css({minHeight: wh - hh - fh - 20});

    // Change height on window resize
    $(window).on('resize', function () {
        $('#masterBody').css({minHeight: $(window).height() - hh - fh - 20});
    })


})