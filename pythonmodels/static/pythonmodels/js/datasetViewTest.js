$(document).ready(function () {

    // Create datatables and add back opacity to show them
    $('#varNumTable, #varOtherTable').DataTable({'dom': 'ftip'});
    $('#varTables').css('opacity', 1);


});