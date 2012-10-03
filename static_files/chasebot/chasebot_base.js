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
};
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
};
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
};


function convertDateTimeToUTC(date) { 
	return new Date(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate(), date.getUTCHours(), date.getUTCMinutes(), date.getUTCSeconds()); 
};
	
function convertDateToUTC(date) { 
	return new Date(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate()); 
};

if (!String.prototype.trim) {
   //code for trim
   String.prototype.trim=function(){
		return this.replace(/^\s+|\s+$/g, '');
	};
};


function row_delete_ajax(event) {
    event.preventDefault();
    if (confirm($('#delete_button_confirmation').text())) {
    	var url = $(this).attr("href") + "/";
    	  		
        $.post(url, function(result){
        	$('#search_result').empty();
        	$('#search_result').append(result);
        	rebind_edit_delete($('#search_result'));
        	rebind_paginator($('#search_result'));
        	rebind_add();        	
        });                
    }    	
};


function filter_rows(event){
	event.preventDefault();
	var url = '';		
	
	//If the page containing the paginator is a modal, then we need to know its type, to modify the url accordingly 
	//Otherwise the url would point to the page containing the modal. 
	var modal = $('#modal_type').text();
	if(modal != ''){
		url = "/" + modal + "/";
	}
	else{
		url = window.location.pathname;
	}
	
	// With ajax as first keywork we can check against in views.py and refresh the list if all filters are cleared but the request came by ajax
	url = url + '?ajax' 
	 
	//Check each input box for values and apply keyword search 
	$('.form-filter-ajax').find('input').each(function(i, v){			
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
				url = url + '&' + keyword + '=' + encodeURIComponent(value);				
			}						
		}				 		
	})
	//Even if no filter are set, still the query to server is required to get all list and undo filters.	
	$('#search_result').load(url, function(){		
		rebind_edit_delete($('#search_result'));
		rebind_paginator($('#search_result'));
		rebind_add();
	});	
};

function paginator_navigate(event) {	
	event.preventDefault();	
	var url = '';
	
	//If the page containing the paginator is a modal, then we need to know its type, to modify the url accordingly 
	//Otherwise the url would point to the page containing the modal. 
	var modal = $('#modal_type').text();
	if(modal != ''){
		url = "/" + modal + "/" + $(this).attr("href");
	}
	else{
		url = $(this).attr("href");
	}
		
	$('#search_result').load(url, function(result){		
		rebind_edit_delete($('#search_result'));
		rebind_paginator($('#search_result'));
		rebind_add();		
	});		
};

function row_edit_cancel_ajax(event){
	event.preventDefault();
	// This is a hidden field that contains the current sales_item_id hold for cancel edit mode
	var salesitem_id = $(this).parent().children('div.salesitem_id').text();
	var url = '/sales_item/edit/cancel/' + salesitem_id + '/';
	var row = $(this).closest('form').closest('tr'); //real row containing also the submit-edit-form
	
	row.load(
		// get only the children (td) of the tr and attach them to the existing empty row.
    	url + ' td',    	
    	function () {    			              		
      		rebind_edit_delete($(row));
    	}
  	);
};


function row_edit_ajax(event) {
	event.preventDefault();
	// e.g. url = '/sales_item/edit/8' 
	var url = $(this).attr("href") + "/";
  
  	//e.g. get whole row to be replaced with editing fields
  	var row = $(this).closest('tr');
  	
	row.load(
    	url,    	
    	function () {
    		//Once loaded make sure the submit-form will be redirected to 'row_edit_save_ajax' once submitted. Url is parameter 
      		$(row).find(".save-edit-form").submit(url, row_edit_save_ajax);
      		$(row).find(".cancel_edit_button").click(row_edit_cancel_ajax);
    	}
  	);  	
};

function row_add_save_ajax(event){
	event.preventDefault();
	// selector starts from Add Button (this)	
	var url = "/sales_item/add/";	
	//var add_button_row = $(this).closest('tr'); //add_button_row inside the form
	var row = $(this).closest('tr'); //real row containing also the form
	
	var data = {
  			item_name: $(this).find("#id_item_name").val()    
  	};
  	
  	$.post(url, data, function (result) {
  		//If there are validation errors upon adding the field
  		if ($('.validation_error_ajax', result).text() == 'True') {  			 
    		 row.empty();    		 
      		 row.append(result);      		       		 
      		 target.find("#save-add-form").submit(url, row_add_save_ajax);      		       		
    	}
    	else {
    		//if there is no error then insert the added row before the current add-button row. (last row)    		
    		$('#search_result').empty();
    		$('#search_result').append(result);    		      		
      		rebind_edit_delete($('#search_result'));
      		rebind_paginator($('#search_result'));
      		$("#save-add-form").submit(url, row_add_save_ajax);   
      		
      		$(".item_name").val('');
      		
    	}
  	});  	
};


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
      		row.append(result);      		
      		$(row).find(".save-edit-form").submit(url, row_edit_save_ajax); 	
      		$(row).find(".cancel_edit_button").click(row_edit_cancel_ajax);	      		
    	}
    	else {
    		//if no error, then simply add the full 'tr' html row (with delete and edit icons) behind this row and remove this row. 
    		var row_before = $(result).insertBefore(row);  		
      		row.remove();      		  
      		rebind_edit_delete($(row_before));	
    	}
  	});	
};

