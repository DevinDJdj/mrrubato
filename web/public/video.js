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
        midienabled = 0;
    }

    if (event.data == YT.PlayerState.PLAYING) {
//          setTimeout(stopVideo, 6000);
//			console.log("state change");
        midienabled = 1;
        
      done = true;
    }
  }
  function stopVideo() {
    player.stopVideo();
  }


  function seekVideo(secs, v){
    if (v !=""){
        if (v == video){
            player.seekTo(secs);
        }
        else{
            video = v;
            player.loadVideoById(video);
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
                if (player.getPlayerState() == 1) {
                    player.seekTo(secs);
                }
                else {
                    ytSeconds = secs;
                    player.playVideo();
                }
            }, 2000);
        }
    }
}

  function loadVideo(url="", secs=0, v=""){
    if (useyoutube){
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
        if (secs > 0){
            seek = secs;
        }
    }
    else{
		v = document.getElementById("my-video");
		v.src = url;
        v.play();
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
   
