var gitbook = [];
var gitcommits = [];

var gitstruct = {"bydate": {}, "bytopic": {}, "alltopics": "", "allcontent": {}}; //context holds sequential string.  
var gittoken = null;
var gitcurrentpath = "";
var gitcurrentfolder = "";
var gitcurrentcontents = "";
var gitcurrentcontentstype = "javascript";
var gitcurrentscrollinfo = null;

var currenttopic = "NONE";
var selectedtopic = "NONE";
var currenttopicline = 0;
var currentrefline = 0;
var currentref = "NONE";
var chathistory = []; //keep history/transcript.  
var selectionhistory = [];
var myCodeMirror = null;

var definitions = {"REF": "##", "REF2": "#", "TOPIC": "**", "STARTCOMMENT": "<!--", "ENDCOMMENT": "-->", "CMD": ">", "QUESTION": "@@", "NOTE": "--", "SUBTASK": "-"};


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

function gitDownloadCommits(data, qpath=null){
   var myarray = [];
	//lets limit the number we display.  
	totalcnt = 100;
    for (j=0; j<data.length && j< totalcnt; j++){
//    for (j=vids.length-1; j> -1; j--){
		commit = data[j];
        console.log(commit.url);
        exists = gitcommits.find(x => x.url === commit.url);
//	   $.getJSON(commit.url,function(commitdata){
      if (!exists){
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
          gitcommits.push({"url": data[this.indexValue].html_url, "patch": commitdata.files[i].patch, "filename": commitdata.files[i].filename, "changes": commitdata.files[i].changes, "d": mydate, "selected": true});
          //timewindow.js
        }
        }
      });


      }
    }
    setTimeout(function (){if (myarray.length > 0) {gitChartCommits(myarray, qpath);} }, 5000);
  }

function gitChartCommits(myarray, qpath=null){
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
//    myarray = await gitDownloadCommits(data);
	dataTableGit.addRows(myarray);
  updateTimeline(gitcommits, qpath);

//	console.log(myarray);




  google.visualization.events.addListener(chart, 'ready', readyHandlerGit);
  google.visualization.events.addListener(chart, 'select', selectHandlerGit);
  chart.draw(dataTableGit, optionsGit);

}


function loadGitBook(){
  reponame = giturl.substring(giturl.search("repos/")+6);
  gitbookref = firebase.database().ref('/git/' + reponame + '/' + gitbranch + '/book');
gitbookref.once('value')
  .then((snap) => {
    if (snap.exists()){
          let books = snap.val();
          for (const [key, value] of Object.entries(books)) {
            gitbook.push(value);
              
          }    
          gitCompareRecent();
          //workaround, only load once
          setTimeout(creategitStruct(), 2000);
      }
  });

}

function gitCompareRecent(){
  gurl = giturl + '/contents/book?ref=' + gitbranch;

  $.getJSON(gurl,function(bookdata){
      console.log(bookdata);       

      for (j=0; j<bookdata.length; j++){
          page = bookdata[j];
          console.log(page.download_url);
          exists = gitbook.find(x => x.url === page.download_url);
          if (!exists || exists.gitdata.size !=page.size){


  
//           if (j< totalcnt || getFileName(page.download_url) == "definitions"){
   //	   $.getJSON(commit.url,function(commitdata){
           $.ajax({
             url: page.download_url,
             indexValue: j,
             exists: exists,
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
                 if (exists){
                   exists.content = data;
                   exists.gitdata = bookdata[this.indexValue];
                 }
                 else{
                   gitbook.push({"url": this.url, "gitdata": bookdata[this.indexValue], "d": gitbookname, "content": data, "selected": true});
                 }

                 //data.sort((a, b) => a.date - b.date);
             }
           });
         }   
  
      }
//       setTimeout(creategitStruct(), 10000);
  
  
   });

}
  
function getGitBook(){
  loadGitBook();
    //get github

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
  //load from book definitions file eventually.  
  for (i=0; i<gblines.length; i++){
    str = gblines[i];
    if (str.startsWith(definitions["STARTCOMMENT"])){ 
      //start comment (ignore)
        incomment = true;
    }
    else if (str.startsWith(definitions["ENDCOMMENT"])){ //end comment
      incomment = false;
    }
    else if (str.startsWith(definitions["CMD"])){ //CMD
      incomment = false;
    }
    else if (str.startsWith(definitions["REF"]) || str.startsWith(definitions["REF2"])){ //reference
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
      if (currentref.charAt(0) == definitions["REF2"]){
        currentref = currentref.slice(1);
      }
      currentrefline = i;
      refstr = "";
    }
    else if (str.startsWith(definitions["QUESTION"])){ //Question
      incomment = false;

    }
    else if (str.startsWith(definitions["NOTE"])){ //NOTE
      incomment = false;
    }
    else if (str.startsWith(definitions["SUBTASK"])){ //subtask
      incomment = false;
    }
    else if (str.startsWith(definitions["TOPIC"])){ //TOPIC
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
      fullstr += str + "\n";
    }
    if (inref){
      refstr += str + "\n";
    }

  }

}

