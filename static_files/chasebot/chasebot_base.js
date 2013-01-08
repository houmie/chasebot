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


function partial(func /*, 0..n args */) {
  var args = Array.prototype.slice.call(arguments, 1);
  return function() {
    var allArguments = args.concat(Array.prototype.slice.call(arguments));
    return func.apply(this, allArguments);
  };
}


if (!String.prototype.trim) {
   //code for trim
   String.prototype.trim=function(){
		return this.replace(/^\s+|\s+$/g, '');
	};
};


function row_delete_ajax(event) {
    event.preventDefault();    
    var target = $(event.data.target);
    var rebind_func = event.data.rebind_func;
    if (confirm(gettext('Are you sure you want to delete this row?'))) {
    	var url = $(this).attr("href");    	  		
        $.post(url, function(result){
        	$(target).empty();
        	$(target).append(result);        	
        	rebind_func();
        }); 
    }
};

function delete_rebind_todo(){
	rebind_edit_delete($(target));
	rebind_paginator($(target));
	rebind_task_edit_delete($(target));			
	rebind_deal_templates();
}

function filter_rows(event){
	event.preventDefault();
	var url = '';		
	
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
	});
	//Even if no filter are set, still the query to server is required to get all list and undo filters.	
	$('#search_result').load(url, function(){		
		//rebind_edit_delete($('#search_result'));
		//rebind_paginator($('#search_result'));
		//rebind_add();
	});	
};

function paginator_navigate(event) {	
	event.preventDefault();	
	var url = $(this).attr('href');	
	var target_pane = $(event.data.target_pane);
	var rebind_func = event.data.rebind_func;
	//If the page containing the paginator is a modal, then we need to know its type, to modify the url accordingly 
	//Otherwise the url would point to the page containing the modal. 
	
	$(target_pane).load(url, function(result){
		rebind_func();		
	});		
};


function paginator_rebind_todo(){
	rebind_edit_delete($(target_pane));
	rebind_task_edit_delete($(target_pane));
	rebind_paginator($(target_pane));		
	rebind_add();	
	rebind_ratings($(target_pane));	
	rebind_business_card_modal_link();
	$('.conversation').off('click').on('click', conversation_clicked);
	$('#new_conversation_button').off('click').on('click',new_conversation);
	rebind_deal_templates();
}

function rebind_conversation_deal_btn(row){
	create_btn_deals(row);
	bind_attach_deal(row);
}

//Used by Conversation & Sales Items
function reload_edit_save_cancel_buttons(row, url, isNewConversation){
	$(row).find("#save_edit_form").submit({url:url, isNewConversation:isNewConversation}, row_edit_save_ajax);
	$(row).find("#save_edit_button").click(function(){
		$(row).find("#save_edit_form").submit();
	});
	if(isNewConversation){
		$(row).find("#cancel_edit_button").off('click').on('click', function(event){
			event.preventDefault();
			$(row).remove();
			$('#new_conversation_button').button('toggle');
		});		
	}		
	else
		$(row).find("#cancel_edit_button").off('click').on('click', function(event){
			event.preventDefault();	
			var url = $(this).attr("href") + "/";
			var row = $(this).closest('form').closest('tr'); //real row containing also the submit-edit-form	
			row.load(
				// get only the children (td) of the tr and attach them to the existing empty row.
		    	url + ' td',
		    	function () {		    			              		
		      		rebind_edit_delete($(row), function(row, url, isNewConversation){						
						reload_edit_save_cancel_buttons(row, url, isNewConversation);
		      		}); 
		    	}
		  	);
		});
	//rebind_add_deals();	
	datepicker_reload($(row));
}


