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


class gitDB{
	//save any git repo info and cache locally.  
	//only download if not already in DB, or size doesnt match.  
	//gitcommits.push({"url": data[this.indexValue].html_url, "patch": commitdata.files[i].patch, "filename": commitdata.files[i].filename, "changes": commitdata.files[i].changes, "d": mydate, "selected": true});
	//gitbook.push({"url": this.url, "gitdata": bookdata[this.indexValue], "d": gitbookname, "content": data, "selected": true});
	constructor(){
		this.db = new Dexie("gitDB");
		this.db.version(1).stores({
			gitrepos: "++id,userid,repo,branch", 
			gitcommits: "++id,url,filename,d", //patch, changes
			gitbook: "++id,url,d", //gitdata, content
			gitcontents: "++id,url", //content 
		});
	}

	saveRepo(userid, repo, branch){
		var obj = {"userid": userid, "repo": repo, "branch": branch};
		this.db.gitrepos.add(obj).then((id) => {
			console.log("added repo with id " + id);
		});
	}
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
			this.ftsindex.add(obj.vidid + '_' + obj.id, obj.ocrtext);
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
		var obj = {"id": vidid + "_" + id, "vidid": vidid, "timestamp": timestamp, "imgblob": imgblob, "ocrtext": ocrtext};
		this.db.screenshots.add(obj).then((id) => {
			console.log("added screenshot with id " + id);
			this.ftsindex.add(vidid + "_" + id, obj.ocrtext);
			if (cb != null){
				cb(id); //callback to complete.  
			}
		});
	}

	getRecent(name=""){
		return this.db.vids.where("name").startsWith(name).reverse().sortBy("version");

	}
	
	getVideos(vids=[]){
		return this.db.vids.bulkGet(vids);
		//how to sort this?  
	}

	getScreenshots(ssids=[]){
		return this.db.screenshots.bulkGet(ssids);
	}

	getSimilar(text="", limit=10){
		//use FTS index to find similar.  
		//index.search({tag:"cat"})
		return this.ftsindex.search(text, {limit: limit});

	}
}