//This function is kept very generic !
//the first two are internal parameters to make typeahead work.
//fieldname is the field to filter against.
//contact_id is the optional id that some querysets might need as prerequisite.
function autocomplete(query, process, path, fieldname, contact_id){
	var url = '';
	//If contact_id is passed in then we have a different url path to pass in the contact_id
	if(contact_id == ''){
		url = '/autocomplete/' + path + '/';
	}
	else{
		url = '/autocomplete/' + path + '/' + contact_id + '/';
	}
	
	//Pass in the query (typed keywords) and the fieldname we are searching against 
	$.ajax({
     	  type: 'GET',
		  url: url,
		  data: { query: query, fieldname: fieldname },		  
		  contentType: "application/json; charset=utf-8",
		  dataType: 'json',
		  success: function (data) {
		  	return process(data);
		  }		  
		});
}

//The average typeahead function passes in two parameters. First one is the category (which defines the related queryset) 
//and the second is the actual field to filter.
function typeahead_sales_items(query, process){
	autocomplete(query, process, 'sales_items', 'item_name', '')
};

function typeahead_contacts_last_name(query, process){
	autocomplete(query, process, 'contacts', 'last_name', '')
};

function typeahead_contacts_first_name(query, process){
	autocomplete(query, process, 'contacts', 'first_name', '')
};

function typeahead_contacts_company(query, process){
	autocomplete(query, process, 'contacts', 'company_name', '')
};

function typeahead_contacts_email(query, process){
	autocomplete(query, process, 'contacts', 'email', '')
};

//This method passes in three parameters, the last one is the contact_id. Since all calls must belong to a contact.
function typeahead_conversation_subject(query, process){
	autocomplete(query, process, 'conversations', 'subject', $('#contact_id').text())
};

function typeahead_deals_deal_name(query, process){
	autocomplete(query, process, 'deals', 'deal_name', '')
};

function typeahead_deals_sales_item(query, process){
	autocomplete(query, process, 'deals', 'sales_item', '')
};

function typeahead_deals_price(query, process){
	autocomplete(query, process, 'deals', 'price', '')
};

function typeahead_deals_sales_term(query, process){
	autocomplete(query, process, 'deals', 'sales_term', '')
};

function typeahead_deals_quantity(query, process){
	autocomplete(query, process, 'deals', 'quantity', '')
};


function rebind_paginator(parent){
	$(parent).find(".paginator_nav_links").click(paginator_navigate);
}


function rebind_edit_delete(parent){	
	$(parent).find(".row_delete_ajax").click(row_delete_ajax);	
	$(parent).find(".row_edit_ajax").click(row_edit_ajax);	
}


function rebind_add(){
	$('#save-add-form').submit(row_add_save_ajax);	
			
};


function clear_filter(event){
	event.preventDefault();
	$(this).siblings().children('input').val('');
	$(this).closest('form').submit();
	
}



// These bindings are for all existing filters. Since they don't get refreshed like the lists, they don't need to be part of bind()
function rebind_filters(parent){
	$(parent).find(".form-filter-ajax").submit(filter_rows);			
	$(parent).find(".typeahead_sales_items").typeahead({ source: typeahead_sales_items });
	$(parent).find(".typeahead_contacts_last_name").typeahead({ source: typeahead_contacts_last_name });
	$(parent).find(".typeahead_contacts_first_name").typeahead({ source: typeahead_contacts_first_name });
	$(parent).find(".typeahead_contacts_company").typeahead({ source: typeahead_contacts_company });
	$(parent).find(".typeahead_contacts_email").typeahead({ source: typeahead_contacts_email });
	$(parent).find(".typeahead_conversation_subject").typeahead({ source: typeahead_conversation_subject });
	$(parent).find(".typeahead_deals_deal_name").typeahead({ source: typeahead_deals_deal_name });
	$(parent).find(".typeahead_deals_sales_item").typeahead({ source: typeahead_deals_sales_item });
	$(parent).find(".typeahead_deals_price").typeahead({ source: typeahead_deals_price });
	$(parent).find(".typeahead_deals_sales_term").typeahead({ source: typeahead_deals_sales_term });
	$(parent).find(".typeahead_deals_quantity").typeahead({ source: typeahead_deals_quantity });	
	$(parent).find(".filter-close").click(clear_filter);
};

function modal_closing(event){
	event.preventDefault();
	$('#salesitems_modal').empty();
}

function open_modal(event){
	event.preventDefault();
	var url = $(this).attr("href") + "/";
	//var map = new Object();
	//map['modal'] = true;
	var data = 'modal';	
	$("#salesitems_modal").load(url, data, function() { 
            $(this).modal('show'); // display the modal on url load
            rebind_add();
            rebind_edit_delete($(this));
            rebind_paginator($(this));
            rebind_filters($(this));
            
         });            
}

function timezone_dropdown(event){
	event.preventDefault();
	$('#timezone_form').submit();			
}

function show_timezone_help(event){
	event.preventDefault();	
	$('#timezone_dropdown').popover('toggle');
	isVisible = true;	
}

var isVisible = false;
var clickedAway = false;


function invite_colleague(event){
	event.preventDefault();
	$(this).button('loading');
	//$(this).button('reset')
	$('#form_invite').submit();
	
}


$(document).ready(function (){	 	
	rebind_add();
	rebind_edit_delete($('#search_result'));
	rebind_paginator($('#search_result'));
	rebind_filters($('body'));
	$(".modal_link").click(open_modal)
	$('#salesitems_modal').on('hidden', modal_closing);
	$('#timezone_dropdown').change(timezone_dropdown);	
	$('.timezone_help').click(show_timezone_help);
	$('.date_picker').datepicker({    		
    		format: $('#locale').text(),
    		autoclose: 'True'
		});
	$('#invite-button').click(invite_colleague)
	
// $(document).click(function(e){
  // if(isVisible & clickedAway){
    // $('#timezone_dropdown').popover('hide');
    // isVisible = clickedAway = false
  // }
  // else {
    // clickedAway = true
  // }
// });



    

});


