function cloneMore(selector, type, row) {
	//Selector is in this case the node to clone from (empty extra form in a separate section in the DOM tree)
    var empty_X = $(selector).clone(true);    
    //Total is teh number of available tabs (deals)
    var total = $(row).find('#attached_deals_tab li').length;
        
    //Rename each extra_deal-0- occurance of the cloned element to deals-total-, whatever total is currently     
    empty_X.find(':input').each(function() {
        var name = $(this).attr('name').replace('extra_deal-0-', type + '-' + total + '-');
        var id = 'id_' + name;
        $(this).attr({'name': name, 'id': id});
    });
    empty_X.find('label').each(function() {
        var newFor = $(this).attr('for').replace('extra_deal-0-', type + '-' + total + '-');
        $(this).attr('for', newFor);
    });    
    return empty_X;
}


function fill_emptyX_with_predefined_or_existing_data(selected_id, type, empty_X, path, row, contact_id){	 	
	var url = '';
	
	//If contact_id is provided it means that we are dealing with an open deal, since we need to open the existing open instance for further processing
	if(contact_id){
		url = path + selected_id + '/' + contact_id;
	}
	//otherwise we are adding a new deal 
	else{
		url = path + selected_id + '/';
	}
			
	//Here we make an ajax call to the server to get the data from the selected deal Template or get the data from the last open deal instance,
	//In either case the user can then override these values  
	$.ajax({
     	  type: 'GET',
		  url: url,		  	  
		  contentType: "application/json; charset=utf-8",
		  dataType: 'json',
		  success: function (data) {		  	
		  	var total = $(row).find('#attached_deals_tab li').length;
		  	
		  	var template_name = '';
		    var deal_instance_name = '';
		  			  			  	
			if(contact_id){
				//if contact_id is provided it means we are dealing with open deal
				//the returned json object will be from a deal object, therefore we check against deal specific fields
				template_name = data[0].fields['deal_template_name'];
				deal_instance_name = data[0].fields['deal_instance_name'];
			}
			else{
				//otherwise we are adding a new deal and the returned json object will be a deal_template object, and therefore we need to check against deal_template specific fields
				template_name = data[0].fields['deal_name'];				
			}

			// Set all the values from json into the cloned fields accordingly
			//Attention, when setting ANY field to the value from json follow these rules: 
			// Set the value for all inputs with .attr('value', foo)
			// Set the value for all dropdowns with val() so that the primary key is used.
			// for m2m you need to use val() on an array (see below)
				
			empty_X.find('#id_deals-' + total + '-deal_template_name').attr('value', template_name);
			empty_X.find('#id_deals-' + total + '-deal_instance_name').attr('value', deal_instance_name);
					  	
		  	//empty_X.find('#id_deals-' + total + '-deal_description').attr('value', data[0].fields['deal_description']);
		  	empty_X.find('#id_deals-' + total + '-deal_description').text(data[0].fields['deal_description']);
		  	empty_X.find('#id_deals-' + total + '-sales_term').val(data[0].fields['sales_term']);		  			  	
		  	empty_X.find('#id_deals-' + total + '-price').attr('value', data[0].fields['price']);
		  	empty_X.find('#id_deals-' + total + '-currency').val(data[0].fields['currency']);
		  	empty_X.find('#id_deals-' + total + '-quantity').attr('value', data[0].fields['quantity']);		  	
	  		
	  		if ('status' in data[0].fields)
				empty_X.find('#id_deals-' + total + '-status').val(data[0].fields['status']);		  	
		  	else
		  		empty_X.find('#id_deals-' + total + '-status>option:eq(1)').prop('selected', true);		  	
		  	
		  	if('deal_template' in data[0].fields)
		  		empty_X.find('#id_deals-' + total + '-deal_template').val(data[0].fields['deal_template']);
		  	else
		  		empty_X.find('#id_deals-' + total + '-deal_template').val(data[0].pk);
		  	
		  	//m2m needs special treatment with arrays
		  	var vals = [];
		  	for (i=0; i<=data[0].fields['sales_item'].length;i++)
		  		vals.push(data[0].fields['sales_item'][i]);
		  	empty_X.find('#id_deals-' + total + '-sales_item').val(vals);

			//var newname = '';
		    if(contact_id){
		    	//Open deal
				//newname = deal_instance_name;
				//We need to populate the open_deal_id that was selected from dropdown into a hidden field. This will be later used in request.POST on server
				// to load the former open deal instance 
				//TODO: Maybe we could pass UUID of the deal and the set by json, so that we don't have to load the open_deal again in request.POST'
				empty_X.find('#id_deals-' + total + '-attached_open_deal_id').attr('value', selected_id);				
			}
		    //else{
		    	//newname = template_name;		    			    	
		    //}		    	
		    //$('#previous_dealinstance_name').text(newname);
		    
		    $('#deal_modal_body').children('form').append(empty_X);
	    	rebind_attach_deals('#deal_modal_body', row);	    	 
	    	calc_total_value();   
	    	validator = validation_rules('#deal_modal_form');	
	    	$('#deal_modal').find('#deal_modal_confirm_btn').off('click').on('click', {row: row, validator:validator}, add_deal_to_formset);
	    	$('#deal_modal').find('#deal_modal_confirm_btn').show();
		  }		  
		});	
}