function creategitStruct(){
  gitbook.sort((a, b) => a.d - b.d);
  //tree by time/topic
  //also topic/time
  //reset struct
  gitstruct = {"bydate": {}, "bytopic": {}, "byref": {}, "alltopics": "", "allrefs": "", "all": "", "allcontent": {}}; //context holds sequential string.  


    for (j=0; j<gitbook.length; j++){
        console.log(gitbook[j].d);
//        console.log(gitbook[j].content);
        parsegitBook(gitbook[j]);

    }
    //any 
    loadTopic(gitbook[gitbook.length-1].d);
    loadTopicGraph(gitstruct["alltopics"]);

    //for now only on load.  
    updateTimelineBook(gitstruct["bydate"]);
    

}

function loadfromGitBook(top){
  var prevcontents = gitcurrentcontents;
  if (isDate(top)){
    var d = parseInt(top);
    if (d in gitstruct["bydate"]){
      gitcurrentcontents = "";
      for (ti=0; ti<gitstruct["bydate"][d].length; ti++){
        gitcurrentcontents += gitstruct["bydate"][d][ti].content;
      }
    }
    else{
      getGitContents(top);
    }
  }
  else{
    if (top in gitstruct["bytopic"]){
      console.log(gitstruct["bytopic"][top]);
      gitcurrentcontents = "";
      for (ti=0; ti<gitstruct["bytopic"][top].length; ti++){
        gitcurrentcontents += "**" + gitstruct["bytopic"][top][ti].d + "\n";
        gitcurrentcontents += gitstruct["bytopic"][top][ti].content;
      }

    }
  }
  var editor = myCodeMirror;
  //adjust to pull from book 
  if (prevcontents !=gitcurrentcontents){
    gitcurrentcontentstype = setContentType("book.txt");    
    editor.setOption("mode", gitcurrentcontentstype);
    editor.getDoc().setValue(gitcurrentcontents);

    $('#for_edit_code').text(top);
  }

}


function setContentType(path){
  var fileExt = path.split('.').pop();
  if (fileExt == "py"){
    return "python";
  }
  else if (fileExt == "sh"){
    return "shell";
  }
  else if (fileExt == "html"){
    return "htmlmixed";
  }
  else{
    return "javascript";
  }
}

function getGitContents(path, load=true){ //load UI or not, if false, return string representation of info.  
  var ret = "";
  var prevcontents = gitcurrentcontents;
  var prevfolder = gitcurrentfolder;
  if (isDate(path) || path=="definitions"){ //workaround for now.  
    return getGitContents(bookfolder + "/" + path + ".txt", load);
    
  }


  url = giturl + '/contents/' + path + '?ref=' + gitbranch;
  gitcurrentpath = path;
  if (gitcurrentpath in gitstruct["allcontent"]){
    //cache, dont reload for now.  Not sure if we want this.  
    var editor = myCodeMirror;
    //adjust to pull from book 
    if (Array.isArray(gitstruct["allcontent"][gitcurrentpath])){
      var data = gitstruct["allcontent"][gitcurrentpath];
      gitcurrentfolder = gitcurrentpath;
      gitstr = "";
      for (di=0; di<data.length; di++){
        gitstr += `<a href="#" onclick="loadTopic('${data[di].path}');">${isFolder(data[di].type)}${shortenName(data[di].path)}${isFolder(data[di].type, true)}</a><br> `;

      }
      if (load){
        $('#topicstatus').html(path + "<br>" + gitstr);
      }
      else{
        gitcurrentfolder = prevfolder;
        gitcurrentcontents = prevcontents;
      }
      ret = gitstr;

    }
    else{
      gitcurrentcontents = gitstruct["allcontent"][gitcurrentpath];
      if (prevcontents !=gitcurrentcontents && load && gitcurrentcontents !=null){
        gitcurrentcontentstype = setContentType(gitcurrentpath);
        editor.setOption("mode", gitcurrentcontentstype);
        editor.getDoc().setValue(gitcurrentcontents);
        $('#for_edit_code').text(gitcurrentpath);
      }
      else{
        ret= gitcurrentcontents;
        gitcurrentcontents = prevcontents;
        gitcurrentfolder = prevfolder;
      }
    }
  }
  else{
    $.ajax({
      url: url,
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
        data = $.parseJSON(data);
//    $.getJSON(url,function(data){
          console.log('git contents');
          console.log(data);
          if (Array.isArray(data)){
            //this is a folder struct, separate handling.  
            gitstr = "";
            gitcurrentfolder = path;
            for (di=0; di<data.length; di++){
              gitstr += `<a href="#" onclick="loadTopic('${data[di].path}');">${isFolder(data[di].type)}${shortenName(data[di].path)}${isFolder(data[di].type, true)}</a><br> `;

            }
            $('#topicstatus').html(path + "<br>" + gitstr);
            gitstruct["allcontent"][gitcurrentpath] = data;
            return;
          }
          console.log(atob(data.content));
          gitcurrentcontents = atob(data.content);
          gitstruct["allcontent"][gitcurrentpath] = gitcurrentcontents;

          if (myCodeMirror == null){
            myCodeMirror = CodeMirror(document.getElementById("edit_code"), {
              value: gitcurrentcontents,
              mode:  gitcurrentcontentstype, 
              lineNumbers: true
            });
          }
          else{
            if (prevcontents !=gitcurrentcontents){
              var editor = myCodeMirror;
              //adjust to pull from book 
              gitcurrentcontentstype = setContentType(gitcurrentpath);
              editor.setOption("mode", gitcurrentcontentstype);
              editor.getDoc().setValue(gitcurrentcontents);
              $('#for_edit_code').text(path);
            }
          }

          var fpath = path.split("/")
          fpath.pop();
          if (fpath.join("/") !=gitcurrentfolder){
            getGitContents(fpath.join("/"));
            gitcurrentfolder = fpath.join("/");
          }
      },
      error: function(xhr, textStatus, errorThrown) { 
        console.log(url + " not found.  "); 
        gitstruct["allcontent"][gitcurrentpath] = null; //dont want to load this again.  
        $('#topicstatus').append("<br>" + path + " not found.") 
        $('#topicstatus').animate({
          scrollTop: $('#topicstatus')[0].scrollHeight}, "slow"
        );
      }
    });
  }
    return ret;
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

  setTimeout(function(){$("stopbut").click();dotrain=false;
    $(".u").each(function() {
      console.log(this);
      //adjust here.  
    });
  }, 18000);

}

