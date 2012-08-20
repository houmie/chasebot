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


$.chasebot = {};
$.chasebot.deal_id = 0;
$.chasebot.hidden_deal_ids = [];


// function deal_edit_func(e) {
  // var item = $('#deal_status tbody')
  // //var selected = $(e.target).val();  
  // var selected = $("#id_deals option:selected");   
  // item.empty();
//   
  // var new_row = $('<tr />');
  // var column_left = $('<td />');
  // var column_right = $('<td />');
//     
  // var title = $('<p />').text("Deal Status:");
  // column_left.append(title);
//   
  // new_row.append(column_left);
  // new_row.append(column_right);
//   
  // item.append(new_row);
//   
  // $.each(selected, function(index, object){
  	// var new_row = $('<tr />');
  	// var column_left = $('<td />');
  	// var column_right = $('<td />');  	
//   	
  	// column_left.append($('<p />').text(object.text + ':'));
//   	
  	// var dropdown = create_dropdown(object);  	
	// column_right.append(dropdown);
// 	
	// new_row.append(column_left);
	// new_row.append(column_right);
// 	
	// item.append(new_row);
  // }); 
//  
  // return false;
// }

function SortByValue(x, y){   
  return ((x < y) ? -1 : ((x > y) ? 1 : 0));
}



function add_deals(e){	
	// $('#id_deal_' + $.chasebot.deal_id).attr({'class':'non_hidden'});
	// $('#id_status_' + $.chasebot.deal_id).attr({'class':'non_hidden'});
	// $('#remove_deals_button_' + $.chasebot.deal_id).attr({'class':'btn btn-danger remove_deals_button'});
	if($.chasebot.hidden_deal_ids.length > 0)
	{		
		$('#tr_' + $.chasebot.hidden_deal_ids[0]).attr({'class':''});	
		$('#id_deal_show_row_' + $.chasebot.hidden_deal_ids[0]).prop("checked", true);
		$.chasebot.hidden_deal_ids.splice( $.inArray($.chasebot.hidden_deal_ids[0], $.chasebot.hidden_deal_ids), 1 );				
	}
	if($.chasebot.hidden_deal_ids.length == 0)	
		$('#add_deals_button').attr({'class': 'btn btn-success disabled'})
}

function remove_deal(e){		
	// $('#id_deal_' + $.chasebot.deal_id).attr({'class':'hidden_cb'});
	// $('#id_status_' + $.chasebot.deal_id).attr({'class':'hidden_cb'});
	// $('#remove_deals_button_' + $.chasebot.deal_id).attr({'class':'btn btn-danger remove_deals_button hidden_cb'});
	// $.chasebot.deal_id--;
	// for(i=0; i<=1; i++)	{
		// var t = $(e.target).parent().parent().find('td select')[i];
		// $(t).attr({'class':'hidden'});	
	// }
	if($.chasebot.hidden_deal_ids.length < 5)
	{
		var tr = $(e.target).closest('tr');
		
		// if($.chasebot.hidden_deal_ids.length == 5)
			// $(tr).attr({'class':'hidden_cb'});
		// else
		$(tr).attr({'class':'hidden_cb'});
		//$(e.target).attr({'class':'btn btn-danger remove_deals_button hidden'});
		var id = $(tr).attr('id').substring(3);
		$('#id_deal_show_row_' + id).prop("checked", false);
		$.chasebot.hidden_deal_ids.push(id);
		$.chasebot.hidden_deal_ids.sort(SortByValue);
		$('#add_deals_button').attr({'class': 'btn btn-success'})
	}	
}


function add_deals_old(e){
	
	var nr_possible_deals = $('#hidden_deals > option').size()
	var nr_selected_deals = $('#deals tbody > tr').size() - 2;
	
	if(max_deals_reached() ||  (nr_selected_deals == nr_possible_deals))
	{		
		return false;
	}	
	
	$.chasebot.deal_id++;
	
	$('#hidden_deal_elements').attr({'class':'hidden'});
		
	var deal = $('#hidden_deals').clone();
	deal.removeAttr('id');
	deal.removeAttr('class');
	deal.attr({'name': 'deal_XX' + $.chasebot.deal_id})	 	
	
	var tr = $('<tr />');
	$('#deals tbody').append(tr);	
	
	var td = $('<td />');
	tr.append(td);
	td.append(deal);
	
	var statuses = $('#hidden_deal_statuses').clone();
	statuses.removeAttr('id');
	statuses.removeAttr('class');
	statuses.attr({'name': 'dealstatus_XX' + $.chasebot.deal_id})
	
	var td = $('<td />');
	tr.append(td);
	td.append(statuses);
	
	var remove_button = $('#remove_deals_button').clone();
	remove_button.attr({'class': 'btn btn-danger'});
	
	remove_button.click(remove_deal)
	
	var td = $('<td />');
	tr.append(td);
	td.append(remove_button);
		
	if(max_deals_reached() || (nr_selected_deals + 1 == nr_possible_deals))
	{
		$('#add_deals_button').attr({'class': 'btn btn-success disabled'})		
	}

		 
}

function max_deals_reached(){
	if($('#deals tbody > tr').size() == 8)
		return true;
	else
		return false;
}

function min_deals_reached(){
	if($('#deals tbody > tr').size() == 2)
		return true;
	else
		return false;
}

function remove_deal_old(e){
	$(e.target).parent().parent().remove()
	$('#add_deals_button').attr({'class': 'btn btn-success'})		
		
	if(min_deals_reached())
	{
		$('#hidden_deal_elements').attr({'class':'hidden_cb'});		
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
  	 
	$("#add_deals_button").click(add_deals)
	$('.remove_deals_button').click(remove_deal)
  
  	$('.select_status').change(attach_open_deal)
  	
  // if(max_deals_reached())
  // {
  	// $('#add_deals_button').attr({'class': 'btn btn-success disabled'})  	
  // }
  // else if($('#deals tbody > tr').size() > 2)
  // {  	
	// $('#hidden_deal_elements').attr({'class':'hidden'});
  // }
});