function add_deal_to_formset(event){ 
	event.preventDefault();
	var validator = event.data.validator;
	
	validator.form();
	if(validator.invalidElements().length > 0){
		return;	
	}
	
	var row = $(event.data.row);
	//var newname = $('#previous_dealinstance_name').text();
	var total = $(row).find('#attached_deals_tab li').length;
	//if(!newname){
	newname = $('#deal_modal_body').find('#id_deals-' + total + '-deal_instance_name').val();
	//}		
		
	//The newname either template_name or instance_name will be stripped from spaces and dots and replaced with _. So that its compatible for URL id's
    var slug =  newname.replace(/ /g,"_").replace(/\./g,"_");
    //Now that the copying of json into the cloned fields is over we create the tabs						
	var a=document.createElement('a');
    a.setAttribute('data-toggle', 'tab');
    a.setAttribute('href', '#' + slug);
    a.innerHTML = newname;
	
	var li=document.createElement('li');
	li.appendChild(a);
	
    //Attaching the tab header
    $(row).find('#attached_deals_tab').append(li);
    
    //creating the tab content
    var div=document.createElement('div');
    div.setAttribute('class', 'tab-pane');
    
    //Setting the id of tab content to the same url href of tab header, so that it can be found when user clicks on the tab header
    div.setAttribute('id', slug);
    
    var source = null;
    if($('#deal_modal_body').children('form').children('div').length == 1)
    	source = $('#deal_modal_body').children('form').children('div');
    else
    	source = $('#deal_modal_body').children('form').children('div').eq(1); 
    
    //attaching the cloned element with json values to the tab content 
    $(div).append($(source));
    // var currency = source.find('#id_deals-' + total + '-currency').val();
    // $(div).find('#id_deals-' + total + '-currency').val(currency);
    // var salesterm = source.find('#id_deals-' + total + '-sales_term').val();
    // $(div).find('#id_deals-' + total + '-sales_term').val(salesterm);
    // var deal_template = source.find('#id_deals-' + total + '-deal_template').val();   
	// $(div).find('#id_deals-' + total + '-deal_template').val(deal_template);  	
    // var sales_items = source.find('#id_deals-' + total + '-sales_item').val();        
  	// $(div).find('#id_deals-' + total + '-sales_item').val(sales_items);
        
    $(row).find('#tab-content').append(div);

	//TODO: solve by chosen instead
	if(contact_id){
		//In case of open deal we need to remove the selected open deal from the dropdown, so it can't be added again to the same call.
		//$(row).find("#id_opendeals_add_form-open_deal_template option[value='" + selected_id + "']").remove();
	}
	else{
		//In case of adding a new deal we need to remove the selected deal Template from the dropdown, so it can't be added again to the same call.
		$(row).find("#id_deals_add_form-deal_template option[value='" + selected_id + "']").remove();				
	}

	//Now that everything is in place, show the tab actively								  				
	//$(a).tab('show');
	
	//Now that its shown, change the m2m multi-selection field to a chosen type field. 
	//$(row).find('#id_deals-' + total + '-sales_item').chosen({no_results_text: 'No results match'});
	
	//Finally set the total form value within the formset to the number of added tabs, so that it can be saved in request.POST 
	total = $(row).find('#attached_deals_tab li').length;
	$(row).find('#id_deals-TOTAL_FORMS').attr('value', total);
	
	$('#deal_modal').modal('hide');
	create_btn_deals(row);
}