function validation_rules(form){
	// add the rule here
	$.validator.addMethod("valueNotEquals", function(value, element, arg){
		return arg != value;
	}, gettext('Please select an item!'));
	
	var validator = $(form).validate({
	  	// options
		errorPlacement: function(error, element){
		  	var field_error = $(form).find('#id_' + element.attr('name')).siblings('.field_error');
		  	if(field_error.length > 0){
		  		error.appendTo(field_error);
		  	}				
			else{
				field_error = $(form).find('#id_' + element.attr('name')).closest('td').children('.field_error');
				error.appendTo(field_error);
			}				
			$(field_error).show();
		},
		ignore: ':hidden:not(.chzn-done)'						  
	});
	
	$(form).find('.quantity').each(function(){
		$(this).rules('add', {
			required: true,
		      digits: true
		});
	});
	
	$(form).find('.price').each(function(){
		$(this).rules('add', {
			required: true,
		      number: true
		});
	});

	
	$(form).find('select.mandatory').each(function(){
		$(this).change(function(){
			$(this).valid();
		});
		$(this).rules('add', {
			valueNotEquals: ""
		});				
	});
	
	$(form).find('input.mandatory, textarea.mandatory').each(function(){		
		$(this).rules('add', {
			required: true,
		});				
	});
	
	$(form).find('select.multi_select_mandatory').each(function(){
		$(this).chosen().change(function(){
			$(this).valid();
		});
		$(this).rules('add', {
			required: true,
		});
	});
	
	return validator;
}

function create_btn_deals(row){
	//For each tab on attached deals tab control we create one button 
	$(row).find('#clipped_deals').empty();
	$(row).find('#attached_deals_tab li a').each(function() {      			
		var btn = $('<a/>', {class: 'btn btn-small', href: $(this).attr('href')});
		//var icon = $('<i/>', {class: 'icon-paper-clip icon-large'}).appendTo(btn);
		var span = $('<span/>', { class: 'badge badge-info', text: $(this).text()}).appendTo(btn);
		$(row).find('#clipped_deals').append(btn);
		
		btn.click(function(event){
			event.preventDefault();
			//The btn's href is the same as its tab pendant's href, which in turn points to the tab content.
			//Hence we clone the content of the tab within the loaded row only.
			var cloned_tab_div = $(row).find(btn.attr('href')).children().clone();
			$('#deal_modal_body').empty();
			//Form is only required for validation, but it doesn't submit
			var form = $('<form/>', {id: 'deal_modal_form', action: '.', method: 'get'}).append(cloned_tab_div);		
			$('#deal_modal_body').append(form);
			
			var total = $(row).find('#attached_deals_tab li').length;			

    		var validator = validation_rules('#deal_modal_form');						
    		
			$('#deal_modal_confirm_btn').off('click').on('click', {validator:validator, btn:btn}, function(event){
				event.preventDefault();				
							
				if(validator.invalidElements().length == 0){
					var source = $('#deal_modal_body').children('form').children('div').clone();
	    			var target = $(row).find('#tab-content').find($(btn).attr('href'));    			
	    			target.empty();
	    			target.append($(source));
	    			$('#deal_modal').modal('hide');    			
	    			create_btn_deals(row);					
				}				
			});		
			
			rebind_attach_deals('#deal_modal_body', row); //TODO: Recheck later
			calc_total_price();
			$('#deal_modal').find('#modal_h3').text(gettext('Edit Deal'));   
			show_modal('#deal_modal');
		});			
	});	
}

function bind_attach_deal(row){
	$(row).find('#add_pre_deal').click(function(event){
		event.preventDefault();
		 var dropdown = $(row).find('#add_deals_dropdown div:first').clone();
		 $('#deal_modal_body').empty();
		 var form = $('<form/>', {id: 'deal_modal_form', action: '.', method: 'get'}).append(dropdown);
		 $('#deal_modal_body').append(form);			 
		 $('#deal_modal_body').find('#add_deals_button').off('click').on('click', {row: row}, add_deals);		 
		 $('#deal_modal').find('#deal_modal_confirm_btn').addClass("disabled");	
		 $('#deal_modal').find('#modal_h3').text(gettext('Add Pre-defined Deal'));
		 show_modal('#deal_modal');
	});
	
	$(row).find('#continue_deal').click(function(event){
		event.preventDefault();
		 var dropdown = $(row).find('#add_opendeals_dropdown div:first').clone();
		 $('#deal_modal_body').empty();
		 var form = $('<form/>', {id: 'deal_modal_form', action: '.', method: 'get'}).append(dropdown);
		 $('#deal_modal_body').append(form);
		 $('#deal_modal_body').find('#add_opendeals_button').off('click').on('click', {row: row}, add_opendeals);		 
		 $('#deal_modal').find('#deal_modal_confirm_btn').addClass("disabled");
		 $('#deal_modal').find('#modal_h3').text(gettext('Continue With Existing Deal'));
		 show_modal('#deal_modal');
	});	
	
	$(row).find('#new_deal').click(function(event){ 
		event.preventDefault();
		$('#deal_modal_body').empty();
		var form = $('<form/>', {id: 'deal_modal_form', action: '.', method: 'get'});
		$('#deal_modal_body').append(form);
		new_deal(row);      				 
		$('#deal_modal_body').find('.deal_status').val(1);
		$('#deal_modal').find('#deal_modal_confirm_btn').off('click').on('click', {row: row}, add_deal_to_formset);
		$('#deal_modal').find('#deal_modal_confirm_btn').removeClass("disabled");
		$('#deal_modal').find('#modal_h3').text(gettext('Create Your Own Deal'));     				 
		show_modal('#deal_modal');
	});	
}

