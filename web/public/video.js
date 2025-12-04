//const { EvalSourceMapDevToolPlugin } = require("webpack");

var watch = false;
var player;
var player2;
var currenttranscriptentry = "";
var transcriptarray = [];
var overlays = [];
var overlayi = 0;
var lastbarcodecheck = 0;

var lastqrresult = "";
var VID_VIEW = 1;
var VID_EDIT = 2;
var VID_DETAILS = 4;

function onYouTubeIframeAPIReady() {
    player = new YT.Player('player', {
      height: '360',
      width: '640',
      videoId: video,
      playerVars: {
        'playsinline': 1
      },
      events: {
        'onReady': onPlayerReady,
        'onStateChange': onPlayerStateChange
      }
    });
  }

  // 4. The API will call this function when the video player is ready.
  function onPlayerReady(event) {
    event.target.playVideo();

    if (watch == true){
      getIterations("", 0); //get one iteration length of video.  
      getAnalyze("");
    }
    if (seek > 0){
        event.target.seekTo(seek);
    }
  }

  // 5. The API calls this function when the player's state changes.
  //    The function indicates that when playing a video (state=1),
  //    the player should play for six seconds and then stop.
  var done = false;
  function onPlayerStateChange(event) {
    if (event.data == YT.PlayerState.PAUSED || event.data == YT.PlayerState.ENDED) {
        //should use same for transcript function.  
      ispaused = 1;
    }

    if (event.data == YT.PlayerState.PLAYING) {
//          setTimeout(stopVideo, 6000);
//			console.log("state change");
        ispaused = 0;
        midioffset = 0;
        
      done = true;
    }
  }


  function pauseVideo(){
    stopVideo();
  }

  function setVideoSpeed(speed){
    if (speed > 0 && speed < 5){
      if (useyoutube || watch){
        player.setPlaybackRate(speed);
      }
      else{
          player2.playbackRate = speed;
      }
    }
  }

function setVideoVolume(volume){
    if (volume >= 0 && volume <= 1){
      if (useyoutube || watch){
        player.setVolume(volume*100); //not sure if we need *100 should be in form 0.xx already.  
      }
      else{
          player2.volume = volume;
      }
    }
  }

  function playVideo() {
    if (useyoutube || watch){
        player.playVideo();
    }
    else{
        player2.play();        
    }
  }
  
  function stopVideo() {
    if (useyoutube || watch){
        player.stopVideo();
    }
    else{
        player2.pause();        
    }
  }

  function getSecsFromTime(time){
	minsec = time.split(":");
	if (minsec == time)
	    return 0;
//	console.log(+parseInt(minsec[0])*60 + +parseInt(minsec[1]));
	return +parseInt(minsec[0])*60 + +parseInt(minsec[1]);
	
  }

  function getTimeFromSecs(time){
    var mins = Math.floor(time/60);
    if (mins < 0) mins = 0;
	  var secs = Math.floor(time - mins*60);
    if (secs < 0) secs = 0;
    var finalTime = str_pad_left(mins,'0',2)+':'+str_pad_left(secs,'0',2);
    return finalTime;
  }

  function makeTimeLinks(desc, vid=""){
    desc = desc.replaceAll("\n", "<br>");
//    desc = desc.replace(")", ")<br>");
    const regExp = /\(([^)]+)\)/g;
    regExp2 = /\d+\:\d\d?/g;
    const matches = [...desc.matchAll(regExp2)].flat();
    for (var i=0; i<matches.length; i++){
        secs = getSecsFromTime(matches[i]);
        if (secs > 0){
            desc = desc.replace(matches[i], '<a href="#" onclick="seekVideo(' + secs + ', &quot;' + vid + '&quot;);">' + matches[i] + '</a>');
        }

    }
