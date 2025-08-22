//should combine with updateVideo afterward.  
//not sure if the struct should be uid / comments, or comments /uid

var mytitle = '';
var vs = null; //VideoSnapper
var as = null; //AudioSnapper

function getNetwork(lang, vs){
    //if KNN for this lang exists, load it.  
	//load from DB.  
	let classDB = getClassifierDB(lang);
	classDB.getKNN(lang, currentmidiuser).then(knnarray => {	
		myknn = null;
		if (knnarray != null && knnarray.length > 0){
			//return knn array.  
			myknn = classDB.getKNNFromBlob(knnarray[0].knnblob);
		}
		else{
			//no knn found for this lang and user.  
			myknn = null;
		}

		if (myknn !== null){
			//load KNN into network.
	
	
			//vs.knn.setClassifierDataset(exists[0].knnblob); //should be an array returned.  
			vs[lang].knn.setClassifierDataset(myknn);
			//vs[lang].knn.classDatasetMatrices = exists[0].knnblob; //should be an array returned.
			/*
			for (const label in vs.knn.classDatasetMatrices) {
				vs[lang].knn.classExampleCount[label] = vs[lang].knn.classDatasetMatrices[label].shape[0];
				}
			*/
	
		}
	
	}).catch(error => {
		console.log("Error retrieving KNN: " + error);
		return null;
	});

    return null;
}


function saveNetwork(lang, knn){
	//save KNN for this lang.
    let classDB = new classifierDB(lang);

	console.log(knn);
	//save classifier to DB.  
	let now = new Date();


	classDB.saveKNN(lang, currentmidiuser, now.format("yyyymmddHHMMss"), knn);
}

function getClassifierDB(lang){
    //if exists in DB, retrieve from DB.  
    classDB = new classifierDB(lang);

    return classDB;
}

async function saveClassificationImages(video){

	vs = {};
    findWordsA(currentmidiuser);
    for (const [lang, value] of Object.entries(wordtimes)) {

        //should classification network be per language?  
        //perhaps...
		vs[lang] = new VideoSnapper(null); //associate with language?  
        let net = getNetwork(lang, vs); //really want to get NN here.  


        const body = document.body;
        for (const [word, times] of Object.entries(value)) {                
            //console.log("WORD: " + word + " " + times);

            //prefDB



            let frames = vs[lang].buildFrames(video, times, word, lang);
            let classifiers = await timeoutPromise(times.length*12000, vs[lang].getClassifiers(frames, video, 10));
            classifiers.forEach(c => {
                //eventually this should be in some DIV which is reviewable and not end of document.  
                console.log("LANG: " + c.lang + ' WORD: ' + c.word);
				vs[lang].addExample(lang, c.word, c.img);				
                //add to DB.  with video info, title, lang, word and classification image.  
                //classDB.saveScreenshot(video, c['lang'], c['word'], currentmidiuser, mytitle, c['time'], c['img']);
				

            });

			setTimeout((l) => {
				//save network after each word?
				//or save all at once?
				//need to save each lang separately.  
				//saveNetwork(lang, vs.knn);
				saveNetwork(l, vs[l].knn);				
			}, 10000, lang);


        }
    }        

}


function initAudioFeedback(){
	//load audio control language.  
	//initialize AudioSnapper
	as = {};
	as["base"] = new AudioSnapper();

	
}

function saveAudioFeedback(useridx=0){

	if (useridx > 0 || (!isadmin)){
		//not sure if we will do this ever.  This is overwriting another users audio feedback.  
		feedbackid = users[useridx].uid;
		return;
	}

	//save audio feedback for this lang.  
	for (const [lang, value] of Object.entries(as)){
		
		//this shouldnt be that much data, so we can save one by one.  
		let aa = as[lang].audioarray[useridx];
		for (let i=0; i< aa.length; i++){
			console.log("Audio " + lang + " " + i + " " + aa[i]);
			var uRef;
			if (watch === false){
				uRef = firebase.database().ref('/misterrubato/' + video + '/comments/' + uid + '/audio/' + lang + '/' + i);
			}
			else{
				uRef = firebase.database().ref('/watch/' + video + '/comments/' + uid + '/audio/' + lang + '/' + i);
			}
			uRef.set(aa[i]);
		}
	}
}

