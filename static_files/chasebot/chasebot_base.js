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
    var target = $(event.data.target);
    if (confirm(gettext('Are you sure you want to delete this row?'))) {
    	var url = $(this).attr("href");
    	  		
        $.post(url, function(result){
        	$(target).empty();
        	$(target).append(result);
        	rebind_edit_delete($(target));
        	rebind_paginator($(target));
        	rebind_task_edit_delete($(target));
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
	if($.chasebot.MODAL_OPEN){
		url = "/" + modal + "/";
	}
	else{
		url = window.location.pathname;
	}
	
	// With ajax as first keywork we can check against in views.py and refresh the list if all filters are cleared but the request came by ajax
	url = url + '?ajax';
	 
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
	var target_pane = $(event.data.target_pane);
	//If the page containing the paginator is a modal, then we need to know its type, to modify the url accordingly 
	//Otherwise the url would point to the page containing the modal. 
	var modal = $('#modal_type').text();
	if($.chasebot.MODAL_OPEN){
		url = "/" + modal + "/" + $(this).attr("href");
	}
	else{
		url = $(this).attr("href");
	}
		
	$(target_pane).load(url, function(result){		
		rebind_edit_delete($(target_pane));
		rebind_task_edit_delete($(target_pane));
		rebind_paginator($(target_pane));		
		rebind_add();	
		rebind_ratings($(target_pane));	
	});		
};

function row_edit_cancel_ajax(event){
	event.preventDefault();
	// This is a hidden field that contains the current sales_item_id hold for cancel edit mode	
	var url = $(this).attr("href") + "/";
	var row = $(this).closest('form').closest('tr'); //real row containing also the submit-edit-form	
	row.load(
		// get only the children (td) of the tr and attach them to the existing empty row.
    	url + ' td',    	
    	function () {    			              		
      		rebind_edit_delete($(row));
    	}
  	);
};

function reload_edit_save_cancel_buttons(row, url){
	$(row).find("#save_edit_form").submit(url, row_edit_save_ajax);
	$(row).find("#save_edit_button").click(function(){
		$(row).find("#save_edit_form").submit();
	});
	$(row).find("#cancel_edit_button").click(row_edit_cancel_ajax);
	rebind_add_deals();
	datepicker_reload($(row));
}


function row_edit_ajax(event) {
	event.preventDefault();
	// e.g. url = '/sales_item/edit/8' 
	var url = $(this).attr("href") + "/";
  
  	//e.g. get whole row to be replaced with editing fields
  	var row = $(this).closest('tr');  	
	row.load(
    	url,    	
    	function (result) {
    		//Once loaded make sure the submit-form will be redirected to 'row_edit_save_ajax' once submitted. Url is parameter 
      		reload_edit_save_cancel_buttons($(row), url);
    	}
  	);  	
};

function row_add_save_ajax(event){
	event.preventDefault();
	// selector starts from Add Button (this)	
	var url = $('#save_add_form').attr('action');		
	var row = $(this).closest('tr'); //real row containing also the form	
	var data = $("#save_add_form").serialize();
  	
  	$.post(url, data, function (result) {
  		//If there are validation errors upon adding the field
  		if ($('#validation_error_ajax', result).text() == 'True') {  			 
    		 row.empty();    		 
      		 row.append(result);      		       		 
      		 row.find("#save_add_form").submit(url, row_add_save_ajax);      		       		
    	}
    	else {
    		//if there is no error then insert the added row before the current add-button row. (last row)    		
    		$('#search_result').empty();
    		$('#search_result').append(result);    		      		
      		rebind_edit_delete($('#search_result'));
      		rebind_paginator($('#search_result'));
      		$("#save_add_form").submit(url, row_add_save_ajax);      		
      		$(".item_name").val('');      		
    	}
  	});  	
};


function row_edit_save_ajax(event) {
	event.preventDefault();
	// selector starts from Edit Button (this)	
	var url = event.data;
  	var row = $(this).closest('tr');  	
  	var data = $(this).closest('#save_edit_form').serialize();
  	
  	$.post(url, data, function (result) {
  		//If there are validation errors upon editing the field
    	if ($('#validation_error_ajax', result).text() == 'True') {
    		//if so, then we empty the current row and load the invalid-indicating-forms in the row 
    		//and attach events to the still existing save and cancel buttons
    		row.empty();    		    		
      		row.append(result);      			
      		reload_edit_save_cancel_buttons($(row), url);     		
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
	$(parent).find(".paginator_nav_links").click({target_pane: parent}, paginator_navigate);
}


function rebind_edit_delete(parent){	
	$(parent).find(".row_delete_ajax").off('click').on('click', {target: parent}, row_delete_ajax);	
	$(parent).find(".row_edit_ajax").click(row_edit_ajax);	
}

function rebind_task_edit_delete(parent){	
	$(parent).find(".row_delete_ajax").off('click').on('click', {target: parent}, row_delete_ajax);	
	$(parent).find(".row_edit_task").click(edit_new_task);	
}

// This rebinds all rating classes within the templates (not forms)
function rebind_ratings(parent){
	$(parent).find('.rating').each(function(i, v){
		// The radio button template tag shows which button was selected from None, 1, 2, 3. The number is then taken to use as score.
		var selection = 0;
		if($(v).text().trim() != 'None'){
			selection = parseInt($(v).text().trim());							
		}			
		$(v).children('.star_small').raty({
				  score		: selection,				  
				  readOnly  : true,				  
				  half      : false,
				  size      : 24,	 
				  hints		: [gettext('Less Important'), gettext('Important'), gettext('Very Important')], 
				  starOff   : 'star-off.png',
				  starOn    : 'star-on.png',
				  number    : 3,
				  path      : $.chasebot.STATIC_URL + 'raty/img/'
		});
	});
}

// This binds the single rating class within the add or edit form
function bind_rating_form(){
	$('#star').raty({
	  cancel    : true,
	  cancelOff : 'cancel-off-big.png',
	  cancelOn  : 'cancel-on-big.png',
	  cancelHint: gettext('Cancel this rating'),
	  half      : false,
	  size      : 24,	 
	  hints		: [gettext('Less Important'), gettext('Important'), gettext('Very Important')], 
	  starOff   : 'star-off-big.png',
	  starOn    : 'star-on-big.png',
	  number    : 3,
	  path      : $.chasebot.STATIC_URL + 'raty/doc/img/',
	  click		: function(score, evt) {
	  	if(score)
	  		$('#id_important_client_' + score).attr('checked', true);
	  	else
	  		$('#id_important_client_0').attr('checked', true);	  	  
	  }	  
	});
	
	for(var i = 1; i<=3 ;i++)
		if($('#id_important_client_' + i).is(':checked'))
			$('#star').raty('score', i);
}


function rebind_add(){
	$('#save_add_form').submit(row_add_save_ajax);	
	// $('.sales_item_submit_btn').off('click').on('click', function(){
		// $('#save_add_form').submit();
	// });	
			
};

function datepicker_reload(parent){
	$(parent).find('.date_picker').datepicker({ format: $('#locale').text(),	autoclose: 'True' });
	var is_showMeridian = false;
	if ($('#locale').text() == 'mm/dd/yyyy'){
		is_showMeridian = true;
	}
		
	$(parent).find('.timepicker-default').timepicker({showMeridian:is_showMeridian, defaultTime : false});			
};



function clear_filter(event){
	event.preventDefault();
	$(this).siblings('input').val('');
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
	$.chasebot.MODAL_OPEN = false;
}

function modal_opening(event){
	event.preventDefault();
	$.chasebot.MODAL_OPEN = true;
}

function open_modal_sales_item(event){
	event.preventDefault();	
	var url = $(this).attr("href") + "/";
	//var map = new Object();
	//map['modal'] = true;
	var data = 'modal';	
	$("#salesitems_modal").load(url, data, function() {		 
            $(this).modal('show'); // display the modal on url load            
            rebind_add();
            rebind_edit_delete($('#search_result'));
            rebind_paginator($('#search_result'));
            // rebind_filters($(''));
            $('#sales_item_filter').find(".form-filter-ajax").submit(filter_rows);			
			$('#sales_item_filter').find(".typeahead_sales_items").typeahead({ source: typeahead_sales_items });
			$('#sales_item_filter').find(".filter-close").click(clear_filter);            
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


function demo(event){
	event.preventDefault();
	$(this).button('loading');
	//$(this).button('reset')
	$('#form_demo').submit();	
}

function cancel_new_conversation(event){	
	//debugger;
	event.preventDefault();
	$('#new_conversation_div').empty();
}

function submit_new_conversation(event){
	event.preventDefault();
	var url = $(this).closest('#new_conversation_form').attr('action');
	var data = $(this).closest('#new_conversation_form').serialize();
	$.post(url, data, function (result) {
		if ($(result).find('#validation_error_ajax').text() == 'True') {						 
		 	$('#new_conversation_div').empty();
		 	$('#new_conversation_div').append(result);      		       		 
	 		rebind_new_conversation('#new_conversation_div'); 
	 		rebind_add_deals();
	 		datepicker_reload('#new_conversation_div'); 		       		
		}
		else{
			$('#new_conversation_div').empty();
			url = window.location.pathname + '?ajax';
			$('#search_result').load(url, function(){		
				rebind_edit_delete($('#search_result'));
				rebind_paginator($('#search_result'));
				rebind_add();				
			});	
		}
	});
}

// function open_deal_conversations(event){
	// event.preventDefault();
	// var url = $(this).attr("href");	
	// $('#new_conversation_div').load(url, function(result){					
		// rebind_new_conversation('#new_conversation_div');
		// rebind_add_deals();		
	// });
// }


function rebind_conversations(){
	$('.conversation').attr('href', function(i, current){
		return current + '?show_only_open_deals';
	})
}

function rebind_new_conversation(parent){
	$(parent).find('#new_conversation_cancel_button').off('click').on('click', cancel_new_conversation);   
	$(parent).find('#new_conversation_form').off('submit').on('submit', submit_new_conversation);
}

function new_conversation(event){	
	event.preventDefault();
	var url = $(this).attr("href") + "/";	
	$('#new_conversation_div').load(url, function(result){					
		rebind_new_conversation('#new_conversation_div');
		rebind_add_deals();	
		datepicker_reload('#new_conversation_div');	
	});
}

function edit_new_task(event){	
	event.preventDefault();
	var url = $(this).attr("href");
	$('#task_modal').empty();	
	$('#task_modal').load(url, function(result){
		$(this).modal('show');	
		$("#task_form").get(0).setAttribute("action", url);
		datepicker_reload('#task_modal');
		$('#task_form').submit({modal:'#task_modal', tasks_pane:'#tasks_pane', form:'#task_form'}, task_modal_add_save);
		reword_collapseable('#accordion_task');		
	});
}

function task_modal_add_save(event){
	event.preventDefault();	
	var modal = $(event.data.modal);
	var tasks_pane = $(event.data.tasks_pane);
	var form = $(event.data.form);
	// selector starts from Add Button (this)	
	var url = $(form).attr('action');		
	//var row = $(this).closest('tr'); //real row containing also the form	
	var data = $(form).serialize();
  	
  	$.post(url, data, function (result) {
  		//If there are validation errors upon adding the field
  		if ($('#validation_error_ajax', result).text() == 'True') {  			 
    		 modal.empty();    		 
      		 modal.append(result);
      		 modal.find('#task_form').get(0).setAttribute("action", url);      		       		 
      		 modal.find('#task_form').submit({modal:'#task_modal', tasks_pane:'#tasks_pane', form:'#task_form'}, task_modal_add_save);
       		 datepicker_reload($(modal));      		
       		 rebind_task_edit_delete($(tasks_pane));
      		 rebind_paginator($(tasks_pane));      		
    	}
    	else {
    		//if there is no error then insert the added row before the current add-button row. (last row)
    		$(modal).modal('hide');    		
    		$(modal).empty();
    		$(tasks_pane).empty();
    		$(tasks_pane).append(result);
      		rebind_task_edit_delete($(tasks_pane));
      		rebind_paginator($(tasks_pane));      		      		      		
    	}
  	});  	
};


function deals_in_progress_coversations(event){
	event.preventDefault();
	if($(this).hasClass('active')){		
		var url = window.location.pathname + '?ajax';
		$('#search_result').load(url, function(result){					
			rebind_edit_delete($('#search_result'));
			rebind_paginator($('#search_result'));
			rebind_add();	
			rebind_ratings($('#search_result'));			
			$('#contacts_title').text(gettext("Contacts"));
		});	
	}
	else{
		var url = window.location.pathname + '?ajax&show_only_open_deals';
		$('#search_result').load(url, function(result){					
			rebind_edit_delete($('#search_result'));
			rebind_paginator($('#search_result'));
			rebind_add();	
			rebind_ratings($('#search_result'));
			rebind_conversations();	
			$('#contacts_title').text(gettext("Contacts with deals in progress"));
		});			
	}
}


function deals_in_progress(event){
	event.preventDefault();
	if($(this).hasClass('active')){
		var url = '/?ajax';
		$('#search_result').load(url, function(result){					
			rebind_edit_delete($('#search_result'));
			rebind_paginator($('#search_result'));
			rebind_add();	
			rebind_ratings($('#search_result'));			
			$('#contacts_title').text(gettext("Contacts"));		
		});	
	}
	else{		
		var url = '/?ajax&show_only_open_deals';
		$('#search_result').load(url, function(result){					
			rebind_edit_delete($('#search_result'));
			rebind_paginator($('#search_result'));
			rebind_add();	
			rebind_ratings($('#search_result'));
			rebind_conversations();	
			$('#contacts_title').text(gettext("Contacts with deals in progress"));			
		});			
	}	
}

function reword_collapseable(parent){
    $(parent).on('shown', function () {       
        $('#collapse_task_head').text(gettext("Less Details"));
    });
    $(parent).on('hidden', function () {       
        $('#collapse_task_head').text(gettext("More Details"));
    });
}



$(document).ready(function (){	
	reword_collapseable('#accordion_task');
	rebind_add();
	rebind_edit_delete($('#search_result'));
	rebind_task_edit_delete($('#tasks_pane'));
	rebind_paginator($('#search_result'));
	rebind_paginator($('#tasks_pane'));
	rebind_filters($('body'));
	rebind_ratings($('#search_result'));
	rebind_ratings($('#business_card_modal'));
	$(".modal_link_sales_item").click(open_modal_sales_item);
	//$(".modal_link_business_card").click(open_modal_business_card);
	$('#salesitems_modal').on('hidden', modal_closing);
	$('#salesitems_modal').on('shown', modal_opening);
	$('#timezone_dropdown').change(timezone_dropdown);	
	$('.timezone_help').click(show_timezone_help);	
	datepicker_reload('body');
	$('#invite-button').click(invite_colleague);
	$('#demo-button').click(demo);
	$('#new_conversation_button').off('click').on('click',new_conversation);
	$('#new_task_button').off('click').on('click', edit_new_task);
	$('#deals_in_progress').off('click').on('click', deals_in_progress);
	if($('#show_only_open_deals').text() == 'True')
		$('#deals_in_progress_calls').button('toggle');
	$('#deals_in_progress_calls').off('click').on('click', deals_in_progress_coversations);
	
	bind_rating_form();	
});