//    console.log(matches);
    return desc;
  }

  function seekTo(seconds, v = "")
  {
    seekVideo(seconds, v);
    /*
    if (v !="" && v != video){
      video = v;
      player.loadVideoById(video);
    }
    if (player.getPlayerState() == 1) {
      player.seekTo(seconds);
    }
    else {
      ytSeconds = seconds;
      player.playVideo();
    }
    */
  }

  function getVideoWH(){
    if (useyoutube || watch){
      //not sure if this is what we want.  
      return [player.getVideoWidth(), player.getVideoHeight()]
    }
    else{
        return [player2.width, player2.height];
//        return [player2.videoWidth, player2.videoHeight];
    }
  }


  function mapToXY(x, y){
    [docwidth, docheight] = getVideoWH();
    
    let xpixel = x*docwidth/_octave;
    let ypixel = y*docwidth/_octave;
    if (xpixel > docwidth){
        xpixel = docwidth;
    }
    if (ypixel > docheight){
        ypixel = docheight;
    }
    /*
    if (xpixel < 0){
        xpixel = 0;
    }
    if (ypixel < 0){
        ypixel = 0;
    }
    */
    return [Math.round(xpixel), Math.round(ypixel)];
  }

  function highlightVideo(x, y, x1=0, y1=0){
    console.log("highlight video" + x + " " + y + " " + x1 + " " + y1);
    [x, y] = mapToXY(x, y);
    [x1, y1] = mapToXY(x1, y1);

  } 

  //from here, create new characters.  
  //need img2font function though.  And is this accurate enough.  
  //should to use the whole canvas essentially when creating chars, then that will generate smaller font sizes.  
  function addOverlay(x, y, polygon={"type": "line", "points": [ [0,0], [1,1] ]}, color='black', alpha=0.5){

    [x_, y_] = mapToXY(x, y);
    for (var pi=0; pi<polygon.points.length; pi++){
      [x, y] = mapToXY(polygon.points[pi][0], polygon.points[pi][1]);
      polygon.points[pi] = [x, y];
    }
    console.log("add overlay" + x + " " + y);
    overlays.push({"x": x_, "y": y_, "polygon": polygon, "alpha": alpha});

  }

  function scanQR(id='qrscreen'){

    const canvas = document.getElementById(id);
    const context = canvas.getContext('2d');
//    const myimg = context.getImageData(imageData.width-500, imageData.height-500, 500, 500);
//    context.drawImage(myimg, 0, 0, 500, 500);
    //eventually change this to visible false.  
    //canvas.style.display = 'none';
    const myimg = context.getImageData(0, 0, 500, 500);
    mycode = jsQR(myimg.data, myimg.width, myimg.height);
    

    if (mycode) {
      updateQRResult(mycode);
//      console.log("Found QR code", code);
    }
    else{
//      console.log("No QR code found");
      updateQRResult(null);
    }
 }    

function displayBook(text, id='qrincoming'){
    //display the book in the book div.  

    document.getElementById(id).innerHTML = text.replaceAll("\n", "<br>");

}
  
