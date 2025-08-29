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

async function checkStorage(){
	const quota = await navigator.storage.estimate();
	const totalSpace = quota.quota;
	const usedSpace = quota.usage;
	console.log('Approx total allocated space:', totalSpace);
	console.log('Approx used space:', usedSpace);	
	console.log('PCT Used: ', ((usedSpace/totalSpace)*100).toFixed(2) + '%');
}


class classifierDB{
	constructor(lang=""){
		this.db = new Dexie("classDB");
		this.lang = lang;
		this.ftsindex = FlexSearch.Index({});

		this.db.version(1).stores({
			examples: "++id,lang,word,user,topic,vid,timestamp", //imagedata.  
			knn: "++id,lang,user,[lang+user],timestamp", //knn data.
		});
		this.db.version(2).stores({
			examples: "++id,lang,word,user,topic,vid,timestamp,imgblob", //imagedata.  
			knn: "++id,lang,user,[lang+user+topic],topic,timestamp", //knn data.
		});
	}

	//do we want to save screenshots or just the model.  
	saveScreenshot(vidid, lang, word, user, topic, timestamp, imgblob, cb=null){
		var obj = {"vid": vidid, "timestamp": timestamp, "imgblob": imgblob, "lang": lang, "word": word, "user": user};
		this.db.screenshots.add(obj).then((id) => {
			console.log("added screenshot with id " + id);
			this.ftsindex.add(vidid + "_" + id, word);
			if (cb != null){
				cb(id); //callback to complete.  
			}
		});
	}

	getKNN(lang="", user="", topic="", timestamp=0){
		//get all knn for this lang and user.  
		return this.db.knn.where("[lang+user+topic]").equals([lang,user,topic]).toArray();
	}

	getKNNBlob(knn){
		/*
		let dataset = knn.getClassifierDataset();
		var datasetObj = {};
		Object.keys(dataset).forEach((key) => {
		  let data = dataset[key].dataSync();
		  // use Array.from() so when JSON.stringify() it covert to an array string e.g [0.1,-0.2...] 
		  // instead of object e.g {0:"0.1", 1:"-0.2"...}
		  datasetObj[key] = Array.from(data); 
		});
		let jsonStr = JSON.stringify(datasetObj)		
		*/
		let jsonStr = JSON.stringify( Object.entries(knn.getClassifierDataset()).map(([label, data])=>[label, Array.from(data.dataSync()), data.shape]) );
		return jsonStr;
	}

	  
	getKNNFromBlob(knnblob, knn){
//		let tensorObj = JSON.parse(knnblob);
		//covert back to tensor
		let tensorObj = Object.fromEntries( JSON.parse(knnblob).map(([label, data, shape])=>[label, tf.tensor(data, shape)]) )
//		return Object.fromEntries( tensorObj.map(([label, data, shape])=>[label, tf.tensor(data, shape)]) )
		return tensorObj;

	}

	//do we need user here?  
	saveKNN(lang, user, timestamp, knn, topic="", cb=null){
		let knnblob = this.getKNNBlob(knn);
		this.getKNN(lang, user, topic, timestamp).then((exists) => {
			if (exists != null && exists.length > 0){
				//already exists.  
				exists[0].timestamp = timestamp;
				exists[0].knnblob = knnblob;
				this.db.knn.put(exists[0]).then((id) => {
					console.log("updated knn with id " + id);
	//				this.ftsindex.add(vidid + "_" + id, lang);  
					if (cb != null){
						cb(id); //callback to complete.  
					}
				});
	
			}
			else{
				var obj = {"timestamp": timestamp, "knnblob": knnblob, "lang": lang, "user": user, "topic": topic};
				this.db.knn.add(obj).then((id) => {
					console.log("added knn with id " + id);
	//				this.ftsindex.add(vidid + "_" + id, lang);  
					if (cb != null){
						cb(id); //callback to complete.  
					}
				});
			}
	
		}).catch((err) => {
			console.log("error in getKNN: " + err);
		});

	}


}

