
function loadAllRecent(limit=20){
	var vrRef = firebase.database().ref(dbname);
	if (typeof(uid) != "undefined" && uid !==null){
	}
	//get mydate if exists.  
	if (querydate ==null || querydate == ""){ //if no date, get today.
		var now = new Date();
		now.setDate(now.getDate() + 1); //add a day so we get today as well.  
//			now.setMilliseconds(0);
		querydate = now.toISOString().substring(0,10);
//			mydate = now.toISOString().replace(/.000/, "");

	}
	else{
		//?date=2021-09-01
	}
//		ref.orderByChild('snippet/title').equalTo(title).on("value", function(snapshot) {
//		vRef.orderByChild('snippet/publishedAt').limitToLast(50).once("value")
	vrRef.orderByChild('snippet/publishedAt').endAt(querydate).limitToLast(limit).once("value")
	.then((recentsnapshot) => {
		if (recentsnapshot.exists()) {							

			console.log(recentsnapshot.val());
			recvideojson = recentsnapshot.val();
			vids = getRecent(recvideojson);
			recentdrawChart(vids);
			recentdrawDurationChart(vids);
		}			
	});


}



function getDuration(desc, vidtime){
    totaldur = 0;
    st = [];
	et = [];
	for (i=1; i< 20; i++){
	    fnd = "TRIAL#" + i;
		let ts = desc.indexOf(fnd);
		te = desc.indexOf(")", ts);
		if (ts > -1)
			st.push(getSecsFromTime(desc.substring(ts+(fnd.length)+2, te)));
	}
	for (i=1; i<20; i++){
	    fnd = "END#" + i;
		ts = desc.indexOf(fnd);
		te = desc.indexOf(")", ts);
		if (ts > -1)
			et.push(getSecsFromTime(desc.substring(ts+(fnd.length)+2, te)));
	}

	mydate = new Date(vidtime);
	for (i=0; i< st.length; i++){
	    if (et[i] !==null){
			totaldur += et[i] - st[i];
		}
	}
	//WORDS = 
//	et[st.length-1] - totaldur
    if (totaldur < 0)
	    totaldur = 1;
    return [totaldur, et[st.length-1] - totaldur];
}


function loadRecentTable(){
	recenttable = new DataTable('#RecentTable', {
		order: [[1, 'desc']],
		columns: [null, null, null, null, { width: 500 }],
		createdRow: function (row, data, dataIndex) {
			this.api()
			//2 causing table to become unbalanced
				.columns([3])
				.every(function () {
					let column = this;
					
					// Create select element
					let select = document.createElement('select');
					select.add(new Option(''));
					column.footer().replaceChildren(select);
	
					// Apply listener for user change in value
					select.addEventListener('change', function () {
						column
							.search(select.value, {exact: true})
							.draw();
					});
	
					// Add list of options
					column
						.data()
						.unique()
						.sort()
						.each(function (d, j) {
							select.add(new Option(d));
						});
				});
		},

	});


}

function addRecentRow(recentrow) {
	var aTag = document.createElement('a');
	aTag.setAttribute('href',domain + '/analyze.html?video=' + recentrow.id);

	if (typeof(getVideoJson) !== "undefined"){
		aTag.addEventListener('click', function(event) {
			event.preventDefault(); // Prevent default link behavior if needed
			// Function to execute on click
			console.log('Link clicked!');
			// Add your desired functionality here
			getVideoJson(recentrow.id);
		});	
	}
	aTag.innerText = " " + recentrow.snippet.title;
	desc = recentrow.snippet.description;
	fnd = desc.indexOf("MIDI");
	if (fnd < 0){
		fnd = recentrow.snippet.description.length -1
	}
	desc = desc.substring(0,fnd);

	recenttable.row
        .add([
            aTag,
			recentrow.snippet.publishedAt,
			recentrow.snippet.title,
			recentrow.status.privacyStatus,
//			"","","",
			desc
        ])
        .draw(false);    
}


function getRecent(recentvideojson){
	loadRecentTable();
    vids = [];
	for (const [key, value] of Object.entries(recentvideojson)) {	
	    //sort by date and list in some way.  
		//right now just like we do, most recent and least recent
		//need something better than this?  
		if (key !="users" && key !="watch"){
			vids.push(value);
		}
		
	}

	vids.sort(function(a, b) {
	   datea = new Date(a.snippet.publishedAt);
	   dateb = new Date(b.snippet.publishedAt);
	   
	  return dateb - datea;
	});		
	//now display the recent videos which are not published and which are published etc.  

	var mydiv = document.getElementById("recent");
	/*
	while (mydiv.firstChild) {
      mydiv.removeChild(mydiv.lastChild);
    }
	*/
	maxcnt = 100;
	for (it=0; it< vids.length && it < maxcnt; it++){
		var obj = vids[it];
		addRecentRow(obj);
		/*
		var aTag = document.createElement('a');
		aTag.setAttribute('href',domain + '/analyze.html?video=' + obj.id);
		
		fnd = obj.snippet.description.indexOf("MIDI");
		if (fnd < 0){
			fnd = obj.snippet.description.length -1
		}
		aTag.innerText = " " + it + obj.snippet.description.substring(0,fnd);
		aTag.innerText += " " + obj.snippet.publishedAt;
		//should really add a date driven graphic representation.  
		console.log(aTag);
		mydiv.appendChild(aTag);
		var br = document.createElement("br");
		mydiv.appendChild(br);
		*/
	}
	return vids;
	
    
}