function updateQRResult(result, id='qrincoming') {
          //maybe want to keep more than one result.  
    if (result && result.data){
      if (result.data !== lastqrresult){
        lastqrresult = result.data;
        console.log("QR Result: " + result.data);
        //need parseBook here.  
        //add to this structure?  Use?  

//        parsegitBook({"d": result.data); //git.js
//make a separate structure for this perhaps.  Just pull the structure and parsing out of git.js perhaps.  

        //do something with the QR result, like displaying it or processing it
        displayBook(result.data)

      }
    }
    else{
        displayBook("", id)
        lastqrresult = "";
    }
  }


 function drawVideo(){
    let canvas = document.getElementById("myvideocanvas");
    let ctx = canvas.getContext("2d");
    if (useyoutube || watch){
    }
    else{
      player = player2;
      if (typeof(player) === 'undefined'){
        //hack for feedback video. rec.html
        player = document.getElementById("myrecordfeedback");
      }
      ctx.drawImage(player, 0, 0, canvas.width, canvas.height);

      //test overlay
      ctx.globalAlpha = 0.5;
      ctx.beginPath(); // Start a new path
      ctx.rect(10, 40, 100, 150); // Add a rectangle to the current path
      ctx.fill(); // Render the path

      ctx.fillStyle = 'black';

      // Set the global alpha value (0 = fully transparent, 1 = fully opaque)

      // Draw the text
      ctx.fillText(currenttranscriptentry, 50, 10);


      //if we have many overlays go through them sequentially.  
      for (i = overlayi; i<overlays.length && i<overlayi+24; i++){        
        if (overlays[i].polygon.type == "line"){
          ctx.beginPath(); // Start a new path
          ctx.globalAlpha = overlays[i].alpha;
          ctx.fillStyle = overlays[i].color;
          ctx.strokeStyle = overlays[i].color;
          ctx.moveTo(overlays[i].x, overlays[i].y);
          ctx.lineTo(overlays[i].x + overlays[i].polygon.points[1][0], overlays[i].y + overlays[i].polygon.points[1][1]);
          ctx.stroke();
        }
      }

      let hcanvas = document.getElementById("myhiddencanvas");
      if (hcanvas == null){
      }
      else{
        let hctx = hcanvas.getContext("2d");
        hctx.globalAlpha = 0.4;
//        hctx.drawImage(canvas, 0, 0, hcanvas.width, hcanvas.height);
        hctx.globalAlpha = 0.5;
        hctx.beginPath(); // Start a new path
        hctx.rect(10, 40, 100, 150); // Add a rectangle to the current path
        hctx.fill(); // Render the path

        hctx.fillStyle = 'black';

        // Set the global alpha value (0 = fully transparent, 1 = fully opaque)

        // Draw the text
        hctx.fillText(currenttranscriptentry, 50, 10);
      }

      //see if we have a barcode in the canvas.  
      if (lastbarcodecheck + 1000 < Date.now()) {
        //draw 
        if (typeof(combinedStream) !== "undefined" && combinedStream != null && combinedStream.active) {

          const imageCapture = new ImageCapture(combinedStream.getVideoTracks()[1]);
          imageCapture.grabFrame().then(imageData => {
            let canvas = document.getElementById('qrscreen');
            canvas.width = 800;
            canvas.height = 800;
            const context = canvas.getContext('2d');
            context.drawImage(imageData, imageData.width-800, imageData.height-800, 800, 800, 0, 0, 800, 800);
            scanQR();
          });
        }
        else if (player != null && player.readyState > 0) {
          if ($('#qrscreen').length){
            let canvas = document.getElementById('qrscreen');
            canvas.width = 800;
            canvas.height = 800;
            const context = canvas.getContext('2d');
            context.drawImage(player, player.videoWidth-800, player.videoHeight-800, 800, 800, 0, 0, 800, 800);
            scanQR();
          }
        }

        lastbarcodecheck = Date.now();
      }  

      requestAnimationFrame(drawVideo);

    }
}

  function skipVideo(secs, v=""){
      if (useyoutube || watch){
          player.seekTo(player.getCurrentTime() + secs);
      }
      else{
          player2.currentTime = player2.currentTime + secs;
      }
  }

  function jumpVideo(eventnum, v=""){
    ct = 0;
      if (useyoutube || watch){
          ct = player.getCurrentTime();
      }
      else{
          ct = player2.currentTime;
      }
      [et, w] = findEvent(eventnum, ct*1000);
      et /= 1000;
      //should be able to get word from this as well.  
      if (et !== 0){
        if (useyoutube || watch){
          player.seekTo(et);
        }
        else{
            player2.currentTime = et;
        }
      }
  }

  function seekVideo(secs, v="", reload=false){
    if (v == ""){
        v = video;
    }
    if (v !=""){
        if (v == video && reload == false){
            if (useyoutube || watch){
                player.seekTo(secs);
            }
            else{
                player2.currentTime = secs;
            }
        }
        else{
            video = v;
            if (useyoutube || watch){
                params = {videoId: video, startSeconds: secs};
                player.loadVideoById(params);
                //player.cueVideoById(video);
            }
            //load data and transcript from this video.  
            if (uid != null){

                ref = firebase.database().ref('/misterrubato/' + video);
                ref.on('value',(snap)=>{
                    if (snap.exists()){
                        item = snap.val();
                        console.log(snap.val());
                        $('#iterationsh').html(makeTimeLinks(snap.val().snippet.description))
                        
                        //get previous iterations of this.  Probably dont need here.  
                        title = snap.val().snippet.description.split('\n')[0];
                        console.log(title);

                        if (!useyoutube){
                            getMedia(snap.val().snippet.description);
                        }
                    }
                });

                //should just use this object.  

                //get the data from the database.  
                firebase.database().ref('/misterrubato/' + video + '/comments/' + uid).once('value')
                .then((snapshot) => {
                    if (snapshot.exists()) {
                        if (typeof(loadPreviousComments) !== "undefined"){
                          loadPreviousComments(snapshot);
                        }
                    }
                    
                });

                firebase.database().ref('/misterrubato/' + video + '/transcript').once('value')
                        .then((snapshot) => {
                            if (snapshot.exists()){
                                loadTranscript(snapshot);
                            }
                            else{
                                console.log('No transcript');		
                                setTranscript('No transcript');							
                                //should never occur
                            }
                        });
            }
            //ontimer.. wait for video to load.  
            setTimeout(() => {
                if (useyoutube || watch){
                    if (player.getPlayerState() == 1) {
                        player.seekTo(secs);
                    }
                    else {
                        ytSeconds = secs;
                        player.playVideo();
                    }
                }
                else{
                    if (player2.readyState > 0){ //HAVE_METADATA
                        player2.currentTime = secs;
                    }
                }
            }, 2000);

        }
    }
}

  function loadVideo(url="", secs=0, v=""){
    if (useyoutube || watch){
        //
        var tag = document.createElement('script');

        tag.src = "https://www.youtube.com/iframe_api";
        var firstScriptTag = document.getElementsByTagName('script')[0];
        firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

        var hideVideo = document.getElementById("my-video");
            hideVideo.style.display = "none";				
//				hideVideo.pause();
//				hideVideo.currentTime = 0;
//				hideVideo.get(0).pause();
//				hideVideo.get(0).currentTime = 0;
    }
    else{
      player2 = document.getElementById("my-video");

        player2.onplay = (event) => {
            console.log(
              "The Boolean paused property is now 'false'. Either the play() method was called or the autoplay attribute was toggled.",
            );
            ispaused = 0;
            midioffset = 0;
            var canvas = document.getElementById("myvideocanvas");
            canvas.style.display = 'block';
            canvas.style.position = 'absolute';
            requestAnimationFrame(drawVideo);
          };

          player2.onpause = (event) => {
            console.log(
              "The Boolean paused property is now 'true'. Either the pause() method was called or the autoplay attribute was toggled.",
            );
            ispaused = 1;
          };
          player2.onended = (event) => {
            console.log(
              "Video stopped either because it has finished playing or no further data is available.",
            );
            ispaused = 1;

          };          
        if (url != ""){
          player2.src = url;
        }
        player2.play();
    }

    if (secs > 0){
        seek = secs;
    }

  }

  function getMedia(desc){
    let tposition = desc.indexOf("MEDIAFILE:");
    if (tposition > -1){
       eposition = desc.indexOf('\n', tposition);
       if (eposition > -1){
           url = desc.substring(tposition+10, eposition);
       }
       else {
           url = desc.substring(tposition+10);
       }
   
       url = url.replace("\r", "");
       var storage = firebase.storage();
   
       var lastPart = url.split("/").pop();
   
   //make this more general.  
   // Create a storage reference from our storage service
       var storageRef = storage.ref();
       //why does this URL have space and others are %20?  
       if (parseInt(lastPart.slice(0,4)) > 2024){
        loc = "videos/" + lastPart.slice(0,4) + "/" + lastPart.replace("%20", " ");
       }
      else{
       loc = "videos/" + lastPart.replace("%20", " ");
      }
       url = storageRef.child(loc).getDownloadURL()
         .then((url) => {
           console.log(url);
           loadVideo(url, 0, video);
   
      })
    }
   }

   function vgetDuration(){
      if (typeof(player2) == 'undefined' || player2 == null){
          return 0;
      }
      if ((useyoutube || watch) && player.getCurrentTime) {
        return player.getDuration()*1000;
      } else if (player2.currentTime) {
        return player2.duration*1000;
      }

   }
   function vgetReferenceTime() {
    if (typeof(player2) == 'undefined' || player2 == null){
        return -1;
    }
    if ((useyoutube || watch) && player.getCurrentTime) {
        const tempTime = player.getCurrentTime();
        const absTime = Math.round(tempTime * 1000);
        return absTime;
    } else if (player2.currentTime) {
        const tempTime = player2.currentTime;
        const absTime = Math.round(tempTime * 1000);
        return absTime;
    }
    else{
      return -1;
    }

}


