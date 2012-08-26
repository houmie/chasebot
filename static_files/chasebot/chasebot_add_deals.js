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
  	 
	$("#add_deals_button").click(add_deals)
	$('.remove_deals_button').click(remove_deal)  
  	$('.select_status').change(attach_open_deal)
});