class codeGraphDB {
	constructor(){
		this.db = new Dexie("codeGraphDB");
		this.db.version(1).stores({
			graph: "++id,qpath,[qpath+qpath2]", //options for node connectivity.  
			//mimic the DOT structure.  Only want to lookup by connection for now though.  
			//TOPICNAME.CLASSNAME.FuncName -> TOPICNAME.CLASSNAME.FuncName ...


		});
	}


	getGraph(qpath, depth=1){
		if (depth==1){
			//get all nodes connected to this qpath.  
			//return all nodes connected to this qpath.  
			return this.db.graph.where("qpath").equals(qpath).toArray();

		}
		if (depth > 1){
			ret = [];
			tops = this.getGraph(qpath,1);
			tops.forEach((top) => {
				//get all nodes connected to this qpath.  
				//return all nodes connected to this qpath.  
				ret.append(this.getGraph(top.qpath2, depth-1));
			});
			return ret;
		}
		else{
			return [];
		}


	}

	addGraph(qpath, qpath2){
		//add a new graph node.  
		this.db.graph.where("[qpath+qpath2]").equals([qpath,qpath2]).first().then((obj) => {
			if (obj == null){
				//add new graph node.  
				var obj = {"qpath": qpath, "qpath2": qpath2};
				this.db.graph.add(obj).then((id) => {
					console.log("added graph with id " + id);
				});
			}
			else{
				console.log("graph already exists");
			}
		}).catch((err) => {
			console.log("error in addGraph: " + err);
		});


	}
}

class tagDB{
	//save all tags and tag info.  
	//tags are unique, but can have multiple entries.  
	//tagid is unique, but can be reused.  
	constructor(){
		this.db = new Dexie("tagDB");
		this.db.version(1).stores({
			tags: "++id,tagname,tagdesc", //tagid, tagname, tagdesc
			//tagid refers to tags to lookup tagname
			//tagdb/tagtable/tagcolumn refers to the DB being used.  
			//topic refers to the field value being tagged.  
			//tagvalue is blank if the value is same as tagname.  This should be standard if possible.  
			taginfo: "++id,tagid,tagname,tagdb,tagtable,tagcolumn,[tagdb+tagtable+tagcolumn],[tagdb+tagtable+tagcolumn+tagvalue]", //tagid, userid, tagdesc

		});

	}
	//these should have default handlers if blank.  
	//get all tags when loading self DB.  in constructor, or load function.  

	getTags(tagname="", tagdb="", tagtable="", tagcolumn="", tagvalue=""){
		//get all tags for this DB.  
		//not most efficient path.  
		if (tagname =="" && tagdb =="" && tagtable =="" && tagcolumn =="" && tagvalue ==""){
			//tag table.  
			return this.db.tags.toArray();
		}
		else{
			//tag info table
			if (tagvalue !== ""){
				//tagvalue is not blank.  get tag info for this value.  
				return this.db.taginfo.where("[tagdb+tagtable+tagcolumn+tagvalue]").equals([tagdb,tagtable,tagcolumn,tagvalue]).toArray();
			}
			else{
				if (tagname !== ""){
					if (tagdb !== "" && tagtable !== "" && tagcolumn !== ""){
						//tagname is not blank.  get tag info for this tagname.  
						//not sure if this is what we want.  
						return this.db.taginfo.where("[tagdb+tagtable+tagcolumn+tagvalue]").equals([tagdb,tagtable,tagcolumn,tagname]).toArray();
					}
					else if (tagcolumn !== ""){	
						//tagname is not blank.  get tag info for this tagname.  
						return this.db.taginfo.where("tagcolumn").equals(tagcolumn).toArray();
					}
					else if (tagtable !== ""){
						//tagname is not blank.  get tag info for this tagname.  
						return this.db.taginfo.where("tagtable").equals(tagtable).toArray();
					}
					else if (tagdb !== ""){
						//tagname is not blank.  get tag info for this tagname.  
						return this.db.taginfo.where("tagdb").equals(tagdb).toArray();
					}

					else{
						//tagname is not blank.  get tag info for this tagname.  
						//get all tags with this name every reference.  is this a topic?  
						return this.db.taginfo.where("tagname").equals(tagname).toArray();
					}
				}

			}

			return this.db.taginfo.where("tagname").equals(tagname).toArray();
		}
	}
	loadTags(tagdb, tagtable, tagcolumn, tagvalue=""){
		if (tagvalue ==""){
			//get all tags for this DB.  
			return this.db.taginfo.where("[tagdb+tagtable+tagcolumn]").equals([tagdb,tagtable,tagcolumn]).toArray();
		}
		else{
			return this.db.taginfo.where("[tagdb+tagtable+tagcolumn+tagvalue]").equals([tagdb,tagtable,tagcolumn,tagvalue]).toArray();
		}
	}