async function timeoutPromise(delay, val) {
    try {
      const promise = new Promise((resolve) => {
        setTimeout(() => {
          resolve(val);
        }, delay);
      });
  
      const value = await promise;
      console.log(value); // Output: "Promise resolved!"
      return value;
    } catch (error) {
      console.error("Error:", error);
      throw error;
    }
  }



class VideoSnapper {
    
  /**
   * Capture screen as canvas
   * @param {HTMLElement} video element 
   * @param {Object} options = width of screen, height of screen, time to seek
   * @param {Function} handle function with canvas element in param
   */
  constructor(knn=null) {
    // Initiate variables
    this.infoTexts = [];
    this.training = -1; // -1 when no class is being trained
    this.videoPlaying = false;
    this.classes = {};
    this.canvases = {};
    this.funcdict = {};
    this.seeking = false;
    this.funcdict["base"] = function(frame){
      //possibly dynamic detection etc.  based on word.  
      if (frame.word=="good"){
        //etc...

      }
      frame.y = Math.round(frame.height*0.8);
      frame.height = Math.round(frame.height*0.2);
      return frame;
    }

    // Initiate deeplearn.js math and knn classifier objects
    this.bindPage(knn);

    // Create video element that will contain the webcam image
    this.player = document.getElementById('my-video');
  }