function add_deals(event){
	//Adding new deals
	event.preventDefault();
		
	var row = $(event.data.row);	
	var type = 'deals';
	var empty_X = cloneMore('#X div:first', type, row);
		
	//Getting the deal Template id from the selected dropdown
	var selected_id = $('#deal_modal_body').find('.pre_defined_deal_dropdown option:selected').val()
	if (selected_id){
		fill_emptyX_with_predefined_or_existing_data(selected_id, type, empty_X, '/deal_template/', row);		
	}	
	$(this).parent().parent().parent().remove();
}

function add_opendeals(event){
	//Adding an open deal
	event.preventDefault();
	
	var row = $(event.data.row);
	var type = 'deals';
	var empty_X = cloneMore('#X div:first', type, row);
	
	//Getting the open deal instance id from the selected dropdown
	var selected_id = $('#deal_modal_body').find('#id_opendeals_add_form-open_deal_template option:selected').val()
	var contact_id = $('#deal_modal_body').find('#contact_id').text()
	if (selected_id){
		fill_emptyX_with_predefined_or_existing_data(selected_id, type, empty_X, '/open_deal/', row, contact_id);		
	}
	$(this).parent().parent().parent().remove();
}

function show_tab(e){
	//Uncheck all active tab checkboxes
	//$('.last_active_tab').attr('checked', false);
	//var current_tab_href = $(this).attr('href');
	
	//current_tab_href is the #id that the tab-header is pointing to. Hence by searching for #id we are searching within the tab content.	
	//$(current_tab_href).find('.last_active_tab').attr('checked', true);	
	//now the last_actice_tab boolean is set to true of the current tab 
}

function rebind_attach_deals(parent, row){
	//Upon opening make sure that all deals from attached_deal_formset will get chosenified. 
	// Attention: Do NOT chosenify the extra-deal form, or it would break.	
	var total = $(row).find('#id_deals-TOTAL_FORMS').val();
	for(i=0;i<=total;i++){
		$(parent).find('#id_deals-' + i + '-sales_item').chosen({no_results_text: gettext('No results match')});
		
		var total_value = multiply($(parent).find('#id_deals-' + i +  '-price').val(), $(parent).find('#id_deals-' + i +  '-quantity').val());		  
		//total_value = (Math.round(total_value*100)/100);
		$(parent).find('#id_deals-' + i +  '-total_value').val(total_value);
	}
}

var bd = {"BigDecimal":BigDecimal, "BigInteger":BigInteger, "RoundingMode":RoundingMode};
function run(opts) {
	var result;
	var ops = {'*': "multiply", '/': "divide", '+': "add", '-': "subtract"};
	var a = new bd.BigDecimal("" + opts.a);
	var b = new bd.BigDecimal("" + opts.b);
	var op = ops[opts.op];
	if (op == "divide") {
		return a.divide(b, 300, bd.RoundingMode.HALF_UP());
	} else {
		return a[op].call(a, b);
	}
}

if(document.addEventListener){
	document.addEventListener("DOMContentLoaded", function() {
		
		// var result = run({"a":"321.4567890","b":"123456789.123456789987654321","op":"*"});
		// document.getElementById("browser_result").innerHTML = result;
	});
}
	
function multiply(a, b){
	//var bigdecimal = require("bigdecimal");
	// var bd = {"BigDecimal":BigDecimal, "BigInteger":BigInteger, "RoundingMode":RoundingMode};
	// var total_value = new bd.BigDecimal(a) * new bd.BigInteger(b);
	// return total_value
	var result = run({"a":a,"b":b,"op":"*"});
	return result;
} 

function rebind_add_deals(){
	//rebind_attach_deals();
	//$("#add_deals_button").click(add_deals);
	//$("#add_opendeals_button").click(add_opendeals);
	
	//subscribing to an event for when tabs are clicked on, they should be made the only active-tab.
	//$('a[data-toggle="tab"]').on('shown', show_tab);
	
	//If no tab is already active, then the first one found shall be made active. Otherwise the last-active-tab will be made active. 
	//Useful when there are validation errors on request.POST and we need to re-activate the previous active tab. 
	// if($('#attached_deals_tab > li.active').length == 0)
		// $('#attached_deals_tab a:first').tab('show');
}

$(document).ready(function () {	
	rebind_add_deals();
});