	saveTag(tagname, tagdb, tagtable, tagcolumn, tagvalue=""){
		//tagid is unique, but can be reused.  
		if (tagvalue == ""){
			tagvalue = tagname;
		}
		this.db.tags.where("tagname").equals(tagname).first().then((obj) => {
			var infoobj = {"tagname": tagname, "tagdb": tagdb, "tagtable": tagtable, "tagcolumn": tagcolumn, "tagvalue": tagvalue};
			this.db.tagsinfo.add(infoobj).then((id) => {
				console.log("added tag info with id " + id);
			});
		}).catch((err) => {
			console.log("error in saveTag: " + err);
			//if tagname not found, then add it.
			this.db.tags.add({"tagname": tagname, "tagdesc": ""}).then((id) => {
				console.log("added tag with id " + id);				
			});
		});

	}
}

class gitDB{
	//save any git repo info and cache locally.  
	//only download if not already in DB, or size doesnt match.  
	//gitcommits.push({"url": data[this.indexValue].html_url, "patch": commitdata.files[i].patch, "filename": commitdata.files[i].filename, "changes": commitdata.files[i].changes, "d": mydate, "selected": true});
	//gitbook.push({"url": this.url, "gitdata": bookdata[this.indexValue], "d": gitbookname, "content": data, "selected": true});
	constructor(){
		this.db = new Dexie("gitDB");
		this.ftsindex = FlexSearch.Index({});
		this.db.version(1).stores({
			gitrepos: "++id,[repo+branch]", //desc
			gitcommits: "[repo+branch],url,filename,d", //patch, changes
			gitbook: "[repo+branch],url,d", //gitdata, content
			gitcontents: "[repo+branch],url", //content 
		});
	}