  async bindPage(knn=null, mnet=null) {
    if (knn == null){
      this.knn = knnClassifier.create();
    }
    else{
      this.knn = knn;
    }
    if (mnet == null){
      this.mnet = await mobilenet.load();
    }else{
      this.mnet = mnet;
    }


  }


  buildFrames(video, times, word, lang){
    var frames = [];
    let x = 0;
    let y = 0;
    let width = 640;
    let height = 360;
    let wh = [player2.videoWidth, player2.videoHeight];
    if (wh[0] > 0){
      width = wh[0];
    }
    if (wh[1] > 0){
      height = wh[1];
    }




    //frame = this.funcdict[lang]()..
    /*
    if (lang=="base"){ //just taking ~ piano portion of the output.  
      y = Math.round(height*0.8);
      height = Math.round(height*0.2);
    }
    */
    for (var i = 0; i < times.length; i++){
      times[i] /= 1000;
      let frame = {x: x, y: y, width: width, height: height, time: times[i], classId: word, lang: lang, word: word}
      if (typeof(this.funcdict[lang]) !== "undefined"){
        frame = this.funcdict[lang](frame);
      }
      else{
        console.log("No function defined for " + lang);
      }
      frames.push(frame);
    }
    return frames;

  }
  //frameXY[{x: 0, y: 0, time: 0, classId/word or wordhash: 0}, ...]
  //for each word, gets called from findWordsA... or similar.  
  //parameters will be based on the word.  For now just use case either keys or user or full frame.  
  getClassifiers(frameXY, video, numframes =1) {

    let retclassifiers = [];
    var combinedcanvas = document.getElementById('tempcanvas');
    var vertical = true;
    let framerate = 0.33; //30 fps.  
    if (numframes < 1){
      return null;
    }
    if (frameXY[0].width>frameXY[0].height){
      //vertical addition
      combinedcanvas.width = frameXY[0].width;
      combinedcanvas.height = numframes*frameXY[0].height;
    }
    else{
      //horizontal addition
      vertical = false;
      combinedcanvas.width = numframes*frameXY[0].width;
      combinedcanvas.height = frameXY[0].height;

    }

    var seekcallback = function(options) {
      // Create canvas


      let canvas = $('<canvas />').attr({
          id: 'tempcanvas' + options.frameNo,
          width: options.width,
          height: options.height
      })[0];

      //hide canvas for now.  
      canvas.style.display='none';
      // Get context and draw screen on it
      canvas.getContext('2d').drawImage(player2, options.x, options.y, options.width, options.height, 0, 0, options.width, options.height);

      let idx = options.frameNo;
      let tempdiv = document.getElementById('tempcanvasdiv');
      let tempcanvas = canvas;//document.getElementById('tempcanvas' + opts.id);
      const headerText = document.createTextNode("LANG: " + frameXY[options.id].lang + ' WORD: ' + frameXY[options.id].word + ' TIME: ' + options.time);
//      headerText.style.visibility='hidden';
//      tempdiv.appendChild(headerText);
      tempdiv.appendChild(tempcanvas);
      let cc = document.getElementById('tempcanvas');
      const ctx = cc.getContext('2d');
      if (vertical) {
        ctx.drawImage(tempcanvas, 0, options.frameNo*options.height, options.width, options.height);
      }
      else{
        ctx.drawImage(tempcanvas, options.frameNo*options.width, 0, options.width, options.height);
      }
      let status = document.getElementById('tempcanvasstatus');
      status.innerText = "LANG: " + frameXY[options.id].lang + " WORD: " + frameXY[options.id].word + " (" + (options.id+1) + " of " + frameXY.length + ") Frame: " + (options.frameNo+1) + " of " + numframes;
        
      if (options.frameNo == numframes - 1){
        //this is where we have the completed image with all frames.
        //save to DB or other location.  
        let cc = document.getElementById('tempcanvas');
        var imgURL = cc.toDataURL();

        var obj = {img: imgURL, lang: frameXY[options.id].lang, word: frameXY[options.id].word, time: options.time};
        let img = new Image();
        img.src = imgURL;

        //tempdiv.appendChild(img);

        retclassifiers.push(obj);


      } 
      
      // Seek video back if we have previous position 
  };

    var allops = [];
    for (var i = 0; i < frameXY.length; i++) {

      for (var j = 0; j < numframes; j++) {
        if (this.seeking){
          sleep(2000);
        }


        
        this.seeking = true;

       
        let ops = { id: i, x: frameXY[i].x, y: frameXY[i].y, width: frameXY[i].width, height: frameXY[i].height, time: frameXY[i].time+j*framerate, frameNo: j };

        allops.push(ops);


        //ok this is closer, why do I need to do this?  
//      player2.currentTime = ops.time;


      }


    }

    for (var i = 0; i < allops.length; i++){
      console.log(allops[i]);
      let ops = allops[i];
      setTimeout(() => {
        player2.onseeked = function() { 
          console.log(ops);
          seekcallback(ops);
        };
        console.log("seeking to " + ops.time);
        seekVideo(ops.time);
      }, i*1000);
  }
    return retclassifiers;
  }


