/**
 * @author Houman
 */

function search_submit() {
    $("#modal-body").load("/contact/edit/2");
    return false;
}

$(document).ready(function() {
    $("#contactModalForm").submit(search_submit);
});

