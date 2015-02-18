(function(){
  "use strict";

  var files = document.getElementById("files");
  var loading = document.getElementById("loading");
  var form = document.getElementsByTagName("form")[0];
  window.onunload = function(){};

  if(window.location.hash.replace(/^#/, '') === "loading"){
    loading.classList.remove("show");
    window.location.hash = "";
  };

  files.addEventListener("change", function(){
    loading.classList.add("show");
		window.location.hash = "loading";
    setTimeout(function(){
      form.submit();
    }, 500);
  });

}())