function saveFeedback(){
	//get authuid.  
	//getref to uid
	//then under here store the videos.  
	//does the video have to be associated with the channel, I guess not.  
	
	
	var grade = $('#points').val();
	var transcript = $('#transcript').val();
	if (uid !==null){
		const currentdate = new Date();
		strdate = currentdate.toISOString().substring(0, 19).replaceAll('-','').replaceAll(':','');
	    if (watch === false){
			var uRef = firebase.database().ref('/misterrubato/' + video + '/comments/' + uid);
	//		videojson.snippet.description = $('#iterations').val();
	//		videojson = JSON.parse( JSON.stringify(videojson ) );
			console.log(uid);
			mycomments = $('#mycomments').val();

	//		sentiment = "test"; //for now
			midifeedback = getMidiFeedback();
//			document.getElementById('out').innerHTML = 'New file: <a download=my.mid href=' + midifeedback + '>DOWNLOAD</a> <embed src=' + midifeedback + ' autostart=false>';


			//get chat history here.  
			let chatted = ""
            if (typeof(getChatHistory) !== "undefined"){
                chatted = getChatHistory();
            }
			obj = {"comments": mycomments, "chatted": chatted, "sentiment": grade, "midi": midifeedback, "updated": strdate };
			uRef.set(obj);

			//set transcript only if we have actually updated it.  
			if (isadmin && transcript.trim() !== "" && originaltranscript !== transcript){
				var tRef = firebase.database().ref('/misterrubato/' + video + '/transcript');
				obj = {"transcript": transcript, "updated": strdate };
				tRef.set(obj);
			}

			saveAudioFeedback(); //save audio feedback for this user.

            //save words associated with this video.  
			if ($("#genCat").is(":checked")){
            	saveClassificationImages(video);	
			}
		}
		else{
			console.log(video + " Not in DB.  Adding watch comments");
			var uRef = firebase.database().ref('/watch/' + video + '/comments/' + uid);
			mycomments = $('#mycomments').val();

	//		sentiment = "test"; //for now
			midifeedback = getMidiFeedback();
			obj = {"comments": mycomments, "sentiment": grade, "midi": midifeedback, "updated": strdate };
			uRef.set(obj);
		
		}
	}
	

	//somewhere else?
	//config.html
//	saveUserConfig();

}


function updateNotes(){
    var allnotes = "";
	for (i=0; i<notesarray.length; i++){
	    allnotes += notesarray[i] + "\n";
	}
    $('#mycomments').val(allnotes);
	//add clickable link inside here instead.  
	$('#mycommentsh').html(makeTimeLinks(allnotes));
	
}

function createTranscriptArray(){
//also update the new DIV with links.  
	alltranscript = $('#transcript').val();
	transcriptarray = [];
	const lines = alltranscript.split("\n");
	for (i = 0; i< lines.length; i++){
	    transcriptarray[i] = lines[i];
	}
	console.log(transcriptarray);

}

function createNotesArray(){
//also update the new DIV with links.  
	allnotes = $('#mycomments').val();
	notesarray = [];
    const lines = allnotes.split("\n");
	for (i = 0; i< lines.length; i++){
	    notesarray[i] = lines[i];
	}
	console.log(notesarray);
	//set title
    updateNotes();
}

function getTime(comment){
	const regExp = /\(([^)]+)\)/g;
    const matches = [...comment.matchAll(regExp)].flat();
//    console.log(matches);
	if (matches.length > 0){
	    return getSecsFromTime(matches[1]);
	}
	else{
	    return 0;
	}
}


