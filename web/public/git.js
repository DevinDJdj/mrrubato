var gitbook = [];
var gitcommits = [];

var gitstruct = {"bydate": {}, "bytopic": {}, "alltopics": ""}; //context holds sequential string.  
var gittoken = null;
var gitcurrentpath = "";
var gitcurrentcontents = "";
var gitcurrentcontentstype = "javascript";

var currenttopic = "NONE";
var currenttopicline = 0;
var currentrefline = 0;
var currentref = "NONE";
var chathistory = []; //keep history/transcript.  
var myCodeMirror = null;


function gitSignin(){
  localStorage.removeItem('gittoken');
  var gitprovider = new firebase.auth.GithubAuthProvider();
  gitprovider.addScope('repo');
  gitprovider.setCustomParameters({
     'allow_signup': 'false'
     });

  firebase
  .auth()
  .signInWithPopup(gitprovider)
  .then((result) => {
      /** @type {firebase.auth.OAuthCredential} */
      var credential = result.credential;

      // This gives you a GitHub Access Token. You can use it to access the GitHub API.
      gittoken = credential.accessToken;
      console.log(gittoken);
      localStorage.setItem("gittoken", gittoken);

      const octokit = new LLM.Octokit({
      auth: gittoken,
      });
      // The signed-in user info.
      var user = result.user;
      // IdP data available in result.additionalUserInfo.profile.
      // ...
  }).catch((error) => {
      // Handle Errors here.
      var errorCode = error.code;
      var errorMessage = error.message;
      // The email of the user's account used.
      var email = error.email;
      // The firebase.auth.AuthCredential type that was used.
      var credential = error.credential;
      if (typeof(credential.accessToken) !== "undefined"){
        gittoken = credential.accessToken;
        console.log(gittoken);
        localStorage.setItem("gittoken", gittoken);

        const octokit = new LLM.Octokit({
        auth: gittoken,
        });
  
      }
      // ...
  });

}

function gitDownloadCommits(data, dataTableGit){
    myarray = [];
	//lets limit the number we display.  
	totalcnt = 100;
    for (j=0; j<data.length && j< totalcnt; j++){
//    for (j=vids.length-1; j> -1; j--){
		commit = data[j];
        console.log(commit.url);

//	   $.getJSON(commit.url,function(commitdata){
		$.ajax({
		  url: commit.url,
      indexValue: j,
		  dataType: 'json',
		  async: false,
      beforeSend: function(xhr) {
        gittoken = localStorage.getItem('gittoken'); // Get the token from local storage
        if (gittoken) {
          xhr.setRequestHeader('Authorization', 'Bearer ' + gittoken);
        }
      },
		  success: function(commitdata) {
		  

		   console.log(commitdata);
		   console.log(commitdata.stats);

			for (i=0; i< commitdata.files.length; i++){
				console.log(commitdata.files[i].filename);
				console.log(commitdata.files[i].changes);
				console.log(commitdata.commit.committer.date);
				mydate = new Date(commitdata.commit.committer.date);
				tempdate = new Date(commitdata.commit.committer.date);
				tempdate.setMinutes(tempdate.getMinutes()+commitdata.files[i].changes);
				tag = { v: commitdata.files[i].filename, p: { link: commit.html_url }};
				var aTag = document.createElement('a');
				aTag.setAttribute('href',commit.html_url);
				aTag.innerText = " " + commitdata.files[i].filename;
				aTag.innerText += " " + commitdata.commit.committer.date;

				console.log(tag);
				obj = [ tag, commitdata.files[i].filename, mydate, tempdate ];
				//getIterations(vid.snippet.description, vid.snippet.publishedAt) ];
				console.log(obj);
				myarray.push(obj);
        gitcommits.push({"url": data[this.indexValue].html_url, "filename": commitdata.files[i].filename, "changes": commitdata.files[i].changes, "d": mydate, "selected": true});

			}
		  }
		});


    }

    return myarray;
}