  addExampleComplete(image, classId){

    let logits;
    // 'conv_preds' is the logits activation of MobileNet.
    if (typeof(this.mnet) == 'undefined' || typeof(this.mnet.infer)== 'undefined'){
       console.log("No mnet object found.  No GPU available?");
       console.log("Skipping KNN example creation.");
       //just add to DB perhaps?  
       return;
    }

    const infer = () => this.mnet.infer(image, 'conv_preds');

    // Train class if one of the buttons is held down
    if (classId != -1) {
      logits = infer();

      // Add current image to classifier
      this.knn.addExample(logits, classId);
    }

  }

  addExample(lang="base", classId=-1, imgURL="") {
    //const image = tf.fromPixels(this.video);

    if (typeof(this.classes[classId]) == 'undefined'){
      this.classes[classId] = 0;
    }
    else{
      //counting all the classes.  
      this.classes[classId] += 1;
    }
    let img = new Image();
    img.src = imgURL;

    //make lang scope local.  Need to do this more.  
    img.onload = (function(lang, classId){
      const canvas = document.getElementById('tempcanvas');
      const ctx = canvas.getContext('2d');
      ctx.drawImage(img, 0, 0);
      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      //add to DB.  
      const image = tf.browser.fromPixels(imageData);
      vs[lang].addExampleComplete(image, classId);
    })(lang, classId);
  }

}