function getIterations(desc, vidtime, isme=false){
	st = [];
	et = [];
	s = 0;

	if (desc ==""){
		//one iteration length of video.  
		//this is for watch.  
		e = player.getDuration();
		st.push(1);
		et.push(e);
		maxduration = e-1;
		numiterations = 1;
		myst.push(st[0]);
		myet.push(et[0]);
	}
	else{
        mytitle = desc.split('\n')[0];
		for (i=1; i< 20; i++){
			s = -1;
			e = -1;
			fnd = "TRIAL#" + i;
			let ts = desc.indexOf(fnd);
			te = desc.indexOf(")", ts);
			if (ts > -1)
				s = getSecsFromTime(desc.substring(ts+(fnd.length)+2, te));
				
			fnd = "END#" + i;
			ts = desc.indexOf(fnd);
			te = desc.indexOf(")", ts);
			if (ts > -1)
				e = getSecsFromTime(desc.substring(ts+(fnd.length)+2, te));
			if (s > -1 && e > -1 && e > s){
				st.push(s);
				et.push(e);
			}
		}
		console.log(st);
		console.log(et);
		//arrays of all iterations
		mydate = new Date(vidtime);
//		if (!isme){
			for (i=0; i< st.length; i++){
				if (et[i] !==null){
					tempdate = mydate;
					tempdate.setSeconds(tempdate.getSeconds()+st[i]);
					starttimes.push(tempdate);
					durations.push([tempdate, et[i]-st[i]]);
					if (isme){
						myst.push(st[i]);
						myet.push(et[i]);
						if (et[i]-st[i] > maxduration){
							maxduration = et[i]-st[i];
							
						}
					}
					tempdate.setSeconds(tempdate.getSeconds()+(et[i]-st[i]));
					endtimes.push(tempdate);
				}
			}
		}
		//from here generate some sort of graphic.  
//	}
	return st.length;
}


function getUser(userindex){

    //if uid is array
    //user = users.find((u) => u.uid.includes(uid));
  //  user = users.find((u) => u.uid == (uid));
  //  userindex = users.findIndex((u) => u.uid == (uid));
      user = users[userindex];
  
  
      uRef = firebase.database().ref('/users/' + uid);
      firebase.database().ref('/users/' + uid).once('value')
                        .then((snapshot) => {
                          if (snapshot.exists()) {
                              //use snapshot.key here because of many subsequent calls uid will change.  
                              if (user.uid == snapshot.key && user.pic == ""){ //initialize this user and add image
                                  
                                  users[userindex].pic = snapshot.val().pic;
                                  users[userindex].name = snapshot.val().name;
                                  var elem = document.createElement("img");
                                  elem.setAttribute("src", users[userindex].pic);
                                  elem.setAttribute("alt", users[userindex].name);
                                  elem.setAttribute("height", "32");
                                  elem.setAttribute("width", "32");
                                  document.getElementById("usericon").appendChild(elem);	//add to DB.  
  
                          } else {
                              console.log("User not found" + snapshot.key);
                          }
                      }
                  });
  
  }
  
  function addMe(user){
      myuser = user;
      uid = user.uid;
      displayname = user.displayName;
  //	email = user.email;
  //	phone = user.phoneNumber;
      pic = user.photoURL;
  
      users.push({"uid": uid, "pic": pic, "name": displayname}); //lookup for array location -> uid
  
      console.log(displayname + " " + pic);
  
      //add user icon
      document.getElementById("usericon").innerHTML = "";
      var elem = document.createElement("img");
        elem.setAttribute("src", user.photoURL);
        elem.setAttribute("alt", user.displayName);
        elem.setAttribute("height", "64");
        elem.setAttribute("width", "64");
        document.getElementById("usericon").appendChild(elem);	//add to DB.  
  
      //do we need this, this doesnt work with Watch:
      /*
      uRef2 = firebase.database().ref('/misterrubato/' + video + '/uid');
      firebase.database().ref('/misterrubato/' + video + '/uid').once('value')
                        .then((snapshot) => {
                          if (snapshot.exists()) {
  
                          } else {
                              
                              obj = {"uid": uid};	
                              uRef2.set(obj);
                          }
                      });
      */
  
      uRef = firebase.database().ref('/users/' + uid);
      firebase.database().ref('/users/' + uid).once('value')
                        .then((snapshot) => {
                          now = new Date();
                          if (snapshot.exists() && typeof(snapshot.val().numlogins) !="undefined") {
                              num = snapshot.val().numlogins + 1;
                              ll = now.toISOString().substring(0, 10).replaceAll('-','');
                              uRef.update({"numlogins": num, "lastlogin": ll});
  
                          } else {
                              
                              obj = {"name": displayname, "pic": pic, "firstlogin": now.toISOString().substring(0, 10).replaceAll('-',''), "lastlogin": now.toISOString().substring(0, 10).replaceAll('-',''), "numlogins": 1};	
                              uRef.set(obj);
                          }
                      });
      
  }
  
  
  function setTranscript(transcript){
	$('#transcriptsh').html(makeTimeLinks(transcript));
	//right now this is not refreshed on page load.  
	//this ends up being the original transcript for some reason.  
	//not sure if we want this or not.  Here we dont keep history about the original transcript.  
	//is this important?  
	var tempDiv = $('#transcript');
	if (isadmin){
		tempDiv.readOnly = false;
	}
	else{
		tempDiv.readOnly = true;
		//we get the updated transcript, but cant edit further.  This removes confusion about if you can edit.  
	}
	tempDiv.val(transcript);
	createTranscriptArray();
}

