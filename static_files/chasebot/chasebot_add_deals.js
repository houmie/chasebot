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
    var total = $('#id_' + type + '-TOTAL_FORMS').val();
    
    newElement.find(':input').each(function() {
        var name = $(this).attr('name').replace('-' + 0 + '-','-' + total + '-');
        var id = 'id_' + name;
        $(this).attr({'name': name, 'id': id}).val('').removeAttr('checked');
    });
    newElement.find('label').each(function() {
        var newFor = $(this).attr('for').replace('-' + 0 + '-','-' + total + '-');
        $(this).attr('for', newFor);
    });
    total++;
    $('#id_' + type + '-TOTAL_FORMS').val(total);
    
    var a=document.createElement('a');
    a.setAttribute('data-toggle', 'tab');
    a.setAttribute('href', '#Deal' + (total-1));
    a.innerHTML = 'Deal ' + (total-1);
	
	var li=document.createElement('li');
	li.appendChild(a);
    
    $('#attached_deals_tab').append(li);
    
    var div=document.createElement('div');
    div.setAttribute('class', 'tab-pane');
    div.setAttribute('id', 'Deal' + (total-1));
    $(div).append(newElement);
    $('#tab-content').append(div);
    $('#attached_deals_tab a:last').tab('show');
    
}


function get_deal_template(deal_template_id, type){	
	var url = '/deal_template/' + deal_template_id + '/'
	
	//Pass in the query (typed keywords) and the fieldname we are searching against 
	$.ajax({
     	  type: 'GET',
		  url: url,
		  // data: { query: query, fieldname: fieldname },		  
		  contentType: "application/json; charset=utf-8",
		  dataType: 'json',
		  success: function (data) {		  	
		  	var total = $('#id_' + type + '-TOTAL_FORMS').val();		  	
		  	$('#id_deals-' + (total-1) + '-deal_template_name').val(data[0].fields['deal_name']);		  	
		  	$('#id_deals-' + (total-1) + '-deal_description').val(data[0].fields['deal_description']);
		  	$('#id_deals-' + (total-1) + '-sales_term>option:eq(' + data[0].fields['sales_term'] + ')').prop('selected', true);		  			  	
		  	$('#id_deals-' + (total-1) + '-price').val(data[0].fields['price']);
		  	$('#id_deals-' + (total-1) + '-quantity').val(data[0].fields['quantity']);
		  	$('#id_deals-' + (total-1) + '-status>option:eq(1)').prop('selected', true);
		  	$('#id_deals-' + (total-1) + '-deal_template>option:eq(' + deal_template_id + ')').prop('selected', true);
		  	for (i=0; i<data[0].fields['sales_item'].length;i++)
				$('#id_deals-' + (total-1) + '-sales_item>option:eq(' + (data[0].fields['sales_item'][i]-1) + ')').prop('selected', true);		  		
		  	$("#id_deals_add_form-deal_template option[value='" + deal_template_id + "']").remove();
		  	
		  }		  
		});
}


function add_deals_new(event){
	event.preventDefault();
	var type = 'deals';
	cloneMore('#X table', type);
	
	var selected_template_id = $('#id_deals_add_form-deal_template option:selected').val()
	if (selected_template_id){
		get_deal_template(selected_template_id, type);
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
	// $('#attached_deals_tab').find('li[class!=hidden] a:first').tab('show');
	var a = $('#attached_deals_tab').find('a:first');
	if(!a.parent('li').hasClass('hidden')) {
	    a.tab('show');
	}
	
	$('.remove_deals_button').click(remove_deal);  
  	$('.select_status').change(attach_open_deal);
});