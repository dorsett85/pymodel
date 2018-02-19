$(document).ready(function () {


    /**
     * Create datatables and add back opacity to show them
     * Remove spinner once datables are loaded
     */
    $('#varNumTable, #varOtherTable').DataTable({'dom': 'ftip'});
    $('#varTables').css('opacity', 1);
    $('.varTableSpinner').hide();


    /**
     * MathJax inline math setup
     */
    MathJax.Hub.Config({
        tex2jax: {inlineMath: [['$', '$']]}
    });


});