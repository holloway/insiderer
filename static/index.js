(function(){
  "use strict";

  var files    = document.getElementById("files");
  var response = document.getElementById("response");
  var loading  = document.getElementById("loading");
  var form     = document.getElementsByTagName("form")[0];

  window.onunload = function(){}; //prevent caching when going back to page

  if(window.location.hash.replace(/^#/, '') === "loading"){
    loading.classList.remove("show");
    window.location.hash = "";
  };

  files.addEventListener("change", function(){
    if(files.value.length === 0) return;
    loading.classList.add("show");
		window.location.hash = "loading";
    setTimeout(function(){
      var formdata = new FormData(form),
          ajax = new XMLHttpRequest();
      ajax.open("POST", "/", true);
      ajax.onload = function(event, second) {
        var metadata;
        loading.classList.remove("show");
        try {
          metadata = JSON.parse(this.responseText);
        } catch(e){
          alert(html2text(this.responseText));
        }       
        renderResponse(metadata);
      }
      ajax.send(formdata);
    }, 500);
  });

  var html2text = function(html){
    if(html.indexOf("<body") >= 0){
      html = html.substr(html.indexOf("<body"));
      html = html.substr(html.indexOf(">") + 1);
    }
    return html.replace(/\<.*?\>/g, '');
  }

  var renderResponse = function(metadatas){
    while (response.firstChild) {
      response.removeChild(response.firstChild);
    }
    var i, metadata, li, div, h1, rawJson, stringified;
    for(i = 0; i < metadatas.length; i++){
      metadata = metadatas[i];
      li = document.createElement("li");
      div = document.createElement("div");
      h1 = document.createElement("h1");
      div.style.background = "white url('mimetypeicon?mimetype=" + encodeURIComponent(metadata.mimetype) + "') no-repeat 14px 10px"
      div.style.backgroundSize = "30px"
      h1.style.paddingLeft = "35px"
      rawJson = document.createElement("pre");
      h1.textContent = metadata.filename;
      stringified = JSON.stringify(metadata, null, 2);
      rawJson.textContent = stringified;
      div.appendChild(h1);
      div.appendChild(rawJson);
      li.appendChild(div);
      response.appendChild(li);
    }
  }

}())