function calc_total_price(){
	$('#deal_modal_body').find('.quantity').off('change').on('change', calc_totals);
	$('#deal_modal_body').find('.price').off('change').on('change', calc_totals);
}

function calc_totals(event){	
  	var total_price = $('#deal_modal_body').find('.quantity').val() * $('#deal_modal_body').find('.price').val();
	total_price = (Math.round(total_price*100)/100);
	$('#deal_modal_body').find('.total_price').val(total_price); 
}

//Currently used by Conversations & sales items
function row_edit_ajax(event) {	
	event.preventDefault();	
	// e.g. url = '/sales_item/edit/8' 
	var url = $(this).attr("href") + "/";
  	var rebind_func = event.data.rebind_func;
  	//e.g. get whole row to be replaced with editing fields
  	var row = $(this).closest('tr');
	row.load(url, function (result) {
    		//Once loaded make sure the submit-form will be redirected to 'row_edit_save_ajax' once submitted. Url is parameter 
      		reload_edit_save_cancel_buttons($(row), url, false);
      		//rebind_func();  
      		rebind_conversation_deal_btn($(row));    		      		  		
    	}
  	);  	
};



function show_modal(target){
	$(target).modal({
        backdrop: true,
        keyboard: true
    }).css({
        width: 'auto',        
        'margin-left': function () {
            return -($(this).width() / 2);
        }
    });
    
	$(target).modal('show');
}


function row_add_save_sales_item(event){
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
      		 rebind_sales_item();      		       		       		       		
    	}
    	else {
    		//if there is no error then insert the added row before the current add-button row. (last row)    		
    		$('#search_result').empty();
    		$('#search_result').append(result);    	
    		rebind_sales_item();      		
      		$(".item_name").val('');
    	}
  	});
};

