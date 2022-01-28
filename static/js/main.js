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

    // filt.style.display = "block";

    document.cookie = `filesize =${elem.files[0].size}`;
}
