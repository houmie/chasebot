$.ajaxSetup({ 
     beforeSend: function(xhr, settings) {
         function getCookie(name) {
             var cookieValue = null;
             if (document.cookie && document.cookie != '') {
                 var cookies = document.cookie.split(';');
                 for (var i = 0; i < cookies.length; i++) {
                     var cookie = jQuery.trim(cookies[i]);
                     // Does this cookie string begin with the name we want?
                 if (cookie.substring(0, name.length + 1) == (name + '=')) {
                     cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                     break;
                 }
             }
         }
         return cookieValue;
         }
         if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
             // Only send the token to relative URLs i.e. locally.
             xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
         }
     } 
});

function row_edit_cancel(){
	// This is a hidden field that contains the current sales_item_id hold for cancel edit mode
	var salesitem_id = $(this).parent().children('div.salesitem_id').text();
	var url = '/sales_item/edit/cancel/' + salesitem_id + '/';
	var row = $(this).closest('form').closest('tr').empty(); //real row containing also the submit-edit-form
	
	row.load(
		// get only the children (td) od the tr and attach them to the existing empty row.
    	url + ' td',    	
    	function () {    			              		
      		$(".row_edit").click(row_edit);
    	}
  	);  	
  	return false;
}


function row_edit() {
	// e.g. url = '/sales_item/edit/8' 
	var url = $(this).attr("href") + "/";
  
  	//e.g. get whole row to be replaced with editing fields
  	var row = $(this).closest('tr').empty();
  	//First dummy is the empty column at left
  	var dummy = $('<td>').appendTo(row);  
  	//target is positioned in the middle
  	var target = $('<td>').appendTo(row);
  	//second dummy is the empty column at right
  	var dummy = $('<td>').appendTo(row);  
  	  	
	target.load(
    	url,    	
    	function () {
    		//Once loaded make sure the submit-form will be redirected to 'row_edit_save' once submitted. Url is parameter 
      		$(target).children(".save-edit-form").submit(url, row_edit_save);
      		$(".cancel_edit_button").click(row_edit_cancel);
    	}
  	);
  	return false;
}

function row_add_save(){
	// selector starts from Add Button (this)	
	var url = "/sales_item/add/";	
	var add_button_row = $(this).closest('tr'); //add_button_row inside the form
	var row = $(add_button_row).closest('form').closest('tr'); //real row containing also the form
	
	var data = {
  			item_description: $(add_button_row).find(".item_description").val()    
  	};
  	
  	$.post(url, data, function (result) {
  		//If there are validation errors upon adding the field
  		if ($('.validation_error_ajax', result).text() == 'True') {
  			 //back_up is a hidden field holding the original state of the add-form. If there is an error we would clone the original add-form.
  			 //This is done by cloning the middle column's children (all editing fields and buttons)
  			 $('#backup_add').append($(row.children().get(1)).children().clone());
    		 row.empty();
    		 var dummy = $('<td>').appendTo(row);
    		 var target = $('<td>').appendTo(row);
  			 var dummy = $('<td>').appendTo(row);    		
      		 target.append(result);   
      		 $(".row_add_button").click(row_add_save);      		 
      		 $(target).children(".save-edit-form").submit(url, row_edit_save); 		      		
    	}
    	else {
    		//if there is no error then insert the added row before the current add-button row. (last row)
    		row.before(result);      		
      		$(".row_edit").click(row_edit);
      		
      		//if backup_add contains any children, it means that previously there was an error and the box is still red. We need to load our backup.
      		if($("#backup_add").children().length > 0)
      		{
	      		row.empty();	      		
	      		var target = $('<td>').appendTo(row);
	  			var dummy = $('<td>').appendTo(row);    		
	      		target.append($("#backup_add").children()); 
	      		row.append(target);
	      		//Clean the backup as its no longer required.
	      		$("#backup_add").empty();
      		}      		
      		else
      		{
      			//if there was no backup, it means all good. Simply empty the value as its already added.
      			$(add_button_row).find(".item_description").val('');
      		}
    	}
  	});
  	return false;
} 


$(document).ready(function () {	
	$(".row_edit").click(row_edit);
	$(".row_add_button").click(row_add_save);	
});


function row_edit_save(e) {
	// selector starts from Edit Button (this)	
	var url = e.data;
  	var row = $(this).closest('tr');
  	var data = {
  			item_description: row.find(".item_description").val()    
  	};
  	
  	$.post(url, data, function (result) {
  		//If there are validation errors upon editing the field
    	if ($('.validation_error_ajax', result).text() == 'True') {
    		//if so, then we empty the current row and load the invalid-indicating-forms in the row 
    		//and attach events to the still existing save and cancel buttons
    		row.empty();
    		var dummy = $('<td>').appendTo(row);   
    		var target = $('<td>').appendTo(row);
  			var dummy = $('<td>').appendTo(row);    		
      		target.append(result);      		
      		$(target).children(".save-edit-form").submit(url, row_edit_save); 	
      		$(".cancel_edit_button").click(row_edit_cancel);	      		
    	}
    	else {
    		//if no error, then simply add the full 'tr' html row (with delete and edit icons) behind this row and remove this row. 
    		row.before(result);
      		row.remove();
      		$(".row_edit").click(row_edit);
    	}
  	});
	return false;
}
