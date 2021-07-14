function filesize(elem) {
    var output = document.getElementById('output');
    // var filename = document.getElementById('filename')
    var fileName = document.getElementById('image-input');
            //replace the "Choose a file" label
    // $(this).next('.custom-file-label').html(fileName);
    // console.log(fileName.value + " aaaaa")
    let file = fileName.value.split(/(\\|\/)/g).pop()
    // TODO use sibling 
    document.querySelector('.custom-file-label').innerHTML = file

    output.src = URL.createObjectURL(event.target.files[0]);
    output.onload = function() {
      URL.revokeObjectURL(output.src) // free memory
    }
    document.cookie = `filesize=${elem.files[0].size}`;
  }