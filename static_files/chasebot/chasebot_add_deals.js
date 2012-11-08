function cloneMore(selector, type) {
	//Selector is in this case the node to clone from (empty extra form in a separate section in the DOM tree)
    var newElement = $(selector).clone(true);    
    //Total is teh number of available tabs (deals)
    var total = $('#attached_deals_tab li').length;
        
    //Rename each extra_deal-0- occurance of the cloned element to deals-total-, whatever total is currently     
    newElement.find(':input').each(function() {
        var name = $(this).attr('name').replace('extra_deal-0-', type + '-' + total + '-');
        var id = 'id_' + name;
        $(this).attr({'name': name, 'id': id});
    });
    newElement.find('label').each(function() {
        var newFor = $(this).attr('for').replace('extra_deal-0-', type + '-' + total + '-');
        $(this).attr('for', newFor);
    });    
    return newElement;
}


function get_deal_or_dealtemplate(selected_id, type, newElement, path, contact_id){	 	
	var url = '';
	
	//If contact_id is provided it means that we are dealing with an open deal, since we need to open the existing open instance for further processing
	if(contact_id){
		url = path + selected_id + '/' + contact_id;
	}
	//otherwise we are adding a new deal 
	else{
		url = path + selected_id + '/';
	}
			
	//Here we make an ajax call to the server to get the data from the selected deal package or get the data from the last open deal instance,
	//In either case the user can then override these values  
	$.ajax({
     	  type: 'GET',
		  url: url,		  	  
		  contentType: "application/json; charset=utf-8",
		  dataType: 'json',
		  success: function (data) {		  	
		  	var total = $('#attached_deals_tab li').length;
		  	
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
				deal_instance_name = gettext('To be set after saving...');
			}

			// Set all the values from json into the cloned fields accordingly
			//Attention, when setting ANY field to the value from json follow these rules: 
			// Set the value for all inputs with .attr('value', foo)
			// Set the value for all dropdowns with val() so that the primary key is used.
			// for m2m you need to use val() on an array (see below)
				
			newElement.find('#id_deals-' + total + '-deal_template_name').attr('value', template_name);
			newElement.find('#id_deals-' + total + '-deal_instance_name').attr('value', deal_instance_name);
		  	
		  	newElement.find('#id_deals-' + total + '-deal_description').attr('value', data[0].fields['deal_description']);
		  	newElement.find('#id_deals-' + total + '-sales_term').val(data[0].fields['sales_term']);		  			  	
		  	newElement.find('#id_deals-' + total + '-price').attr('value', data[0].fields['price']);
		  	newElement.find('#id_deals-' + total + '-currency').val(data[0].fields['currency']);
		  	newElement.find('#id_deals-' + total + '-quantity').attr('value', data[0].fields['quantity']);		  	
	  		
	  		if ('status' in data[0].fields)
				newElement.find('#id_deals-' + total + '-status').val(data[0].fields['status']);		  	
		  	else
		  		newElement.find('#id_deals-' + total + '-status>option:eq(1)').prop('selected', true);		  	
		  	
		  	if('deal_template' in data[0].fields)
		  		newElement.find('#id_deals-' + total + '-deal_template').val(data[0].fields['deal_template']);
		  	else
		  		newElement.find('#id_deals-' + total + '-deal_template').val(data[0].pk);
		  	
		  	//m2m needs special treatment with arrays
		  	var vals = [];
		  	for (i=0; i<=data[0].fields['sales_item'].length;i++)
		  		vals.push(data[0].fields['sales_item'][i]);
		  	newElement.find('#id_deals-' + total + '-sales_item').val(vals);

			//Now that the copying of json into the cloned fields is over we create the tabs						
			var a=document.createElement('a');
		    a.setAttribute('data-toggle', 'tab');
		    var newname = '';
		    if(contact_id){
		    	//Open deal
				newname = deal_instance_name;
				//We need to populate the open_deal_id that was selected from dropdown into a hidden field. This will be later used in request.POST on server
				// to load the former open deal instance 
				//TODO: Maybe we could pass UUID of the deal and the set by json, so that we don't have to load the open_deal again in request.POST'
				newElement.find('#id_deals-' + total + '-attached_open_deal_id').attr('value', selected_id);				
			}
		    else{
		    	newname = template_name;
		    }		    	
		    
		    //The newname either template_name or instance_name will be stripped from spaces and dots and replaced with _. So that its compatible for URL id's
		    var slug =  newname.replace(/ /g,"_").replace(/\./g,"_");
		    a.setAttribute('href', '#' + slug);
		    a.innerHTML = newname;
			
			var li=document.createElement('li');
			li.appendChild(a);
			
			//Subscribing an event to this tab when it would go active in order to determine teh active tab.
			$(a).on('shown', show_tab);
		    
		    //Attaching the tab header
		    $('#attached_deals_tab').append(li);
		    
		    //creating the tab content
		    var div=document.createElement('div');
		    div.setAttribute('class', 'tab-pane');
		    
		    //Setting the id of tab content to the same url href of tab header, so that it can be found when user clicks on the tab header
		    div.setAttribute('id', slug);
		    
		    //attaching the cloned element with json values to the tab content 
		    $(div).append(newElement);
		    $('#tab-content').append(div);

			if(contact_id){
				//In case of open deal we need to remove the selected open deal from the dropdown, so it can't be added again to the same call.
				$("#id_opendeals_add_form-open_deal_template option[value='" + selected_id + "']").remove();
			}
			else{
				//In case of adding a new deal we need to remove the selected deal package from the dropdown, so it can't be added again to the same call.
				$("#id_deals_add_form-deal_template option[value='" + selected_id + "']").remove();				
			}

			//Now that everything is in place, show the tab actively								  				
			$(a).tab('show');
			
			//Now that its shown, change the m2m multi-selection field to a chosen type field. 
			$('#id_deals-' + total + '-sales_item').chosen({no_results_text: 'No results match'});
			
			//Finally set the total form value within the formset to the number of added tabs, so that it can be saved in request.POST 
			total = $('#attached_deals_tab li').length;
    		$('#id_' + type + '-TOTAL_FORMS').attr('value', total);
		  }		  
		});	
}



