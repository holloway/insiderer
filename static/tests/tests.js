(function(){
  "use strict";

  window.onunload = function(){}; //prevent caching when going back to page

  var http_get_json = function(url, callback){
    var ajax = new XMLHttpRequest();
    ajax.open("GET", url, true);
    ajax.onload = function(response, e){
      callback(JSON.parse(this.responseText))
    }
    ajax.send();
  };

  var OneEightyT = function(template, dict) {
    var value, div = document.createElement("div");
    return template.replace(/{(.*?)}/g, function(a, key) {
        value = dict[key];
        div.textContent = value;
        return typeof value == "function" ? value() : div.innerHTML
    })
  };

  var runAllTestsButton = document.getElementById("runAllTests").getElementsByTagName("button")[0];
  var results = document.getElementById("results");

  runAllTestsButton.addEventListener("click", function(){
    var buttons = results.getElementsByTagName("button"), i;
    for(i = 0; i < buttons.length; i++){
      setTimeout(function(i){
        return function(){
          var button = buttons[i],
              event  = document.createEvent("MouseEvents");
          event.initEvent("click", true, true);
          event.synthetic = true;
          button.dispatchEvent(event, true);
        }
      }(i), i * 500);
    } 
  })



  results.addEventListener("click", function(event){
    var currentNode = event.target;
    while(currentNode.previousSibling){
      currentNode = currentNode.previousSibling;
    };
    http_get_json(currentNode.textContent, compareResults);
  });

  var compareResults = function(result){
    var filename = result.filename;
    var buttonFilename = document.getElementById(filename);
    buttonFilename.className = ""
    var actual   = JSON.parse(result.actual);
    var expected = JSON.parse(result.expected);
    var actual_norm = JSONc14n.stringify(actual);
    var expected_norm = JSONc14n.stringify(expected);
    if(actual_norm !== expected_norm){
      console.log(actual_norm)
      console.log(expected_norm)
      buttonFilename.className = "fail";
      buttonFilename.textContent = "Test Fail :(";
    } else {
      buttonFilename.className = "pass";
      buttonFilename.textContent = "Test Pass!";
    }
  }
 
  http_get_json("/tests/list", function(list){
    for(var i = 0; i < list.length; i++){
      results.innerHTML += OneEightyT(
        '<li><span>{name}</span> <button id="{name}">Test</button></li>',
        {name: list[i]}
      );
    }
  });


}())
