$.chasebot_dp = {}
$.chasebot_dp.locale = '';

$(document).ready(function () {		
	// $.chasebot_dp.locale = 'dd/mm/yyyy';
	$('.datepicker')
    	.datepicker({    		
    		format: $('#locale').text(),
    		autoclose: 'True'
		});	
});

