var map;
var marker;
var infowindow

function toTable(locations, verbose=false) {
  var tbl = document.createElement('table');
  var tbdy = document.createElement('tbody');
  for( var i=0; i<locations.length; i++ ) {
    var tr = document.createElement('tr');
    for ( var j=0; j<locations[i].length; j++ ) {
      var td = document.createElement('td');
      td.appendChild(document.createTextNode(locations[i][j]))
      tr.appendChild(td)
    }
    tbdy.appendChild(tr);
    if( verbose ) console.log( locations[i] );
  }
  tbl.appendChild(tbdy);
  return tbl;
}


function initMap() {
  if( DEBUG ) {
    table = toTable( locations );
    document.getElementById('locations').appendChild( table );
  }
  center = locations[0]
  map = new google.maps.Map(document.getElementById('map'), {
    zoom: 10,
    scaleControl: true,
    center: new google.maps.LatLng(center[1], center[2]),
    mapTypeId: google.maps.MapTypeId.ROADMAP
  });
  
  infowindow = new google.maps.InfoWindow();
  
  var i;
  
  for (i = 0; i < locations.length; i++) {  
    marker = new google.maps.Marker({
      position: new google.maps.LatLng(locations[i][1], locations[i][2]),
      map: map
    });
  
    google.maps.event.addListener(marker, 'click', (function(marker, i) {
      return function() {
        infowindow.setContent(locations[i][0]);
        infowindow.open(map, marker);
      }
    })(marker, i));
  }
}