function toggleTranscript(){
	if ($('#transcript').is(':visible')){
		setTranscript($('#transcript').val());
		$('#transcript').hide();
		$('#transcriptsh').show();
	}
	else{
		$('#transcript').show();
		$('#transcriptsh').hide();
	}
}


function toggleMyComments(){
	if ($('#mycomments').is(':visible')){
		createNotesArray(); //update values of the data.  
		$('#mycomments').hide();
		$('#mycommentsh').show();
	}
	else{
		$('#mycomments').show();
		$('#mycommentsh').hide();
	}
}
function loadTranscript(snapshot){
	console.log(snapshot.val().transcript);
	if (snapshot.val().transcript !==null){
		//not sure if we want this or not.  Here we dont keep history about the original transcript.  
		//is this important?  
		originaltranscript = snapshot.val().transcript;
		setTranscript(snapshot.val().transcript);
	}
}

//loadFeedback
function loadPreviousComments(snapshot, uid=0){
	user=0;
	currentmidiuser = 0;
	allcomments = snapshot.val();
	foundme = false;

	for (const [key, value] of Object.entries(allcomments)){
		if (key == uid){
			$('#mycomments').val(value.comments);
			$('#mycommentsh').html(makeTimeLinks(value.comments));
			if (value.sentiment !==null){
				$('#points').val(value.sentiment);
			}
			currentmidiuser = 0;
			foundme = true;
		}
		else{
			midiarray.push({"base": []});
			users.push({"uid": key, "pic": "", "name": ""}); //lookup for array location -> uid
			currentmidiuser=midiarray.length-1;
			getUser(currentmidiuser);
		}
		midifeedback = value.midi;
		langstoload = loadMidiFeedback(midifeedback);
		loadDictionaries(currentmidiuser, langstoload);

		if ("audio" in value){
			for (const [alang, avalue] of Object.entries(value.audio)){
				if (!(alang in as)){
					as[alang] = new AudioSnapper();
				}
				as[alang].loadAudioFeedback(avalue, currentmidiuser);
			}
		}


		console.log("MIDI:" + midifeedback);
	}

	if (!foundme){
		//logged in user has no comments.  
		//need to load anyway.  
		loadDictionaries(0);
	}
	//set back to our user.  
	currentmidiuser = 0;
//	initDicFilters();

}