function shortenName(top){
  topics = gitstruct["alltopics"].split(" ");
  var pathArray = top.split("/");
  var shortname = pathArray[pathArray.length - 1];

  filteredtopics = topics.filter(str => str.includes(shortname));
  if (filteredtopics.length > 1){
    return top;
  }
  else{
    return shortname;
  }
}

function isFolder(d,end=false){
  if (d=="dir"){
    if (end){
      return "</b>"
    }
    else{
      return "<b>"
    }
  }  
  else{
    if (end){
      return "";
    }
    else{
      return "./";
    }
  }
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
      topicstr += `<a href="#" onclick="loadTopic('${t[j]}');">${shortenName(t[j])}</a> `;
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
      topicstr += `<a href="#" onclick="loadTopic('${t[j]}');">${shortenName(t[j])}</a> `;
      if (t[j] == top){
        topicstr += "</b>";
      }
    }
  }
  fulltopicstr = topicstr + fulltopicstr;
  $('#recenttopics').html(fulltopicstr);


}

function loadSelectionHistory(){
  fullselection = "";
  for (si =0; si<selectionhistory.length; si++){
    fullselection += `<a href="#" onclick="loadTopic('${selectionhistory[si]}');">${shortenName(selectionhistory[si])}</a><br> `;

  }
  $('#selectionhistory').html(fullselection);
  $('#selectionhistory').animate({
    scrollTop: $('#selectionhistory')[0].scrollHeight}, "slow"
  );

//  $('#selectionhistory').scrollTop = $('#selectionhistory')[0].scrollHeight - $('#selectionhistory')[0].clientHeight;

}

function selectOpacity(top){
  const result = selectionhistory.find((element) => element === top);
  if (result){
    return 1;
  }
  else{
    return 0.6;
  }
}
function selectFont(top){
  const result = selectionhistory.find((element) => element === top);
  if (result){
    return 16;
  }
  else{
    return 10;
  }

}
function isDate(top){
  if (top.startsWith("20")){
    return true;
  }
}
function loadTopic(top){
    selectedtopic = top;

//    selectionhistory.unshift(top);
    var currentmode = $('#code_mode').find(":selected").val();
    if (currentmode == "GIT"){

      cont = getGitContents(top);
      if (cont !==null){
        selectionhistory.push(top);
      }

    }
    else if (currentmode=="BOOK"){
      loadfromGitBook(top); //search Git for this string **.... in gitbook and retrieve all.  
      selectionhistory.push(top);
    }
    loadSelectionHistory();

    zoomTopic(top);

    //look through the latest commit info and if newer than RTDB entry, pull from git.  
    //Cache result in RTDB.  
    loadTopicIterations(top);
    getGitCommits(null, top);

}

function getGitTree(){
  url = giturl + '/git/trees/' + gitbranch + '?recursive=true';

   $.getJSON(url,function(data){
      console.log('git tree');
      console.log(data);

	});

}

function getGitCommits(qdate=null, qpath=null){
	//get github
  if (isDate(qpath)){
    getGitCommits(qdate, bookfolder + "/" + qpath + ".txt");
    return;
  }

    url = giturl + '/commits?sha=' + gitbranch;

	if (qdate !=null){
		url += "&until=" + qdate;
//		url += ""
	}
  if (qpath !=null){
    url += "&path=" + qpath;
  }
	
  $.ajax({
    url: url,
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
      data = $.parseJSON(data);

       console.log(data);
       myarray = gitDownloadCommits(data, qpath);
    }
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
  
  