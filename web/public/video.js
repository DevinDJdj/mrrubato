var watch = false;
var player;
var player2;
var currenttranscriptentry = "";
var transcriptarray = [];
var overlays = [];
var overlayi = 0;

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

  function drawVideo(){
    var canvas = document.getElementById("myvideocanvas");
    var ctx = canvas.getContext("2d");
    if (useyoutube || watch){
    }
    else{
      ctx.drawImage(player2, 0, 0, canvas.width, canvas.height);

      //test overlay
      ctx.beginPath(); // Start a new path
      ctx.rect(10, 40, 100, 150); // Add a rectangle to the current path
      ctx.fill(); // Render the path

      ctx.fillStyle = 'black';

      // Set the global alpha value (0 = fully transparent, 1 = fully opaque)
      ctx.globalAlpha = 0.5;

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
      et = findEvent(eventnum, ct);
      if (useyoutube || watch){
        player.seekTo(player.getCurrentTime() + et);
      }
      else{
          player2.currentTime = player2.currentTime + et;
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
                        loadPreviousComments(snapshot);
                    }
                    
                });

                firebase.database().ref('/misterrubato/' + video + '/transcript').once('value')
                        .then((snapshot) => {
                            if (snapshot.exists()){
                                loadTranscript(snapshot);
                            }
                            else{
                                console.log('No transcript');									
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
       loc = "videos/" + lastPart.replace("%20", " ");
       url = storageRef.child(loc).getDownloadURL()
         .then((url) => {
           console.log(url);
           loadVideo(url, 0, video);
   
      })
    }
   }
   
