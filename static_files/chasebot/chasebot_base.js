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


function row_delete() {
    if (confirm($('#delete_button_confirmation').text())) {
    	var url = $(this).attr("href") + "/";
    	//e.g. get whole row to be removed
  		var row = $(this).closest('tr').empty();
  		
        $.post(url, function(){
        	alert('OK');
        });
        row.remove();        
    }
    return false;
}


function filter_rows(){
	var url = window.location.pathname;		
	
	//'?' found means dirty url		
	if(url.indexOf('?') != -1) {
		//Make Url clean (copy bit before ?)
		url = url.substring(url.indexOf('?'));
	}
	// With ajax as first keywork we can check against in views.py and refresh the list if all filters are cleared but the request came by ajax
	url = url + '?ajax' 
	 
	//Check each input box for values and apply keyword search 
	$('.filter_button').parent().children('input').each(function(i, v){			
		//id_last_name -> last_name
		var keyword = $(v).attr('id').substring(3);
		
		//Only if it contains any value in the field, attach it to the url GET, otherwise its pointless		
		if($(v).val() != ''){			
			url = url + '&' + keyword + '=' + $(v).val();			
		}				 		
	})
	//Even if no filter are set, still the query to server is required to get all list and undo filters.	
	$('#search_result').load(url, function(){		
		$(".row_delete").click(row_delete);	
	});	
	
	return false;
}

$(document).ready(function () {	
	$(".row_delete").click(row_delete);	
	$(".filter_button").click(filter_rows);		
});