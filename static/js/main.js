if ( window.history.replaceState ) {
  window.history.replaceState( null, null, window.location.href );
}

//Refresh
if (performance.navigation.type == performance.navigation.TYPE_RELOAD) {
  // alert("refresh button is clicked");
  document.location.href="/";

}    

function truncate(str, n){
  return (str.length > n) ? str.substr(0, n-1) + '&hellip;' : str;
};

function filesize(elem) {
    console.log("changing")
    var output = document.querySelector('.uploaded');
    var fileName = document.querySelector('#image-input');
    var submit = document.querySelector('#submit-image');
    var main = document.querySelector('#content');
    var inps = document.querySelector('#inputs');

    output.classList.remove('default');
    inps.classList.remove("d-none");
    inps.classList.add("d-block");

    submit.disabled = false;
    let file = fileName.value.split(/(\\|\/)/g).pop()
    // document.getElementById('uploaded-image-text').innerHTML = 'Uploaded Image'
    // document.querySelector('.custom-label').innerHTML = `${truncate(file, 30)}`

    output.src = URL.createObjectURL(event.target.files[0]);
    output.onload = function() {
      URL.revokeObjectURL(output.src) // free memory
    }

    main.style.display = "none";
    // filt.style.display = "block";

    document.cookie = `filesize =${elem.files[0].size}`;
    // document.cookie = `filename =${elem.files[0].size}`;
}

jQuery(document).ready(function($){
  
  $('.zoom-image img').click(function(event){
    var ix = $(this).offset().left;
    var iy = $(this).offset().top;
    console.log(ix + '-' + iy);
    
      var mx = event.pageX;
      var my = event.pageY;
    console.log(mx + '-' + my);
  })

  $('.zoom-image img').hover(function(){

    var img = $(this).attr('src');

    $(this).after("<div class='hover-image' style='background-image: url(" + img + "); background-size: 1200px;'></div>");

    $(this).mousemove(function(event){

      // Mouse Position
      var mx = event.pageX;
      var my = event.pageY;

      // Image Position
      var ix = $(this).offset().left;
      var iy = $(this).offset().top;

      // Mouse Position Relavtive to Image
      var x = mx - ( ix );
      var y = my - ( iy );

      // Image Height and Width
      var w = $(this).width();
      var h = $(this).height();

      // Mouse Position Relative to Image, in %
      var xp = ( -x / w ) * -100;
      var yp = ( -y / h ) * -100;

      $(this).parent().find('.hover-image').attr('style',

      "background-image: url(" + img + "); background-size: 1200px; background-repeat: no-repeat; background-position: " + xp + "% " + yp + "%; top: " + y + "px; left: " + x + "px;");

    });

  }, function(){

    $(this).parent().find('.hover-image').remove();

  });

});