	loadContents(repo, branch, url=""){
		if (url == ""){
			return this.db.gitcontents.where("[repo+branch]").equals([repo,branch]).toArray();
		}
		else{
			//get all contents for this repo and branch.  
			return this.db.gitcontents.where("url").equals(url).toArray();
		}

	}
	saveRepo(repo, branch, userid=0){
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
			//mycomments is the original transcript for video owner.  
			vids: "++id,[category+name+version],category,name,version,userid", //mycomments, videoblob (if local), otherwise remoteurl
			screenshots: "id,imid,userid,vidid,timestamp", //imgblob, ocrtext
			//files and/or links relevant to activity.  For now just text.  
			files: "++id,[category+name+version],category,name,version,fname,size,path,userid", //text, fileblob?, or remoteurl
		});

		this.ftsindex = FlexSearch.Index({});
		//really need FTS component.  Load all transcript etc for FTS.  
		//not sure how scalable this is, but I estimate perhaps 1000 local records = ~10MB max which browser should handle fine.  
		//may need to limit FTS load to 1000 records or so.
	}

	loadFTS(){
		this.db.vids.each((obj) => {
			this.ftsindex.update(obj.id, obj.category + " " + obj.name + " " + obj.mycomments);
		});
		this.db.screenshots.each((obj) => {
			this.ftsindex.update(obj.id, obj.ocrtext);
		});
		this.db.files.each((obj) => {
			//use path here as id.  
			this.ftsindex.update(obj.path, obj.category + " " + obj.name);
		});
	}

	saveFile(userid, category, name, version, filename, mycomments, text, size=0, remoteurl=null, cb=null){
		if (size==0){
			size = text.length;
		}
		//key here is path.  Not sure how we will generate this for uploaded files.  
		//try to save original if possible.  
		//yeah just overwrite if we get the same again.  
		let path = category + "/" + name + "/" + filename;
		var obj = {"userid": userid, "category": category, "name": name, "version": version, "filename": filename, "mycomments": mycomments, "text": text, "size": size, "path": path, "remoteurl": remoteurl};
		this.db.files.put(path, obj).then((id) => {
			console.log("added file with id " + id);
			this.ftsindex.update(obj.path, obj.category + " " + obj.name + " " + obj.mycomments);
			if (cb != null){
				cb(id); //callback to add file.  
				//indicate we have completed action.  
			}
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

	loadVideo(id, category="", name="", version=0){
		//load video by id, or category, name, version.  
		if (id != null){
			return this.db.vids.get(id);
		}
		else{
			
			return this.db.vids.where("[category+name+version]").equals([category,name,version]).first(); 
		}
	}

	saveScreenshot(id, vidid, secs, imgblob, ocrtext, cb=null){
		var obj = {"id": vidid + "_" + id, "imid": id, "vidid": vidid, "secs": secs, "imgblob": imgblob, "ocr": ocrtext};
		this.db.screenshots.add(obj).then((ida) => {
			console.log("added screenshot with id " + ida);
			this.ftsindex.add(vidid + "_" + id, obj.ocrtext);
			if (cb != null){
				cb(ida); //callback to complete.  
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

	
	getScreenshots(vidid){
		return this.db.screenshots.where("vidid").equals(vidid).sortBy("imid");
	}

	getScreenshotsA(imgrecs=[]){
		//get all screenshots for these video ids.  
		return this.db.screenshots.bulkGet(imgrecs);


	}

	getSimilar(text="", limit=10){
		//use FTS index to find similar.  
		//index.search({tag:"cat"})
		return this.ftsindex.search(text, {limit: limit});

	}
}



class vecDB{
	//save all vectors and vector info.
	//text should be unique key here.  

	constructor(){
		
		this.db = new Dexie("vecDB");
		this.db.version(1).stores({
			vec: "&text,user, topic", //vector, jaccardtext
		});
	}

	//pass array of topics to filter.
	getSimilar(vec, topic=[], user=0, limit=10, method="cosine"){
		//get all vectors and find similar.
//		return this.db.vec.where("user").equals(user).toArray().then((allvecs) => {
		if (topic.length > 0){
			return this.db.vec.where("topic").equals(topic).toArray().then((allvecs) => {
				let sims = [];
				allvecs.forEach((v) => {
					let sim = 0;
					if (method == "cosine"){
						sim = cosineSimilarity(vec, v.vector);
					}
					else if (method == "euclidean"){
						sim = euclideanDistance(vec, v.vector);
					}
					else if (method == "jaccard"){
						sim = calculateJaccardSimilarity(vec, v.jaccardtext);
					}
					sims.push({"id": v.id, "vector": v.vector, "text": v.text, "topic": v.topic, "sim": sim});
				});
				//sort by sim desc
				sims.sort((a, b) => b.sim - a.sim);	
				return sims.slice(0, limit);
			});
		}
		else{
			return this.db.vec.toArray().then((allvecs) => {
				let sims = [];
				allvecs.forEach((v) => {
					let sim = 0;
					if (method == "cosine"){
						sim = cosineSimilarity(vec, v.vector);
					}
					else if (method == "euclidean"){
						sim = euclideanDistance(vec, v.vector);
					}
					else if (method == "jaccard"){
						sim = calculateJaccardSimilarity(vec, v.jaccardtext);
					}
					sims.push({"id": v.id, "vector": v.vector, "text": v.text, "topic": v.topic, "sim": sim});
				});
				//sort by sim desc
				sims.sort((a, b) => b.sim - a.sim);	
				return sims.slice(0, limit);
			}
			);
		}
	}
		
	getVec(text, userid=0){
		return this.db.vec.where("text").equals(text).first();

	}

	saveVec(text, vector, topic, userid=0, cb=null){
		const arrayOfWords = text.split(' ').map(word => word.trim()).filter(word => word !== '');
		const jaccardtext = Array.from(new Set(arrayOfWords)); //unique words only.


		this.getVec(text, userid).then((exists) => {
			var obj = {"userid": userid, "text": text, "vector": vector, "topic": topic, "jaccardtext": jaccardtext};
			if (typeof(exists) !=="undefined" && exists != null && exists.length > 0){
				//already exists.  
				exists[0].vector = vector;
				exists[0].jaccardtext = jaccardtext;
				exists[0].topic = topic;
				this.db.vec.put(exists[0]).then((id) => {
					console.log("updated VEC with id " + id);
	//				this.ftsindex.add(vidid + "_" + id, lang);  
					if (cb != null){
						cb(id); //callback to complete.  
					}
				});
	
			}
			else{
				this.db.vec.add(obj).then((id) => {
					console.log("added VEC with id " + id);
	//				this.ftsindex.add(vidid + "_" + id, lang);  
					if (cb != null){
						cb(id); //callback to complete.  
					}
				});
			}
	
		}).catch((err) => {
			console.log("error in getVec: " + err);
		});

	}

}



function cosineSimilarity(vectorA, vectorB) {
	if (vectorA.length !== vectorB.length) {
	  throw new Error("Vectors must have the same length.");
	}
  
	let dotProduct = 0;
	let magnitudeA = 0;
	let magnitudeB = 0;
  
	for (let i = 0; i < vectorA.length; i++) {
	  dotProduct += vectorA[i] * vectorB[i];
	  magnitudeA += vectorA[i] * vectorA[i];
	  magnitudeB += vectorB[i] * vectorB[i];
	}
  
	magnitudeA = Math.sqrt(magnitudeA);
	magnitudeB = Math.sqrt(magnitudeB);
  
	const magnitudeProduct = magnitudeA * magnitudeB;
  
	if (magnitudeProduct === 0) {
	  return 0; // Handle cases where one or both vectors are zero vectors
	}
  
	return dotProduct / magnitudeProduct;
  }

  function euclideanDistance(vector1, vector2) {
	if (vector1.length !== vector2.length) {
	  throw new Error("Vectors must have the same dimension.");
	}
  
	let sumOfSquaredDifferences = 0;
	for (let i = 0; i < vector1.length; i++) {
	  const difference = vector1[i] - vector2[i];
	  sumOfSquaredDifferences += difference * difference;
	}
  
	return Math.sqrt(sumOfSquaredDifferences);
  }
  
  function calculateJaccardSimilarity(arr1, arr2) {
	// Convert arrays to Sets for efficient set operations
	const set1 = new Set(arr1);
	const set2 = new Set(arr2);
  
	// Calculate the intersection of the two sets
	// Filter elements of set1 that are also present in set2
	const intersection = new Set([...set1].filter(x => set2.has(x)));
  
	// Calculate the union of the two sets
	// Combine all unique elements from both sets
	const union = new Set([...set1, ...set2]);
  
	// Handle the case where the union is empty to avoid division by zero
	if (union.size === 0) {
	  return 0; // Or handle as an error, depending on requirements
	}
  
	// Calculate Jaccard similarity
	const similarity = intersection.size / union.size;
  
	return similarity;
  }  