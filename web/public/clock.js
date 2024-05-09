var urlParams;
(function () {
    var match,
        pl     = /\+/g,  // Regex for replacing addition symbol with a space
        search = /([^&=]+)=?([^&]*)/g,
        decode = function (s) { return decodeURIComponent(s.replace(pl, " ")); },
        query  = window.location.search.substring(1);
    urlParams = {};
    while (match = search.exec(query))
       urlParams[decode(match[1])] = decode(match[2]);
})();

if (urlParams["style"]) output.setAttribute("style", urlParams["style"]);
if (urlParams["bodyStyle"]) document.body.setAttribute("style", urlParams["bodyStyle"]);
if (urlParams["video"]){ 
  video = urlParams["video"];
  console.log(video);
}
if (urlParams["seek"]){
  seek = urlParams["seek"];
  console.log(seek);
}

var output = document.getElementById("clock");

var c;
setInterval(
c = function() {
	output.innerText = moment().format(urlParams["format"] || 'DD/MM/YYYY HH:mm:ss');
//	$("#clock").load(" #clock > *");

//    output.innerText = moment().format(urlParams["format"] || '');
}, 1000);
c();

var secondselapsed = document.getElementById("secondselapsed");
startc = moment()
var se;
setInterval(
se = function() {
    endc = moment()
	secondselapsed.innerText = (endc - startc)/1000;
//	$("#secondselapsed").load(" #secondselapsed > *");
	
//    output.innerText = moment().format(urlParams["format"] || '');
}, 1000);
se();


