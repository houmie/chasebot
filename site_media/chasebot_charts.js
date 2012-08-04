$(document).ready(function(){	
	
	var EM = parseInt($('#EM').text().trim());
	var LM = parseInt($('#LM').text().trim());
	var EA = parseInt($('#EA').text().trim());
	var LA = parseInt($('#LA').text().trim());
	var EE = parseInt($('#EE').text().trim());	
	
  var data = [
    ['Early Morning 6:00 AM - 8:59 AM', EM],['Late Morning 9:00 AM - 11:59 AM', LM], ['Early Afternoon 12:00 PM - 2:59 PM', EA],
    ['Late Afternoon 3:00 PM - 5:59 PM', LA],['Early Evening 6:00 PM - 8:59 PM', EE]
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