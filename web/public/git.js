var gitbook = [];
var gitcommits = [];

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
		  dataType: 'json',
		  async: false,
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
                gitcommits.push(obj);
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
       totalcnt = 10;
       for (j=0; j<bookdata.length && j< totalcnt; j++){
   //    for (j=vids.length-1; j> -1; j--){
           page = bookdata[j];
           console.log(page.download_url);
   
   //	   $.getJSON(commit.url,function(commitdata){
           $.ajax({
             url: page.download_url,
             dataType: 'text',
             async: false,
             success: function(data) {
                console.log(data);   
                const pathArray = this.url.split("/");
                const gitbookname = pathArray[pathArray.length - 1];
                gitbookname = gitbookname.split(".")[0];
                gitbook.push({"url": this.url, "name": gitbookname, "content": data});
                //data.sort((a, b) => a.date - b.date);
             }
           });
   
   
       }
   
   
    });

}
function getGitCommits(){
	//get github
    url = giturl + '/commits?sha=master';

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