async function gitChartCommits(data){
	var container = document.getElementById('gitchart');
	gitchart = new google.visualization.Timeline(container);
	chart = gitchart;
	dataTableGit = new google.visualization.DataTable();
    optionsGit = {
	     height: 300,
         title: 'Git',
         legend: { position: 'labeled' },
		 tooltip: {isHtml: true},
         crosshair: { trigger: 'both', orientation: 'both' },
		 timeline: {
			rowLabelStyle: {
				color: '#3399cc'
			}
		 },
         trendlines: {
           0: {
             type: 'polynomial',
             degree: 3,
             visibleInLegend: true,
           }
         }
       };
	   
	   
	dataTableGit.addColumn({ type: 'string', id: 'Name' });
//	dataTableGit.addColumn({type: 'string', id: 'Label' });
	dataTableGit.addColumn({type: 'string', role: 'tooltip', 'p': {'html': true}});
	dataTableGit.addColumn({ type: 'date', id: 'DatePlayed' });
	dataTableGit.addColumn({ type: 'date', id: 'DateEnded' });
	
//	dataTable.addColumn({ type: 'number', id: 'Iterations' });
//	dataTable.addColumn({ type: 'number', id: 'Duration' });
	
//	dataTable.addColumn({ type: 'number', id: 'Iteration#' });
    myarray = await gitDownloadCommits(data, dataTableGit);
	dataTableGit.addRows(myarray);

	console.log(myarray);




  google.visualization.events.addListener(chart, 'ready', readyHandlerGit);
  google.visualization.events.addListener(chart, 'select', selectHandlerGit);
  chart.draw(dataTableGit, optionsGit);

}


  
function getGitBook(){
    //get github
    url = giturl + '/contents/book';

   $.getJSON(url,function(bookdata){
       console.log(bookdata);       
       totalcnt = 40;
       for (j=0; j<bookdata.length; j++){
   //    for (j=vids.length-1; j> -1; j--){
           page = bookdata[j];
           console.log(page.download_url);
   
           if (j< totalcnt || getFileName(page.download_url) == "definitions"){
    //	   $.getJSON(commit.url,function(commitdata){
            $.ajax({
              url: page.download_url,
              indexValue: j,
              dataType: 'text',
  //             headers: {"Authorization": "Bearer " + gittoken},
              async: false,
              beforeSend: function(xhr) {
                gittoken = localStorage.getItem('gittoken'); // Get the token from local storage
                if (gittoken) {
                  xhr.setRequestHeader('Authorization', 'Bearer ' + gittoken);
                }
              },
                      success: function(data) {
  //                console.log(data);   
                  var pathArray = this.url.split("/");
                  var gitbookname = pathArray[pathArray.length - 1];
                  gitbookname = gitbookname.split(".")[0];
                  //this should be a date YYYYmmdd
                  gitbook.push({"url": this.url, "gitdata": bookdata[this.indexValue], "d": gitbookname, "content": data, "selected": true});
                  //data.sort((a, b) => a.date - b.date);
                  if (gitbook.length == bookdata.length || gitbook.length == totalcnt){
                    //need better way...
                    creategitStruct();
                    console.log(gitstruct);
                  }
              }
            });
          }   
   
       }
//       setTimeout(creategitStruct(), 10000);
   
   
    });

}

