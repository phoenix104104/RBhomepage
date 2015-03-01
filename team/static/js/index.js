$(document).ready(function() {

	$('.navbar-fixed-top').addClass('opaque');
	$(window).scroll(function() {
        if($(this).scrollTop() < 300) {
            $('.navbar-fixed-top').addClass('opaque');
	    } else {
            $('.navbar-fixed-top').removeClass('opaque');
        }
    });
});
// google-map API
function initialize() {
	var myLatlng = new google.maps.LatLng(25.068230, 121.569206);
	var mapOptions = {
		zoom: 15,
		center: myLatlng
	}
	var map = new google.maps.Map(document.getElementById('googleMap'), mapOptions);

	var marker = new google.maps.Marker({
		position: myLatlng,
		map: map,
		title: 'Hello World!'
	});
}

google.maps.event.addDomListener(window, 'load', initialize);