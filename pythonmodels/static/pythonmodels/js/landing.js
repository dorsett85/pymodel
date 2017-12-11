
$(document).ready(function() {

    // Set active navigation li
    var activeTab = $("a[href='" + window.location.pathname + "']").parent();
    activeTab.addClass('active');

    // Hide collapsed navigation after click
    $('.nav a').click(function(){
        $('#myNavbar').collapse('hide');
    });

    // Submit logout form
    $('#logoutBtn').click(function() {
        document.getElementById("logout").submit();
    });

});
