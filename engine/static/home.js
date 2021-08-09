
function addOptions() {
    var select = document.getElementById("select_landmark");
    for( var i=0; i<landmarks.length; i++ ) {
        var option = document.createElement("option");
        option.text = landmarks[i][0];
        option.value = i;
        select.appendChild( option );
    }

    var select = document.getElementById("select_body");
    for( var i=0; i<bodies.length; i++ ) {
        var option = document.createElement("option");
        option.text = bodies[i]
        option.value = i;
        select.appendChild( option );
    }
}
  
window.onload = function() {
    addOptions();
    document.getElementById('datePicker').valueAsDate = new Date();
    document.getElementById("defaultOpen").click();
};