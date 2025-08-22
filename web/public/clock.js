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
seek = 0;
if (urlParams["seek"]){
  seek = urlParams["seek"];
  console.log(seek);
}
querydate = "";
if (urlParams["date"]){ 
  querydate = urlParams["date"];
  console.log(querydate);
}

myquery = "";
if (urlParams["query"]){ 
  myquery = urlParams["query"];
  console.log(query);
}
myprompt = "";
if (urlParams["prompt"]){
  myprompt = urlParams["prompt"];
  console.log(prompt);
}
codefile = "";
if (urlParams["codefile"]){
  codefile = urlParams["codefile"];
  console.log(codefile);
}

repo = "";
if (urlParams["repo"]){
  repo = urlParams["repo"];
  console.log(repo);
}



function startClock(){
  var clockoutput = document.getElementById("clock");

  var secondselapsed = document.getElementById("secondselapsed");
  startc = moment();
  var se;
  var seeking = false;
  setInterval(
  se = function() {
      endc = moment();
      clockoutput.innerText = endc.format(urlParams["format"] || 'DD/MM/YYYY HH:mm:ss');
      secondselapsed.innerText = (endc - startc)/1000;
  //	$("#secondselapsed").load(" #secondselapsed > *");
    
  //    output.innerText = moment().format(urlParams["format"] || '');
  }, 1000);
  se();
}

if (document.getElementById("clock") !==null){
  startClock();
}
else{
  setTimeout(function(){
    //wait for page to load.  
    if (document.getElementById("clock") !==null){
      startClock();
    }
  }, 5000);
}
function str_pad_left(string,pad,length) {
  return (new Array(length+1).join(pad)+string).slice(-length);
}


//need JS to share some of this stuff.  
function getSecsFromTime(time){
	minsec = time.split(":");
	if (minsec == time)
	    return 0;
//	console.log(+parseInt(minsec[0])*60 + +parseInt(minsec[1]));
  if (minsec.length < 2)
      return 0;

	return +parseInt(minsec[minsec.length-2])*60 + +parseInt(minsec[minsec.length-1]);
	
}


function getMilliSecsFromTime(time){
	minsec = time.split(":");
	if (minsec == time)
	    return 0;
//	console.log(+parseInt(minsec[0])*60 + +parseInt(minsec[1]));
  if (minsec.length < 2)
      return 0;

	return +parseInt(minsec[minsec.length-2])*60 + +parseFloat(minsec[minsec.length-1]);
	
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
