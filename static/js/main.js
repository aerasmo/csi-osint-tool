if ( window.history.replaceState ) {
  window.history.replaceState( null, null, window.location.href );
}


function filesize(elem) {
    var output = document.getElementById('output');
    var fileName = document.getElementById('image-input');
    

    output.classList.remove('default')
    let file = fileName.value.split(/(\\|\/)/g).pop()
    document.getElementById('uploaded-image-text').innerHTML = 'Uploaded Image'
    // TODO use sibling 
    document.querySelector('.custom-file-label').innerHTML = file

    output.src = URL.createObjectURL(event.target.files[0]);
    output.onload = function() {
      URL.revokeObjectURL(output.src) // free memory
    }
    document.cookie = `filesize=${elem.files[0].size}`;
}

