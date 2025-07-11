(function() {

	window.onload = function() {

		// Creating a new map
		var map = new google.maps.Map(document.getElementById("map-canvas"), {
           center: new google.maps.LatLng(25.3554592,51.4441797),
      styles: [{"featureType":"administrative","elementType":"labels.text.fill","stylers":[{"color":"#444444"}]},{"featureType":"landscape","elementType":"all","stylers":[{"color":"#f2f2f2"}]},{"featureType":"poi","elementType":"all","stylers":[{"visibility":"off"}]},{"featureType":"road","elementType":"all","stylers":[{"saturation":-100},{"lightness":45}]},{"featureType":"road.highway","elementType":"all","stylers":[{"visibility":"simplified"}]},{"featureType":"road.arterial","elementType":"labels.icon","stylers":[{"visibility":"off"}]},{"featureType":"transit","elementType":"all","stylers":[{"visibility":"off"}]},{"featureType":"water","elementType":"all","stylers":[{"color":"#9bc1d4"},{"visibility":"on"}]}],
             
          zoom: 10,
            
          mapTypeId: google.maps.MapTypeId.ROADMAP
        });
   
		// Creating the JSON data
		var json = [
		    {
		         "id": 878,
        "name": "Magic Tours",
        "address": "FBA complex Al Ithihad Street, Near Qmall, Al Gharafa",
//        "workingDays": "Daily",
//        "businessHours": "7:30AMâ€“10:30PM",
        "latitude": "25.3269638",
        "longitude": "51.4606136",
        "lang": "ENGLISH"
    }, {
        "id": 879,
        "name": "Magic Tours",
        "address": "Commercial Street, Birakat Al Awamir, Al Wakrah",
//        "workingDays": "Daily",
//        "businessHours": "7:30AMâ€“10:30PM",
        "latitude": "25.080308",
        "longitude": "51.473457",
        "lang": "ENGLISH"
    }];

		

		// Creating a global infoWindow object that will be reused by all markers
		var infoWindow = new google.maps.InfoWindow();

		// Looping through the JSON data
		for (var i = 0, length = json.length; i < length; i++) {
			var data = json[i],
				latLng = new google.maps.LatLng(data.latitude, data.longitude);

			// Creating a marker and putting it on the map
			 var marker = new google.maps.Marker({
      position: new google.maps.LatLng(data.latitude,data.longitude),
      map: map,
        animation: google.maps.Animation.DROP,
        icon: 'assets/img/map-marker.png', // null = default icon
      title:data.name,// this works, giving the marker a title with the correct title
     
       
    });


			// Creating a closure to retain the correct data, notice how I pass the current data in the loop into the closure (marker, data)
			(function(marker, data) {

				// Attaching a click event to the current marker
				google.maps.event.addListener(marker, "click", function(e) {
					infoWindow.setContent("<h1>"+data.name+"</h1>"+ "<br>"+data.address);
					infoWindow.open(map, marker);
				});


			})(marker, data);

		}

	}

})();