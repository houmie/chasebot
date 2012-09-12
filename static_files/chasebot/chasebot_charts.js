$(document).ready(function(){	
	
	//IE workaround for trim()
	if(typeof String.prototype.trim !== 'function') {
	  String.prototype.trim = function() {
    		return this.replace(/^\s+|\s+$/g, ''); 
  		}
	}

	
	var VEM = parseInt($('#VEM').text().trim());
	var EM = parseInt($('#EM').text().trim());
	var LM = parseInt($('#LM').text().trim());
	var EA = parseInt($('#EA').text().trim());
	var LA = parseInt($('#LA').text().trim());
	var EE = parseInt($('#EE').text().trim());
	var LE = parseInt($('#LE').text().trim());	
	
  var data = [
    ['Very Early Morning 0:00 AM - 5:59 AM', VEM],
    ['Early Morning 6:00 AM - 8:59 AM', EM],['Late Morning 9:00 AM - 11:59 AM', LM], ['Early Afternoon 12:00 PM - 2:59 PM', EA],
    ['Late Afternoon 3:00 PM - 5:59 PM', LA],['Early Evening 6:00 PM - 8:59 PM', EE], ['Late Evening 9:00 PM - 23:59 PM', EE]
  ];
  var plot1 = jQuery.jqplot ('chartdiv', [data],
    {
      seriesDefaults: {
        // Make this a pie chart.
        renderer: jQuery.jqplot.PieRenderer,
        rendererOptions: {
          // Put data labels on the pie slices.
          // By default, labels show the percentage of the slice.
          showDataLabels: true
        }
      },
      legend: { show:true, location: 'e' }
    }
  );
});