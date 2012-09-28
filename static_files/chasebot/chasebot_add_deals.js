function cloneMore(selector, type) {
    var newElement = $(selector).clone(true);
    var total = $('#id_' + type + '-TOTAL_FORMS').val();
    
    //.default is the class for chosen behind the scenes input element. 
    //This needs to be excluded as its irrelevent to formset and causes js to break otherwise. 
    newElement.find(':input:not(.default)').each(function() {
        var name = $(this).attr('name').replace('extra_deal-' + 0 + '-', type + '-' + total + '-');
        var id = 'id_' + name;
        $(this).attr({'name': name, 'id': id});
    });
    newElement.find('label').each(function() {
        var newFor = $(this).attr('for').replace('extra_deal-' + 0 + '-', type + '-' + total + '-');
        $(this).attr('for', newFor);
    });    
    return newElement;
}


function get_deal_or_dealtemplate(selected_id, type, newElement, path, contact_id){	
	
	var url = '';
	if(contact_id == null || contact_id == ''){
		url = path + selected_id + '/';
	}
	else{
		url = path + selected_id + '/' + contact_id;
	}
		
	$.ajax({
     	  type: 'GET',
		  url: url,
		  // data: { query: query, fieldname: fieldname },		  
		  contentType: "application/json; charset=utf-8",
		  dataType: 'json',
		  success: function (data) {		  	
		  	var total = $('#id_' + type + '-TOTAL_FORMS').val();
		  	
		  	var template_name = '';
		    var deal_instance_name = '';
		  	
			if(contact_id == null || contact_id == ''){
				template_name = data[0].fields['deal_name'];
				deal_instance_name = gettext('To be set after saving...');
			}		  		  	
			else{
				template_name = data[0].fields['deal_template_name'];
				deal_instance_name = data[0].fields['deal_instance_name'];
			}
			
			newElement.find('#id_deals-' + total + '-deal_template_name').attr('value', template_name);
			newElement.find('#id_deals-' + total + '-deal_instance_name').attr('value', deal_instance_name);
		  	
		  	newElement.find('#id_deals-' + total + '-deal_description').attr('value', data[0].fields['deal_description']);
		  	newElement.find('#id_deals-' + total + '-sales_term').val(data[0].fields['sales_term']);		  			  	
		  	newElement.find('#id_deals-' + total + '-price').attr('value', data[0].fields['price']);
		  	newElement.find('#id_deals-' + total + '-quantity').attr('value', data[0].fields['quantity']);		  	
	  		
	  		if ('status' in data[0].fields)
				newElement.find('#id_deals-' + total + '-status').val(data[0].fields['status']);		  	
		  	else
		  		newElement.find('#id_deals-' + total + '-status>option:eq(1)').prop('selected', true);		  	
		  	
		  	if('deal_template' in data[0].fields)
		  		newElement.find('#id_deals-' + total + '-deal_template').val(data[0].fields['deal_template']);
		  	else
		  		newElement.find('#id_deals-' + total + '-deal_template').val(data[0].pk);
		  	var vals = [];
		  	for (i=0; i<=data[0].fields['sales_item'].length;i++)
		  		vals.push(data[0].fields['sales_item'][i]);
		  	newElement.find('#id_deals-' + total + '-sales_item').val(vals);
						
			var a=document.createElement('a');
		    a.setAttribute('data-toggle', 'tab');
		    var newname = '';
		    if(contact_id){
				newname = deal_instance_name;
				newElement.find('#id_deals-' + total + '-attached_open_deal_id').attr('value', selected_id);
				newElement.find('#id_deals-' + total + '-set').attr('value', data[0].fields['set']);
			}
		    else{
		    	newname = template_name;
		    }		    	
		     
		    a.setAttribute('href', '#' + newname.replace(/ /g,"_").replace(/\./g,"_"));
		    a.innerHTML = newname;
			
			var li=document.createElement('li');
			li.appendChild(a);
			
			$(a).on('shown', show_tab);
		    
		    $('#attached_deals_tab').append(li);
		    
		    var div=document.createElement('div');
		    div.setAttribute('class', 'tab-pane');
		    div.setAttribute('id', newname.replace(/ /g,"_").replace(/\./g,"_"));
		    $(div).append(newElement);
		    $('#tab-content').append(div);

			if(contact_id == null || contact_id == '')
				$("#id_deals_add_form-deal_template option[value='" + selected_id + "']").remove();
			else
				$("#id_opendeals_add_form-open_deal_template option[value='" + selected_id + "']").remove();
					  				
			$(a).tab('show');
			$('#id_deals-' + total + '-sales_item').chosen({no_results_text: 'No results match'});
			
			total = $('#attached_deals_tab li').length;
    		$('#id_' + type + '-TOTAL_FORMS').attr('value', total);
		  }		  
		});	
}



function add_deals(event){
	event.preventDefault();
	var type = 'deals';
	var newElement = cloneMore('#X table', type);
	
	var selected_id = $('#id_deals_add_form-deal_template option:selected').val()
	if (selected_id){
		get_deal_or_dealtemplate(selected_id, type, newElement,  '/deal_template/');		
	}
}

function add_opendeals(event){
	event.preventDefault();
	var type = 'deals';
	var newElement = cloneMore('#X table', type);
	
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
	//Check current active tab as active tab
	$(current_tab_href).find('.last_active_tab').attr('checked', true);	
}

$(document).ready(function () {	
	var total = $('#id_deals-TOTAL_FORMS').val();
	for(i=0;i<=total;i++){
		$('#id_deals-' + i + '-sales_item').chosen({no_results_text: gettext('No results match')});
	}  	
  	 
	$("#add_deals_button").click(add_deals);
	$("#add_opendeals_button").click(add_opendeals);
	
	$('a[data-toggle="tab"]').on('shown', show_tab);
	
	if($('#attached_deals_tab > li.active').length == 0)
		$('#attached_deals_tab a:first').tab('show');

});