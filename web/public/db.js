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