function parsegitBook(gb){
//coming in time sequence.  
  //read all context.  
  //split by topic.  
  const gblines = gb.content.split('\n');

  str = "";
  fullstr = "";
  gitstruct["bydate"][gb.d] = [];
  gitstruct["alltopics"] += gb.d + " "; //add book as well.  onclick add the needed book/d.txt
  incomment = false;
  inref = false;
  refstr = "";
  for (i=0; i<gblines.length; i++){
    str = gblines[i];
    if (str.startsWith("<!--")){ //start comment (ignore)
      incomment = true;
    }
    else if (str.startsWith("-->")){ //end comment
      incomment = false;
    }
    else if (str.startsWith(">")){ //CMD
      incomment = false;
    }
    else if (str.startsWith("##") || str.startsWith("#")){ //reference
      incomment = false;
      inref = true;
      gitstruct["allrefs"] += currentref + " ";
      gitstruct["all"] += currentref + " ";
      content = {"ref": currentref, "d": gb.d, "line": currentrefline, "content": refstr  };
      if (!(currentref in gitstruct["byref"])){
        gitstruct["byref"][currentref] = [];
      }
      gitstruct["byref"][currentref].push(content); //ordered by date.  

      currentref = str.slice(1).split(" ")[0];
      if (currentref.charAt(0) == "#"){
        currentref = currentref.slice(1);
      }
      currentrefline = i;
      refstr = "";
    }
    else if (str.startsWith("@@")){ //Question
      incomment = false;

    }
    else if (str.startsWith("--")){ //NOTE
      incomment = false;
    }
    else if (str.startsWith("-")){ //subtask
      incomment = false;
    }
    else if (str.startsWith("**")){ //TOPIC
      //add to current topic.  
      incomment = false;
      inref = false;
      gitstruct["alltopics"] += currenttopic + " ";
      gitstruct["all"] += currenttopic + " ";
      content = {"topic": currenttopic, "d": gb.d, "line": currenttopicline, "content": fullstr  };
      if (!(currenttopic in gitstruct["bytopic"])){
        gitstruct["bytopic"][currenttopic] = [];
      }
      gitstruct["bytopic"][currenttopic].push(content); //ordered by date.  

      gitstruct["bydate"][gb.d].push(content);
      currenttopic = str.slice(2).split(" ")[0];
      currenttopicline = i;
      fullstr = "";


    }
    if (!incomment){
      fullstr += str;
    }
    if (inref){
      refstr += str;
    }

  }

}

function creategitStruct(){
  gitbook.sort((a, b) => a.d - b.d);
  //tree by time/topic
  //also topic/time
  //reset struct
  gitstruct = {"bydate": {}, "bytopic": {}, "byref": {}, "alltopics": "", "allrefs": "", "all": ""}; //context holds sequential string.  


    for (j=0; j<gitbook.length; j++){
        console.log(gitbook[j].d);
//        console.log(gitbook[j].content);
        parsegitBook(gitbook[j]);

    }
    //any 
    loadTopic(gitbook[gitbook.length-1].d);
    loadTopicGraph(gitstruct["alltopics"]);
    

}

function loadfromGitBook(top){
  if (top in gitstruct["bytopic"]){
    console.log(gitstruct["bytopic"][top]);
  }

}

function getGitContents(path){
  url = giturl + '/contents/' + path + '?ref=' + gitbranch;
  gitcurrentpath = path;

   $.getJSON(url,function(data){
      console.log('git contents');
      console.log(data);
      console.log(atob(data.content));
      gitcurrentcontents = atob(data.content);

      $('#for_edit_code').text(gitcurrentpath);

      if (myCodeMirror == null){
        myCodeMirror = CodeMirror(document.getElementById("edit_code"), {
          value: gitcurrentcontents,
          mode:  gitcurrentcontentstype, 
          lineNumbers: true
        });
      }
      else{
        var editor = myCodeMirror;
        editor.getDoc().setValue(gitcurrentcontents);
        editor.setOption("mode", gitcurrentcontentstype);
      }
	});
  
}

function getgitSelected(start, end){
  //return books selected as well as commits selected.  
  console.log(start);
  console.log(end);
  var dstart = new Date(start *1000).toISOString().slice(0,10);
  dstart = dstart.replace('-', '');
  var dend = new Date(end*1000).toISOString().slice(0,10);
  dend = dend.replace('-', '');
  var numselected = 0;
  for (i=0; i<gitbook.length; i++){
    if (gitbook[i].d >= dstart && gitbook[i].d <= dend){
      gitbook[i].selected = true;
      numselected++;
    }
    else{
      gitbook[i].selected = false;
    }
  }
  return numselected + ' of ' + gitbook.length;
  //change selected for any book date.  

}

