function addUser(user){
    uid = user.uid;
	displayname = user.displayName;
	email = user.email;
	phone = user.phoneNumber;
	pic = user.photoURL;
	console.log(displayname + " " + email + " " + phone + " " + pic);
    //add to DB.  
	var uRef = firebase.database().ref('/users/' + uid);

	obj = {"name": displayname, "pic": pic};
	uRef.set(obj);
	
}



class recDB{
		constructor(){
		this.db = new Dexie("recDB");
		this.db.version(1).stores({
			vids: "++id,userid,category,name,version", //mycomments, videoblob (if local), otherwise remoteurl
			screenshots: "id,userid,vidid,timestamp", //imgblob, ocrtext
		});

		this.ftsindex = FlexSearch.Index({});
		//really need FTS component.  Load all transcript etc for FTS.  
		//not sure how scalable this is, but I estimate perhaps 1000 local records = ~10MB max which browser should handle fine.  
		//may need to limit FTS load to 1000 records or so.
	}

	loadFTS(){
		this.db.vids.each((obj) => {
			this.ftsindex.add(obj.id, obj.category + " " + obj.name + " " + obj.mycomments);
		});
		this.db.screenshots.each((obj) => {
			this.ftsindex.add("OCR" + obj.id, obj.ocrtext);
		});
	}

	saveVideo(userid, category, name, version, mycomments, videoblob, remoteurl=null, cb=null){
		var obj = {"userid": userid, "category": category, "name": name, "version": version, "mycomments": mycomments, "videoblob": videoblob, "remoteurl": remoteurl};
		this.db.vids.add(obj).then((id) => {
			console.log("added video with id " + id);
			this.ftsindex.add(id, obj.category + " " + obj.name + " " + obj.mycomments);
			if (cb != null){
				cb(id); //callback to add screenshots.  
			}
		});


	}

	saveScreenshot(id, vidid, timestamp, imgblob, ocrtext, cb=null){
		var obj = {"id": id, "vidid": vidid, "timestamp": timestamp, "imgblob": imgblob, "ocrtext": ocrtext};
		this.db.screenshots.add(obj).then((id) => {
			console.log("added screenshot with id " + id);
			this.ftsindex.add(vidid + "_" + id, obj.ocrtext);
			if (cb != null){
				cb(id); //callback to complete.  
			}
		});
	}
}


