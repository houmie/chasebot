$.chasebot = {};
$.chasebot.deal_id = 0;
$.chasebot.hidden_deal_ids = [];


function SortByValue(x, y){   
  return ((x < y) ? -1 : ((x > y) ? 1 : 0));
}



function add_deals(e){	
	if($.chasebot.hidden_deal_ids.length > 0)
	{		
		$('#tr_' + $.chasebot.hidden_deal_ids[0]).attr({'class':''});	
		$('#id_deal_show_row_' + $.chasebot.hidden_deal_ids[0]).prop("checked", true);
		$.chasebot.hidden_deal_ids.splice( $.inArray($.chasebot.hidden_deal_ids[0], $.chasebot.hidden_deal_ids), 1 );				
	}
	if($.chasebot.hidden_deal_ids.length == 0)	
		$('#add_deals_button').attr({'class': 'btn btn-success disabled'})
}

function cloneMore(selector, type) {
    var newElement = $(selector).clone(true);
    //var total = $('#id_' + type + '-TOTAL_FORMS').val();
    var total = $(selector).length;
    
    newElement.find(':input').each(function() {
        var name = $(this).attr('name').replace('extra_deal-' + 0 + '-', type + '-' + total + '-');
        var id = 'id_' + name;
        $(this).attr({'name': name, 'id': id});
    });
    newElement.find('label').each(function() {
        var newFor = $(this).attr('for').replace('extra_deal-' + 0 + '-', type + '-' + total + '-');
        $(this).attr('for', newFor);
    });

	newElement.find('#id_deals-' + total + '-is_form_cloned_by_ajax').prop('checked', true);
    
    total++;
    $('#id_' + type + '-TOTAL_FORMS').val(total);
    
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
				deal_instance_name = 'New Deal...';
				//$('#id_deals-' + (total-1) + '-deal_template_name').val(data[0].fields['deal_name']);
				//$('#id_deals-' + (total-1) + '-deal_instance_name').val('New Deal...');				
			}		  		  	
			else{
				template_name = data[0].fields['deal_template_name'];
				deal_instance_name = data[0].fields['deal_instance_name'];
				//$('#id_deals-' + (total-1) + '-deal_template_name').val(data[0].fields['deal_template_name']);
				//$('#id_deals-' + (total-1) + '-deal_instance_name').val(data[0].fields['deal_instance_name']);
			}
			
			newElement.find('#id_deals-' + (total-1) + '-deal_template_name').attr('value', template_name);
			newElement.find('#id_deals-' + (total-1) + '-deal_instance_name').attr('value', deal_instance_name);
		  	
		  	newElement.find('#id_deals-' + (total-1) + '-deal_description').attr('value', data[0].fields['deal_description']);
		  	newElement.find('#id_deals-' + (total-1) + '-sales_term').val(data[0].fields['sales_term']);		  			  	
		  	newElement.find('#id_deals-' + (total-1) + '-price').attr('value', data[0].fields['price']);
		  	newElement.find('#id_deals-' + (total-1) + '-quantity').attr('value', data[0].fields['quantity']);		  	
	  		
	  		if ('status' in data[0].fields)
				newElement.find('#id_deals-' + (total-1) + '-status').val(data[0].fields['status']);		  	
		  	else
		  		newElement.find('#id_deals-' + (total-1) + '-status>option:eq(1)').prop('selected', true);		  	
		  	
		  	newElement.find('#id_deals-' + (total-1) + '-deal_template').val(data[0].fields['deal_template']);
		  	var vals = [];
		  	for (i=0; i<=data[0].fields['sales_item'].length;i++)
		  		vals.push(data[0].fields['sales_item'][i]);
		  	newElement.find('#id_deals-' + (total-1) + '-sales_item').val(vals);
				// newElement.find('#id_deals-' + (total-1) + '-sales_item').val(data[0].fields['sales_item'][i]).prop("selected", true);
						
			var a=document.createElement('a');
		    a.setAttribute('data-toggle', 'tab');
		    //a.setAttribute('href', '#Deal' + (total-1));
		    var newname = '';
		    if(contact_id){
				newname = deal_instance_name;
				newElement.find('#id_deals-' + (total-1) + '-attached_open_deal_id').attr('value', selected_id);
				newElement.find('#id_deals-' + (total-1) + '-set').attr('value', data[0].fields['set']);
			}
		    else{
		    	newname = template_name;
		    	newElement.find('#id_deals-' + (total-1) + '-set').attr('value', 1);
		    }		    	
		     
		    a.setAttribute('href', '#' + newname.replace(/ /g,"_").replace(/\./g,"_"));
		    
		    //a.setAttribute('id', 'hrefDeal' + (total-1));
		    a.innerHTML = newname;
			
			var li=document.createElement('li');
			li.appendChild(a);
		    
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
					  				
			$('#attached_deals_tab a:last').tab('show');		  	
		  }		  
		});
	
	
		
	
}


function add_deals_new(event){
	event.preventDefault();
	var type = 'deals';
	var newElement = cloneMore('#X table', type);
	
	var selected_id = $('#id_deals_add_form-deal_template option:selected').val()
	if (selected_id){
		get_deal_or_dealtemplate(selected_id, type, newElement,  '/deal_template/');
	}
}

function add_opendeals_new(event){
	event.preventDefault();
	var type = 'deals';
	var newElement = cloneMore('#X table', type);
	
	var selected_id = $('#id_opendeals_add_form-open_deal_template option:selected').val()
	var contact_id = $('#contact_id').text()
	if (selected_id){
		get_deal_or_dealtemplate(selected_id, type, newElement, '/open_deal/', contact_id);
		
	}
}

function remove_deal(e){
	if($.chasebot.hidden_deal_ids.length < 5)
	{
		var tr = $(e.target).closest('tr');	
		$(tr).attr({'class':'hidden_cb'});
		var id = $(tr).attr('id').substring(3);
		$('#id_deal_show_row_' + id).prop("checked", false);
		$.chasebot.hidden_deal_ids.push(id);
		$.chasebot.hidden_deal_ids.sort(SortByValue);
		$('#add_deals_button').attr({'class': 'btn btn-success'})
	}	
}


function attach_open_deal(e){
	$('.select_status').closest('tr').find('input:checkbox').attr('checked', true);
}

$(document).ready(function () {	
	for(i=1;i<=5;i++)
	{
		if($('#id_deal_show_row_' + i).is(':checked')==false)
		{
			$.chasebot.hidden_deal_ids.push(i);
		}		
	}  
  	 
	$("#add_deals_button").click(add_deals_new);
	$("#add_opendeals_button").click(add_opendeals_new);
	// $('#attached_deals_tab').find('li[class!=hidden] a:first').tab('show');
	//var a = $('#attached_deals_tab').find('a:first');
	// if(!a.parent('li').hasClass('hidden')) {
	    // a.tab('show');
	// }
	$('#attached_deals_tab li:not(.hidden) a:first').tab('show');

	
	$('.remove_deals_button').click(remove_deal);  
  	$('.select_status').change(attach_open_deal);
});