function loadTopicGraph(str){
  //this is input for word2vec struct.  
  //also update canvas for this.  
    $('#textdata').val(str);
  setTimeout(function(){$("#prepareData").click();}, 2000); 
  setTimeout(function(){$("#trainModel").click();}, 4000);
  
  setTimeout(function(){$("#inbut").click(); }, 12000);

  setTimeout(function(){$("stopbut").click();dotrain=false;}, 18000);

}

function loadTopicIterations(top){
  topics = gitstruct["alltopics"].split(" ");
  index = topics.lastIndexOf(top);
  topicstr = "";
  fulltopicstr = "";
  if (index > -1){
    t = topics.slice(index-7, index+3);
    for (j=0; j<t.length; j++){
      if (t[j] == top){
        topicstr += "<b>";
      }
      topicstr += `<a href="#" onclick="loadTopic('${t[j]}');">${t[j]}</a> `;
      if (t[j] == top){
        topicstr += "</b>";
      }
    }
  }
  fulltopicstr = topicstr;
  topicstr = "";
  index = topics.lastIndexOf(top, -(topics.length-index)-1);
  if (index > -1){
    t = topics.slice(index-5, index+5);
    for (j=0; j<t.length; j++){
      if (t[j] == top){
        topicstr += "<b>";
      }
      topicstr += `<a href="#" onclick="loadTopic('${t[j]}');">${t[j]}</a> `;
      if (t[j] == top){
        topicstr += "</b>";
      }
    }
  }
  fulltopicstr = topicstr + fulltopicstr;
  $('#recenttopics').html(fulltopicstr);


}

function isDate(top){
  if (top.startsWith("20")){
    return true;
  }
}
function loadTopic(top){
    if (isDate(top)){
      getGitContents("book/" + top + ".txt");
    }
    else{
      getGitContents(top);
    }
    loadfromGitBook(top); //search Git for this string **.... in gitbook and retrieve all.  
    //look through the latest commit info and if newer than RTDB entry, pull from git.  
    //Cache result in RTDB.  
    loadTopicIterations(top);
}

function getGitTree(){
  url = giturl + '/git/trees/' + gitbranch + '?recursive=true';

   $.getJSON(url,function(data){
      console.log('git tree');
      console.log(data);

	});

}

function getGitCommits(){
	//get github
    url = giturl + '/commits?sha=' + gitbranch;

	if (querydate !=null){
		url += "&until=" + querydate;
//		url += ""
	}
	
   $.getJSON(url,function(data){
       console.log(data);
	   gitChartCommits(data);
	});
}


function clickHandlerGit(sender) {
    var rowLabel = sender.target.textContent;
    var dataRows = dataTableGit.getFilteredRows([{
      column: 0,
      value: rowLabel
    }]);
    if (dataRows.length > 0) {
      var link = dataTableGit.getProperty(dataRows[0], 0, 'link');
	  console.log(link);
      window.open(link, '_blank');
    }
  }

  function selectHandlerGit() {
	var container = document.getElementById('gitchart');
	var selection = gitchart.getSelection();
  var message = '';
//  for (var i = 0; i < selection.length; i++) {
//		var item = selection[i];
		console.log("Selection");
		console.log(selection);
		console.log(dataTableGit.getValue(selection[0].row, 1));
      var link = dataTableGit.getProperty(selection[0].row, 0, 'link');
	  console.log(link);
      window.open(link, '_blank');
  
  }

  function readyHandlerGit() {
    var container = document.getElementById('gitchart');
      var labels = container.getElementsByTagName('text');
      Array.prototype.forEach.call(labels, function(label) {
  //      if (label.getAttribute('fill') === options.timeline.rowLabelStyle.color) {
          label.addEventListener('click', clickHandlerGit);
          label.setAttribute('style', 'cursor: pointer; text-decoration: underline;');
  //      }
      });
    }
  
  