function add_deals(event){
	//Adding new deals
	event.preventDefault();
	var type = 'deals';
	var newElement = cloneMore('#X table', type);
	
	//Getting the deal package id from the selected dropdown
	var selected_id = $('#id_deals_add_form-deal_template option:selected').val()
	if (selected_id){		
		get_deal_or_dealtemplate(selected_id, type, newElement,  '/deal_template/');		
	}
}

function add_opendeals(event){
	//Adding an open deal
	event.preventDefault();
	var type = 'deals';
	var newElement = cloneMore('#X table', type);
	
	//Getting the open deal instance id from the selected dropdown
	var selected_id = $('#id_opendeals_add_form-open_deal_template option:selected').val()
	var contact_id = $('#contact_id').text()
	if (selected_id){
		get_deal_or_dealtemplate(selected_id, type, newElement, '/open_deal/', contact_id);		
	}
}

function show_tab(e){
	//Uncheck all active tab checkboxes
	$('.last_active_tab').attr('checked', false);
	var current_tab_href = $(this).attr('href');
	
	//current_tab_href is the #id that the tab-header is pointing to. Hence by searching for #id we are searching within the tab content.	
	$(current_tab_href).find('.last_active_tab').attr('checked', true);	
	//now the last_actice_tab boolean is set to true of the current tab 
}

function rebind_add_deals(){
	//Upon opening make sure that all deals from attached_deal_formset will get chosenified. 
	// Attention: Do NOT chosenify the extra-deal form, or it would break.
	var total = $('#id_deals-TOTAL_FORMS').val();
	for(i=0;i<=total;i++){
		$('#id_deals-' + i + '-sales_item').chosen({no_results_text: gettext('No results match')});
	}  	
  	 
	$("#add_deals_button").click(add_deals);
	$("#add_opendeals_button").click(add_opendeals);
	
	//subscribing to an event for when tabs are clicked on, they should be made the only active-tab.
	$('a[data-toggle="tab"]').on('shown', show_tab);
	
	//If no tab is already active, then the first one found shall be made active. Otherwise the last-active-tab will be made active. 
	//Useful when there are validation errors on request.POST and we need to re-activate the previous active tab. 
	if($('#attached_deals_tab > li.active').length == 0)
		$('#attached_deals_tab a:first').tab('show');
}

$(document).ready(function () {	
	rebind_add_deals();
});