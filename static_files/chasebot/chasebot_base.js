function row_delete() {
    if (confirm($('#delete_button_confirmation_msg').text())) {
    	var url = $(this).attr("href") + "/";
    	//e.g. get whole row to be removed
  		var row = $(this).closest('tr').empty();
  		
        $.post(url);
        row.remove();        
    }
    return false;
}


$(document).ready(function () {	
	$(".row_delete").click(row_delete);	
});