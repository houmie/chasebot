// using jQuery
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
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    crossDomain: false, // obviates need for sameOrigin test
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});



function ISODateString(d){
	function pad(n){
		return n<10 ? '0'+n : n
	}
	return d.getUTCFullYear()+'-'
      + pad(d.getUTCMonth()+1)+'-'
      + pad(d.getUTCDate())+'T'
      + pad(d.getUTCHours())+':'
      + pad(d.getUTCMinutes())+':'
      + pad(d.getUTCSeconds())+'Z'
}


function convertDateTimeToUTC(date) { 
	return new Date(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate(), date.getUTCHours(), date.getUTCMinutes(), date.getUTCSeconds()); 
	}
	
function convertDateToUTC(date) { 
	return new Date(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate()); 
	}

if (!String.prototype.trim) {
   //code for trim
   String.prototype.trim=function(){
		return this.replace(/^\s+|\s+$/g, '');
	};
}



function row_delete_ajax(event) {
    event.preventDefault();
    if (confirm($('#delete_button_confirmation').text())) {
    	var url = $(this).attr("href") + "/";
    	  		
        $.post(url, function(result){
        	$('#search_result').empty();
        	$('#search_result').append(result);
        	rebind();
        });                
    }    	
}


function filter_rows(event){
	event.preventDefault();
	var url = window.location.pathname;		
	
	//'?' found means dirty url		
	if(url.indexOf('?') != -1) {
		//Make Url clean (copy bit before ?)
		url = url.substring(url.indexOf('?'));
	}
	// With ajax as first keywork we can check against in views.py and refresh the list if all filters are cleared but the request came by ajax
	url = url + '?ajax' 
	 
	//Check each input box for values and apply keyword search 
	$('.filter_button').parent().children('input').each(function(i, v){			
		//id_last_name -> last_name
		var keyword = $(v).attr('id').substring(3);
		
		//Only if it contains any value in the field, attach it to the url GET, otherwise its pointless
		var value = $(v).val();		
		if(value != ''){
			// if($(v).attr('type') == 'date'){
			// }			
			
			//If multiple parameters are passed seperated by commas...
			if(value.indexOf(',') != -1){				
				values = value.split(',');
				$(values).each(function(i, v){
					if(v.trim() != ''){
						//Put each paramater in its own keyword .e.g. ?ajax&sales_item=t3&sales_item=t1
						url = url + '&' + keyword + '=' + v.trim();
					}
				});
			}
			//If single paramaters are passed in...
			else{
				url = url + '&' + keyword + '=' + value;				
			}						
		}				 		
	})
	//Even if no filter are set, still the query to server is required to get all list and undo filters.	
	$('#search_result').load(url, function(){		
		rebind();
	});	
}

function paginator_navigate(event) {	
	event.preventDefault();	
	var url = $(this).attr("href");
	//e.g. get whole row to be removed	
	//var row = $('#search_result').empty();
	
	$('#search_result').load(url, function(){		
		rebind();	
	});		
}

function row_edit_cancel_ajax(event){
	event.preventDefault();
	// This is a hidden field that contains the current sales_item_id hold for cancel edit mode
	var salesitem_id = $(this).parent().children('div.salesitem_id').text();
	var url = '/sales_item/edit/cancel/' + salesitem_id + '/';
	var row = $(this).closest('form').closest('tr').empty(); //real row containing also the submit-edit-form
	
	row.load(
		// get only the children (td) od the tr and attach them to the existing empty row.
    	url + ' td',    	
    	function () {    			              		
      		rebind();
    	}
  	);
}


function row_edit_ajax(event) {
	event.preventDefault();
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
    		//Once loaded make sure the submit-form will be redirected to 'row_edit_save_ajax' once submitted. Url is parameter 
      		$(target).children(".save-edit-form").submit(url, row_edit_save_ajax);
      		$(".cancel_edit_button").click(row_edit_cancel_ajax);
    	}
  	);  	
}

function row_add_save_ajax(event){
	event.preventDefault();
	// selector starts from Add Button (this)	
	var url = "/sales_item/add/";	
	var add_button_row = $(this).closest('tr'); //add_button_row inside the form
	var row = $(add_button_row).closest('form').closest('tr'); //real row containing also the form
	
	var data = {
  			item_name: $(add_button_row).find(".item_name").val()    
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
      		 $(".row_add_button_ajax").click(row_add_save_ajax);      		 
      		 $(target).children(".save-edit-form").submit(url, row_edit_save_ajax); 		      		
    	}
    	else {
    		//if there is no error then insert the added row before the current add-button row. (last row)    		
    		$('#search_result').empty();
    		$('#search_result').append(result);    		      		
      		rebind();
      		
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
      			$(add_button_row).find(".item_name").val('');
      		}
    	}
  	});  	
} 


function row_edit_save_ajax(event) {
	event.preventDefault();
	// selector starts from Edit Button (this)	
	var url = event.data;
  	var row = $(this).closest('tr');
  	var data = {
  			item_name: row.find(".item_name").val()    
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
      		$(target).children(".save-edit-form").submit(url, row_edit_save_ajax); 	
      		$(".cancel_edit_button").click(row_edit_cancel_ajax);	      		
    	}
    	else {
    		//if no error, then simply add the full 'tr' html row (with delete and edit icons) behind this row and remove this row. 
    		row.before(result);
      		row.remove();      		  
      		rebind();	
    	}
  	});	
}


function rebind(){
	$(".row_delete_ajax").click(row_delete_ajax);	
	$(".filter_button").click(filter_rows);	
	$(".paginator_nav_links").click(paginator_navigate);
	$(".row_edit_ajax").click(row_edit_ajax);
	$(".row_add_button_ajax").click(row_add_save_ajax);	
	$(".form-filter-ajax").submit(filter_rows);
}

$(document).ready(function () {	
	rebind();	
});


