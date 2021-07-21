if ( window.history.replaceState ) {
  window.history.replaceState( null, null, window.location.href );
  // file nasa cookie 
  // delete foldername
  // window.location.href = "./";
  // document.location.href="/";
}
// upload -> change state delete upload -> upload[ post req] 
// output page -> 

  // Use getEntriesByType() to just get the "navigation" events
// var perfEntries = performance.getEntriesByType("navigation");

// for (var i=0; i < perfEntries.length; i++) {
//   console.log("= Navigation entry[" + i + "]");
//   var p = perfEntries[i];
//   // dom Properties
//   console.log("DOM content loaded = " + (p.domContentLoadedEventEnd - p.domContentLoadedEventStart));
//   console.log("DOM complete = " + p.domComplete);
//   console.log("DOM interactive = " + p.interactive);

//   // document load and unload time
//   console.log("document load = " + (p.loadEventEnd - p.loadEventStart));
//   console.log("document unload = " + (p.unloadEventEnd - p.unloadEventStart));

//   // other properties
//   console.log("type = " + p.type);
//   console.log("redirectCount = " + p.redirectCount);
// }

//Refresh
if (performance.navigation.type == performance.navigation.TYPE_RELOAD) {
  // alert("refresh button is clicked");
  document.location.href="/";
  // redirect to path na nagdedelete

  // /delete/foldername

  // redirect to home/
  //delete output
  //delete upload
}    

function filesize(elem) {
    var output = document.getElementById('output');
    var fileName = document.getElementById('image-input');
    

    output.classList.toggle('default')
    let file = fileName.value.split(/(\\|\/)/g).pop()
    document.getElementById('uploaded-image-text').innerHTML = 'Uploaded Image'
    document.querySelector('.custom-file-label').innerHTML = file

    output.src = URL.createObjectURL(event.target.files[0]);
    output.onload = function() {
      URL.revokeObjectURL(output.src) // free memory
    }
    document.cookie = `filesize =${elem.files[0].size}`;
    // document.cookie = `filename =${elem.files[0].size}`;
}