function getMidi(desc){
    var tempDiv = $('#midi');
    //find in notes array the TRANSCRIPT:
    //gsutil cors set cors.json gs://misterrubato-test.appspot.com
    let tposition = desc.indexOf("MIDI:");
    url = "";
    if (tposition > -1){
       eposition = desc.indexOf('\n', tposition);
       if (eposition > -1){
           url = desc.substring(tposition+5, eposition);
       }
       else {
           url = desc.substring(tposition+5);
       }
   //	tempDiv.html(url);
   //using up space.  Need this space.  
       getAnalyze(url);
    }
    else{
       //initialize blank midi.  
       getAnalyze(url);
    }
   }
   
   
   
   function getIteration(currentTime){
       for (j=0; j< myst.length; j++){
           if (currentTime >= myst[j] && currentTime <= myet[j]){
               return j;
           }
       }
       return -1;
   }
   
   
   function getIterationAndSecs(){
       if (useyoutube || watch){
           if (player.getCurrentTime){
               var tempTime = player.getCurrentTime();
               i = getIteration(tempTime);
               secs = tempTime - myst[i];
           }
       }
       else{
           if (player2.readyState > 0){
                   var tempTime = player2.currentTime;
                   i = getIteration(tempTime);
                   secs = tempTime - myst[i];
           }
       }
       return i, secs;
   }

   
   function addImages(ims, storageRef){
    //in case we have \r\n
    removeAllChildren("images");


    for (i=0; i< ims.length; i++){
        let im = ims[i];
        im = im.replace("\r", "");
        // Create a storage reference from our storage service
        addImage(im, storageRef, (i==0)? 1 : 0);

    }

   }

   function getAnalyze(midiurl){
    //in case we have \r\n

	removeAllChildren("pianorollmini");
	removeAllChildren("pianoroll");
	removeAllChildren("images");
    var storage = firebase.storage();
	//make this more general.  
	// Create a storage reference from our storage service
    var storageRef = storage.ref();
	if (midiurl == ""){
		//set up blank image for visualizing feedback anyway.  
		addImages([""], storageRef, 1);
	}
	else{

		midiurl = midiurl.replace("\r", "");

		var lastPart = midiurl.split("/").pop();

		//why does this URL have space and others are %20?  
		if (parseInt(lastPart.slice(0,4)) > 2024){
			midiloc = "midi/" + lastPart.slice(0,4) + "/" + lastPart.replace("%20", " ");

		}
		else{
			midiloc = "midi/" + lastPart.replace("%20", " ");
		}

		url = storageRef.child(midiloc).getDownloadURL()
		.then((url) => {
			console.log("MIDI: " + url);
            if (typeof(midicontroller) !== "undefined"){
                midicontroller.getFile(url);
            }
            else{
    			getFile(url); //midi.js 
            }
		})
		

        //this needs to be changed.  

        ims = [];

        im = "analyze/" + lastPart;
        im = im.replace(".mid", ".jpg");
        ims.push(im);

        im = "analyze/kk_" + lastPart;
        im = im.replace(".mid", ".png");
        ims.push(im);
	
        im = "analyze/ks_" + lastPart;
        im = im.replace(".mid", ".png");
        ims.push(im);

        im = "analyze/ks2_" + lastPart;
        im = im.replace(".mid", ".png");
        ims.push(im);

        addImages(ims, storageRef); //external function. should use class pointer function?  minimize to one call.  

	}	
}

function getTranscript(desc){
 var tempDiv = $('#transcript');
 var tempDiv2 = $('#transcriptsh');
 //find in notes array the TRANSCRIPT:
 //gsutil cors set cors.json gs://misterrubato-test.appspot.com
 let tposition = desc.indexOf("TRANSCRIPT:");
 if (tposition > -1){
    eposition = desc.indexOf('\n', tposition);
	if (eposition > -1){
    	url = desc.substring(tposition+11, eposition);
	}
	else {
		url = desc.substring(tposition+11);
	}
	if (url.trim() !== "error"){
		tempDiv.load(url, function(){
			createTranscriptArray();
		});
		tempDiv2.load(url, function(){
			tempDiv2.html(makeTimeLinks(tempDiv2.html()));
		});
	}
 }
}

function makeTimeLinks(desc){
    desc = desc.replaceAll("\n", "<br>");
//    desc = desc.replace(")", ")<br>");
	const regExp = /\(([^)]+)\)/g;
	regExp2 = /\d+\:\d\d?/g;
    const matches = [...desc.matchAll(regExp2)].flat();
	for (i=0; i<matches.length; i++){
	    secs = getSecsFromTime(matches[i]);
		if (secs > 0){
    		desc = desc.replace(matches[i], '<a href="#" onclick="seekTo(' + secs + ');">' + matches[i] + '</a>');
		}

	}
//    console.log(matches);
	return desc;
}