function recentreadyHandler() {
	var container = document.getElementById('timeline');
    var labels = container.getElementsByTagName('text');
    Array.prototype.forEach.call(labels, function(label) {
//      if (label.getAttribute('fill') === options.timeline.rowLabelStyle.color) {
        label.addEventListener('click', recentclickHandler);
        label.setAttribute('style', 'cursor: pointer; text-decoration: underline;');
//      }
    });
  }


  function recentclickHandler(sender) {
    var rowLabel = sender.target.textContent;
    var dataRows = dataTable.getFilteredRows([{
      column: 0,
      value: rowLabel
    }]);
    if (dataRows.length > 0) {
      var link = dataTable.getProperty(dataRows[0], 0, 'link');
	  console.log(link);
      window.open(link, '_blank');
    }
  }

  function recentselectHandler(sender) {
	var container = document.getElementById('timeline');
	var selection = vidchart.getSelection();
  var message = '';
//  for (var i = 0; i < selection.length; i++) {
//		var item = selection[i];
		console.log("Selection");
		console.log(selection);
		console.log(dataTable.getValue(selection[0].row, 1));
      var link = dataTable.getProperty(selection[0].row, 0, 'link');
	  console.log(link);
      window.open(link, '_blank');
  }


  function recentdrawChart(vids) {
	var container = document.getElementById('timeline');
	var chart = new google.visualization.Timeline(container);
	vidchart = chart;
	dataTable = new google.visualization.DataTable();
    options = {
	     height: 300,
         title: 'Timeline',
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
	   
	   
	dataTable.addColumn({ type: 'string', id: 'Name' });
	dataTable.addColumn({type: 'string', role: 'tooltip', 'p': {'html': true}});
	dataTable.addColumn({ type: 'date', id: 'DatePlayed' });
	dataTable.addColumn({type: 'date', id: 'DateEnded' });
//	dataTable.addColumn({ type: 'number', id: 'Iterations' });
//	dataTable.addColumn({ type: 'number', id: 'Duration' });
	
//	dataTable.addColumn({ type: 'number', id: 'Iteration#' });
    myarray = [];
	//lets limit the number we display.  
	totalcnt = 100;
    for (j=0; j<vids.length && j< totalcnt; j++){
//    for (j=vids.length-1; j> -1; j--){
		vid = vids[j];
		mydate = new Date(vid.snippet.publishedAt);
		tempdate = new Date(vid.snippet.publishedAt);
		tempdate.setSeconds(tempdate.getSeconds()+getDuration(vid.snippet.description, vid.snippet.publishedAt)[0]);
		tag = { v: vid.snippet.title, p: { link: domain + '/analyze.html?video=' + vid.id + '' }};
		var aTag = document.createElement('a');
		aTag.setAttribute('href',domain + '/analyze.html?video=' + vid.id);
		aTag.innerText = " " + vid.snippet.description;
		aTag.innerText += " " + vid.snippet.publishedAt;

        console.log(tag);		
	    obj = [ tag, vid.snippet.title, mydate, tempdate ];
		//getIterations(vid.snippet.description, vid.snippet.publishedAt) ];
		console.log(obj);
		myarray.push(obj);
    }
	dataTable.addRows(myarray);




  google.visualization.events.addListener(chart, 'ready', recentreadyHandler);
  google.visualization.events.addListener(chart, 'select', recentselectHandler);
  chart.draw(dataTable, options);


}

function recentdrawDurationChart(vids){
	dataTableDur = new google.visualization.DataTable();
    options = {
	     height: 500,
		 isStacked: true,
         title: 'Duration',
         legend: { position: 'bottom' },
		 tooltip: {isHtml: true},
         crosshair: { trigger: 'both', orientation: 'both' },
		 timeline: {
			rowLabelStyle: {
				color: '#3399cc'
			}
		 }
       };

	dataTableDur.addColumn({ type: 'date', id: 'DatePlayed' });
//	dataTable.addColumn({ type: 'string', id: 'Name' });
	dataTableDur.addColumn({type: 'number', id: 'Duration' });
	dataTableDur.addColumn({type: 'number', id: 'Words Duration' });
	dataTableDur.addColumn({type: 'number', id: 'Aggregated Duration' });

    myarray = [];
	//lets limit the number we display.  
	totalcnt = 100;
	prevDate = null;
	aggDuration = 0;
    for (j=0; j<vids.length && j< totalcnt; j++){
//    for (j=vids.length-1; j> -1; j--){
		vid = vids[j];
		mydate = new Date(vid.snippet.publishedAt);
		if (prevDate === null)
		    prevDate = mydate;
		if (mydate.getDate() != prevDate.getDate()){
			aggDuration = 0;
		}
		duration = getDuration(vid.snippet.description, vid.snippet.publishedAt);
		aggDuration += duration[0];
		

	    obj = [ mydate, duration[0], duration[1], aggDuration ];
		//getIterations(vid.snippet.description, vid.snippet.publishedAt) ];
		console.log(obj);
		myarray.push(obj);
		prevDate = mydate;
    }
	dataTableDur.addRows(myarray);

	var container = document.getElementById('durationchart');
	var chart = new google.visualization.SteppedAreaChart(container);
	chart.draw(dataTableDur);

}