//Used by Conversation and Sales Items
function row_edit_save_ajax(event) {
	event.preventDefault();
	// selector starts from Edit Button (this)	
	var url = event.data.url;
	var isNewConversation = event.data.isNewConversation;
	
  	var row = $(this).closest('tr');  	
  	var data = $(this).closest('#save_edit_form').serialize();
  	
  	$.post(url, data, function (result) {
  		//If there are validation errors upon editing the field
    	if ($('#validation_error_ajax', result).text() == 'True') {
    		//if so, then we empty the current row and load the invalid-indicating-forms in the row 
    		//and attach events to the still existing save and cancel buttons
    		row.empty();    		    		
      		row.append(result);      			
      		reload_edit_save_cancel_buttons($(row), url, false);     		
    	}
    	else {
    		//if no error, then simply add the full 'tr' html row (with delete and edit icons) behind this row and remove this row. 
    		var row_before = $(result).insertBefore(row);  		
      		row.remove();      		  
      		rebind_edit_delete('#search_result', function(row_before){
      			rebind_conversations($(row_before));
      		});	
      		if(isNewConversation)
      			$('#new_conversation_button').button('toggle');
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


function rebind_paginator(source, rebind_func){	
	source.find(".paginator_nav_links").off('click').on('click', {target_pane: source, rebind_func:rebind_func}, paginator_navigate);
}


function rebind_edit_delete(source, rebind_func){	
	$(source).find(".row_delete_ajax").off('click').on('click', {target: source, rebind_func:rebind_func}, row_delete_ajax);	
	$(source).find(".row_edit_ajax").off('click').on('click', {rebind_func:rebind_func}, row_edit_ajax);	
}

function rebind_task_edit_delete(parent){	
	$(parent).find(".row_delete_ajax").off('click').on('click', {target: parent}, row_delete_ajax);	
	$(parent).find(".row_edit_task").click(edit_new_task);	
}

function rebind_event_edit_delete(parent){	
	$(parent).find(".row_delete_ajax").off('click').on('click', {target: parent}, row_delete_ajax);	
	$(parent).find(".row_edit_event").click(edit_new_event);	
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
	$(parent).find(".typeahead_deals_deal_name").typeahead({ source: typeahead_deals_deal_name });
	$(parent).find(".typeahead_deals_sales_item").typeahead({ source: typeahead_deals_sales_item });
	$(parent).find(".typeahead_deals_price").typeahead({ source: typeahead_deals_price });
	$(parent).find(".typeahead_deals_sales_term").typeahead({ source: typeahead_deals_sales_term });
	$(parent).find(".typeahead_deals_quantity").typeahead({ source: typeahead_deals_quantity });	
	$(parent).find(".filter-close").click(clear_filter);
};


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
	$(this).button(gettext('Loading'));	
	$('#form_invite').submit();	
}


function demo(event){
	event.preventDefault();
	$(this).button('loading');	
	$('#form_demo').submit();	
}


// function rebind_conversations(){
	// $('.conversation').attr('href', function(i, current){
		// return current + '?show_only_open_deals';
	// })
// }

function rebind_new_conversation(parent){
	$(parent).find('#new_conversation_cancel_button').off('click').on('click', cancel_new_conversation);   
	$(parent).find('#new_conversation_form').off('submit').on('submit', submit_new_conversation);
}

function new_conversation(event){
	event.preventDefault();
	if($(this).hasClass('active')){
		$('#new_conversation_div').empty();		
		return;
	}
	var contact_id = $('#contact_id').text();
	var url = '/contact/' + contact_id + '/call/add/';
	var row = $('<tr/>');
	row.load(url, function(result){
		$('#search_result').prepend(row);
  		reload_edit_save_cancel_buttons($(row), url, true);  		
  		bind_attach_deal(row);
		datepicker_reload('#new_conversation_div');			
	});		
}

function new_conversation_old(event){	
	event.preventDefault();
	if($(this).hasClass('active')){
		$('#new_conversation_div').empty();		
		return;
	}
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


function negotiate_deal(event){	
	event.preventDefault();
	event.stopPropagation();
	var url = $(this).attr("href");
	$('#deal_modal_body').empty();
	var form = $('<form/>', {id: 'deal_modal_form', action: '.', method: 'post'});		
	$('#deal_modal_body').append(form);
	form.load(url, function(result){		
		show_modal('#deal_modal');
		$(this).get(0).setAttribute("action", url);
		datepicker_reload('#deal_modal_body');				
		$('#deal_modal_body').find('#id_sales_item').chosen({no_results_text: gettext('No results match')});		
		calc_total_price();
		$('#deal_modal').find('#modal_h3').text(gettext('Negotiate Deal'));
		$(this).submit({modal:'#deal_modal', form:$(this)}, negotiate_deal_submit);	
		
		var validator = validation_rules('#deal_modal_form');			
		
		$('#deal_modal').find('#deal_modal_confirm_btn').off('click').on('click', {validator:validator}, function(){
			validator.form();
			if(validator.invalidElements().length == 0){ 
				form.submit(); 
			}
		});	
	});
}

function negotiate_deal_submit(event){
	event.preventDefault();
	var form = event.data.form;
	var url = $(form).attr('action');
	var data = $(form).serialize();
	var modal = event.data.modal;	
	
	$.post(url, data, function (result) {
  		//If there are validation errors upon adding the field
  		if ($('#validation_error_ajax', result).text() == 'True') {  			 
    		 form.empty();    		 
      		 form.append(result);
      		 //modal.find('#event_form').get(0).setAttribute("action", url);      		       		 
      		 //modal.find('#event_form').submit({modal:'#event_modal', events_pane:'#events_pane', form:'#event_form'}, event_modal_add_save);
      		 $('#deal_modal_body').find('#id_sales_item').chosen({no_results_text: gettext('No results match')});
       		 datepicker_reload('#deal_modal_body');
       		 calc_total_price();      		
       		 //rebind_event_edit_delete($(events_pane));
      		 //rebind_paginator($(events_pane));      		
    	}
    	else {
    		//if there is no error then insert the added row before the current add-button row. (last row)
    		$(modal).modal('hide');    		
    		//$(modal).empty();
    		$('#tab_open_deals').empty();
    		$('#tab_open_deals').append(result);
    		load_open_deals();
    		//$(events_pane).empty();
    		//$(events_pane).append(result);
      		//rebind_event_edit_delete($(events_pane));
      		//rebind_paginator($(events_pane));      		      		      		
    	}
  	});
}


function edit_new_event(event){	
	event.preventDefault();
	var url = $(this).attr("href");
	$('#event_modal').empty();
	$('#event_modal').load(url, function(result){
		$(this).modal('show');	
		$("#event_form").get(0).setAttribute("action", url);
		datepicker_reload('#event_modal');
		$('#event_form').submit({modal:'#event_modal', events_pane:'#events_pane', form:'#event_form'}, event_modal_add_save);		
	});
}

function event_modal_add_save(event){
	event.preventDefault();	
	var modal = $(event.data.modal);
	var events_pane = $(event.data.events_pane);
	var form = $(event.data.form);		
	var url = $(form).attr('action');	
	var data = $(form).serialize();
  	
  	$.post(url, data, function (result) {
  		//If there are validation errors upon adding the field
  		if ($('#validation_error_ajax', result).text() == 'True') {  			 
    		 modal.empty();    		 
      		 modal.append(result);
      		 modal.find('#event_form').get(0).setAttribute("action", url);      		       		 
      		 modal.find('#event_form').submit({modal:'#event_modal', events_pane:'#events_pane', form:'#event_form'}, event_modal_add_save);
       		 datepicker_reload($(modal));      		
       		 rebind_event_edit_delete($(events_pane));
      		 rebind_paginator($(events_pane));      		
    	}
    	else {
    		//if there is no error then insert the added row before the current add-button row. (last row)
    		$(modal).modal('hide');    		
    		$(modal).empty();
    		$(events_pane).empty();
    		$(events_pane).append(result);
      		rebind_event_edit_delete($(events_pane));
      		rebind_paginator($(events_pane));      		      		      		
    	}
  	});  	
};


// function deals_in_progress_coversations(event){
	// event.preventDefault();
	// if($(this).hasClass('active')){		
		// var url = window.location.pathname + '?ajax';
		// $('#search_result').load(url, function(result){					
			// rebind_edit_delete($('#search_result'));
			// rebind_paginator($('#search_result'), url);
			// rebind_add();	
			// rebind_ratings($('#search_result'));			
			// $('#contacts_title').text(gettext("Contacts"));
		// });	
	// }
	// else{
		// var url = window.location.pathname + '?ajax&show_only_open_deals';
		// $('#search_result').load(url, function(result){					
			// rebind_edit_delete($('#search_result'));
			// rebind_paginator($('#search_result'), url);
			// rebind_add();	
			// rebind_ratings($('#search_result'));
			// rebind_conversations();	
			// $('#contacts_title').text(gettext("Contacts with deals in progress"));
		// });			
	// }
// }
// 
// 
// function deals_in_progress(event){
	// event.preventDefault();
	// if($(this).hasClass('active')){
		// var url = '/?ajax';
		// $('#search_result').load(url, function(result){					
			// rebind_edit_delete($('#search_result'));
			// rebind_paginator($('#search_result'), url);
			// rebind_add();	
			// rebind_ratings($('#search_result'));			
			// $('#contacts_title').text(gettext("Contacts"));		
		// });	
	// }
	// else{		
		// var url = '/?ajax&show_only_open_deals';
		// $('#search_result').load(url, function(result){					
			// rebind_edit_delete($('#search_result'));
			// rebind_paginator($('#search_result'), url);
			// rebind_add();	
			// rebind_ratings($('#search_result'));
			// rebind_conversations();	
			// $('#contacts_title').text(gettext("Contacts with deals in progress"));			
		// });			
	// }	
// }

function reword_collapseable(parent){
    $(parent).on('shown', function () {       
        $('#collapse_event_head').text(gettext("Less Details"));
    });
    $(parent).on('hidden', function () {       
        $('#collapse_event_head').text(gettext("More Details"));
    });
}

function add_more_tag_to_all_notefields(){
	$('.cb_notes').filter(function(){
    	return $(this).innerHeight() / $(this).css('line-height').slice(0,-2) > 3; //more than 3 lines
	}).each(function(){
		var arr = [];				
	    while($(this).innerHeight() / $(this).css('line-height').slice(0,-2) > 3){	    		    		
	        arr.push($(this).text().slice(-10));
	        $(this).text($(this).text().slice(0,-10));				
	    }
	    arr.reverse();
	    var morecontent = arr.join("");
	    var extracontentspan = $("<span/>").text(morecontent).hide();
	    var extracontentbutton = $("<a/>",{href:"#", class:"badge badge-info"}).text(gettext("More...")).click(function(){
	        var span = $(this).prev().toggle();
	        if(span.is(':hidden'))
	        	$(this).text(gettext("More..."));
        	else
        		$(this).text(gettext("Less..."));
	    });
	    $(this).append(extracontentspan);
	    $(this).append(extracontentbutton);
	});
}

function load_business_card(event){	
	event.preventDefault();
	var url = $(this).attr("href");
	$('#business_card_modal').load(url, function(result){					
			rebind_ratings($('#business_card_modal'));
			$(this).modal('show');
	});		
}

function rebind_business_card_modal_link(){
	$('.business_card_modal_link').off('click').on('click', load_business_card);	
}


function deal_template_add_edit(event){
	event.preventDefault();
	var url = $(this).attr('href');
	$('#tab_predefined').load(url, function(result){
		validator = validation_rules('#pre_deal_form_id');
		
		$(this).find('#id_sales_item').chosen({no_results_text: gettext('No results match')});
		
		$(this).find('#pre_deals_id').off('click').on('click', function(event){
			event.preventDefault();
			tab_predefined_clicked();
		});		
		
		$('#pre_deal_form_id').submit({url:url}, function(event){
			event.preventDefault();
			var url = event.data.url;	
			var data = $(this).serialize();		
		  	$.post(url, data, function (result) {  		    		
				$('#tab_predefined').empty();
				$('#tab_predefined').append(result);
				rebind_deal_templates();
			});		
		});
		
		$('#deal_template_save_btn').off('click').on('click', {validator:validator}, function(event){
			event.preventDefault();
			validator.form();
			if(validator.invalidElements().length == 0){
				$('#pre_deal_form_id').submit();
			}
		});
		
		$('#deal_template_cancel_btn').off('click').on('click', function(event){
			event.preventDefault();
			tab_predefined_clicked();
		});
		
		$("#modal_sales_items_btn").off('click').on('click', function(event){
			event.preventDefault();	
			var url = $(this).attr("href") + "/";	
			$("#sales_items_modal_body").load(url, function(result) {		 
		        $('#salesitems_modal').modal('show'); // display the modal on url load            
		        rebind_sales_item();            
		     });
		});						
	});
}

function rebind_sales_item(){
	var source = $('#search_result');
	var rebind_func = rebind_sales_item;		
    rebind_edit_delete(source, rebind_func);
    $('#save_add_form').submit(row_add_save_sales_item);
    rebind_paginator(source, rebind_func);    
    $('#sales_item_filter').find(".form-filter-ajax").submit(filter_rows);			
	$('#sales_item_filter').find(".typeahead_sales_items").typeahead({ source: typeahead_sales_items });
	$('#sales_item_filter').find(".filter-close").click(clear_filter);
}

function rebind_deal_templates(){
	var source = $('#search_result');
	source.find('.deal_template_edit_btn').off('click').on('click', deal_template_add_edit);
	$('#new_deal_template_btn').off('click').on('click', deal_template_add_edit);
	var rebind_func = rebind_deal_templates;
	rebind_paginator(source, rebind_func);
	source.find(".row_delete_ajax").off('click').on('click', {target: source, rebind_func:rebind_func}, row_delete_ajax);
}


function tab_predefined_clicked(){	
	$('#tab_predefined').load('deals/', function(result){
		rebind_deal_templates();
	});	
	$('#main_tabs a[href="#tab_predefined"]').off('click');
	bind_main_tabs('tab_predefined');	
}


function rebind_contacts(){
	var rebind_func = rebind_contacts; 
	rebind_ratings($('#search_result'));
	rebind_paginator($('#search_result'), rebind_func);
	rebind_business_card_modal_link();
	rebind_edit_delete($('#search_result'), rebind_func);
	rebind_filters($('body'));		
	$('.conversation').off('click').on('click', conversation_clicked);
	
}
 

function tab_contacts_clicked(){
	$('#tab_contacts').load('contacts/', function(result){
		rebind_contacts();
	});
	$('#main_tabs a[href="#tab_contacts"]').off('click');
	bind_main_tabs('tab_contacts');
}

function tab_open_deals_clicked(){
	$('#tab_open_deals').load('open_deals/', function(result){				
		load_open_deals();
	});
	$('#main_tabs a[href="#tab_open_deals"]').off('click');
	bind_main_tabs('tab_open_deals');	
}


function load_open_deals(){
	$('#tab_open_deals tbody tr').off('click').on('click', function(){
			var clicked_on_same_row = false;
			var deal_row = $(this);
			if($(this).next('#details').length == 1){
				clicked_on_same_row = true;												
			}			
			$(".collapse").collapse('toggle');
			$('.collapse').on('hidden', function () {
				$(this).closest('tr').prev().find(".negotiate_deal_btn").hide();
				$(this).closest('#details').remove();										    	
		    })			
			
			if(clicked_on_same_row){				
				return;
			}
			
			var tr = $(this);			
			var url = $(this).find('#open_deal_url').text();
			var row = $('<tr/>', {id:'details'});	
			
			row.load(url, function(result){
				row.insertAfter(tr);
				row.find('#new_event_button').off('click').on('click', edit_new_event);
				rebind_event_edit_delete($('#events_pane'));
				tr.find(".negotiate_deal_btn").show();
				tr.find(".negotiate_deal_btn").off('click').on('click', negotiate_deal);
				
				$(".collapse").collapse('toggle');
			});
		});
}

function rebind_conversations(){
	var rebind_func = rebind_conversations;
	rebind_ratings($('#business_card_modal'));	
	rebind_paginator($('#search_result'), rebind_func);
	rebind_edit_delete($('#search_result'), rebind_func);
	$('.back2contacts').off('click').on('click', function(event){
		event.preventDefault();
		tab_contacts_clicked();
	});
	rebind_filters($('body'));
	$('#new_conversation_button').off('click').on('click',new_conversation);
}


function conversation_clicked(event){
	event.preventDefault();
	var url = $(this).attr('href');
	$('#tab_contacts').load(url, function(result){
		rebind_conversations();
	});
}



function bind_main_tabs(optionalArg){
	//Exclude the passed in tab name from being subscribed to the click event. (So that repetetive clicking on active tab
	// is ignored. However the other tabs get subscribed at the sam time.
	optionalArg = (typeof optionalArg === "undefined") ? null : optionalArg;
	if(optionalArg != 'tab_contacts')
		$('#main_tabs a[href="#tab_contacts"]').off('click').on('click', tab_contacts_clicked);
	if(optionalArg != 'tab_open_deals')
		$('#main_tabs a[href="#tab_open_deals"]').off('click').on('click', tab_open_deals_clicked);
	if(optionalArg != 'tab_predefined')	
		$('#main_tabs a[href="#tab_predefined"]').off('click').on('click', tab_predefined_clicked);	
}

$(document).ready(function (){
	bind_main_tabs();
	reword_collapseable('#accordion_task');	
	//rebind_task_edit_delete($('#tasks_pane'));
	//$(".modal_link_business_card").click(open_modal_business_card);	
	$('#timezone_dropdown').change(timezone_dropdown);	
	$('.timezone_help').click(show_timezone_help);	
	//datepicker_reload('body');
	$('#invite-button').click(invite_colleague);
	$('#demo-button').click(demo);
	
	//$('#new_task_button').off('click').on('click', edit_new_task);
	// $('#deals_in_progress').off('click').on('click', deals_in_progress);
	// if($('#show_only_open_deals').text() == 'True')
		// $('#deals_in_progress_calls').button('toggle');
	// $('#deals_in_progress_calls').off('click').on('click', deals_in_progress_coversations);	
	//bind_rating_form();
		
});