function getVideoJson(videoid, mode=VID_VIEW){
        
  video = videoid;
  vref = firebase.database().ref('/misterrubato/' + videoid);
  vref.once('value')
                    .then((snap) => {
                      //.on('value',(snap)=>{
      if (snap.exists()){
          loadVideo();
          seekVideo(0, video, true);
          item = snap.val();
          console.log(snap.val());

          if (mode & VID_DETAILS){
            $('#iterationsh').html(makeTimeLinks(snap.val().snippet.description))
            createNotesArray();
          } 
          
          //get previous iterations of this.  
          title = snap.val().snippet.description.split('\n')[0];
          author = snap.val().snippet.channelTitle;
          authorurl = "https://www.youtube.com/channel/" + snap.val().snippet.channelId;
          $('#vidinfo').html(title + " (<a href=\"" + authorurl + "\">" + author + "</a>)");
          console.log(title);

          //we need to get the iterations here before we do anything else, otherwise the graphic doesnt work.  
          numiterations = getIterations(item.snippet.description, item.snippet.publishedAt, true);
//			searchPrevious(videoid);

          if (mode & VID_DETAILS){
            searchPrevious(videoid);

            getTranscript(item.snippet.description);
            getMedia(item.snippet.description);
            getMidi(item.snippet.description);
      
          }
          else{
  //			getTranscript(item.snippet.description);
            getMedia(item.snippet.description);
  //			getMidi(item.snippet.description);
          }
      }
      else{
          //this is not our video, need to retrieve and allow for commenting.  
          //this can be for comments.  Then we can retrieve comments from the person.  via API
          //misterrubato/watch/xxxx
          //combine this from several people you like.  
          //Need to record the audio though if we do like this.  
          //but this is sustainable then.  This is a web server per person.  
          //when you are following someone, the algorithm would overlay that audio on top of 
          //whatever you are watching based on your settings.  
          //we need a master DB though probably, otherwise you have too much unnecessary traffic.  
          //add this description to our DB using timestep.  
          //item.snippet.description
          watch = true;
          loadVideo();
          console.log(videoid + " Not in DB.  Retrieving from Youtube API");
          vref = firebase.database().ref('/watch/' + videoid);
          vref.on('value',(snap)=>{
              if (snap.exists()){
              //retrieve previous comments etc.  
              }
              else{
              //		obj = {"comments": mycomments, "sentiment": grade };
              //uRef.set(obj);
              }
          });
              tempurl = 'https://www.youtube.com/watch?v=' + videoid;

              //https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=R4LoM208_Ow
              $.getJSON('https://www.youtube.com/oembed?url=' + tempurl, function (data) {
                  console.log(data.title);
                  title = data.title;
                  console.log(data.author_name);
                  author = data.author_name;
                  console.log(data.author_url);
                  authorurl = data.author_url;
                  console.log(data.thumbnail_url);
                  $('#vidinfo').html(title + " (<a href=\"" + authorurl + "\">" + author + "</a>)");
              });
              //input details about this video

      }

  });



}
