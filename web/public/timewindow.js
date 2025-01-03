
var backx = 1544;
var backy = 0;
function changeBackgroundImage() {
//        let headingID = document.getElementById("GFG");
    let headingID = document.getElementById("timewindow");
    headingID.style.backgroundImage = 
"url('test/prolltest.jpg')";
    headingID.style.backgroundSize = "1544px 352px" //half size
    headingID.style.backgroundPosition ="-3000px 100px";
    headingID.style.backgroundPosition = "0px 0px"
//        timeline.zoomOut(1);
    }
function changeBackgroundLoc(start, end){
    let headingID = document.getElementById("timewindow");
    headingID.style.backgroundPosition = backx + "px " + backy + "px";
    backx--;
    //pixel calculation based on start/end here.  
    //y calculation based on iteration.  

//        backy++;
}


var timecounter = 0;
var idcounter = 0;

function updateTimelineBook(gs, fn=null){
    for (const [k2, v2] of Object.entries(gs)) {	//k2 = date  //v2 = array of content entries.  

        for (const [k3, d] of Object.entries(v2)) { //k3 = entry num, d = topic contents.  

            gitstr = `<a href="#" onclick="loadTopic('${d.topic}');">${shortenName(d.topic)}</a><br> `;
            myitem = {
                id: idcounter,
                group: 0,
                topic: d.topic,
                content: gitstr,
                start: new Date(d.d.substring(0,4) + "-" + d.d.substring(4, 6) + "-" + d.d.substring(6,8))
            }
            timeline.itemsData.add(myitem);
            idcounter++;

        }
    }
}

function updateTimeline(gitcommits, fn=null){
//    gitcommits.push({"url": data[this.indexValue].html_url, "filename": commitdata.files[i].filename, "changes": commitdata.files[i].changes, "d": mydate, "selected": true});
    for (gi=0; gi<gitcommits.length; gi++){

        if (fn !==null && gitcommits[gi].filename != fn){

        }
        else{
            myitem = {
                id: idcounter,
                group: 0,
                content: '<a href="' + gitcommits[gi].url + '" target="_blank">' + gitcommits[gi].filename + '</a>',
                start: gitcommits[gi].d
            }
            timeline.itemsData.add(myitem);
            idcounter++;
        }

    }

}

function addItem(group, content, start){
    timewindowitems.add({
        id: idcounter,
        group: group,
        content: content,
        start: start
    });
    idcounter++;
}

function logme(i){
    console.log(timewindowitems[i]);
}
  var container = document.getElementById('timewindow');

  var timewindowitems = new vis.DataSet();

  //#https://visjs.github.io/vis-timeline/examples/timeline/items/htmlContents.html
  var item7 = 'item7<br><a href="https://visjs.org" target="_blank">click here</a>';

// create data and a Timeline
var options = {};

  for (var i = 10; i >= 0; i--) { 
//    addItem(0, "item " + i + '<a href="#" onclick="logme(' + i + ')";>item' + i + '</a>', new Date(new Date().getTime() + i*100000));

  }

  // Configuration for the Timeline
  // specify options
  var options = {
    height: "100px", //height and width adjustment
    width: "900px",
    verticalScroll: true,
    zoomKey: 'ctrlKey',
    start: new Date(),
    end: new Date(new Date().getTime() + 1000000),
    margin: {
        axis: 5, 
        item: 5
    },
    orientation: {
        axis: "top" //none
    },
    rollingMode: {
      follow: true,
      offset: 0.5
    }
  };

  // create a Timeline
  timeline = new vis.Timeline(container, timewindowitems, null, options);
  timeline.on('select', function (properties) {
    console.log('selected items: ' + properties.items);
    console.log(timewindowitems.get(properties.items));
    });

    timeline.on("rangechange", function ({start, end}){
        //this appears to be a 30 Hz refresh rate.  Probably dont need that much.  
        //depends on the movement rate.  
        if (timecounter%30==0){
            console.log(start.toString(), end.toString());
            changeBackgroundLoc(start, end);
        }
        timecounter++;
    });
    
    
    
    timeline.on("rangechanged", function({ start, end }) {
        //pick up both these.  
      console.log(start.toString(), end.toString());
        
    });

$('#timewindow').resizable();
$("#timewindow").resize(function () {
    var ht = $(this).height();
    var wd = $(this).width();
    timeline.setOptions({ height: ht, width: wd });
    //adjust other div height.  
    cvheight = 360 - ht;
    if (cvheight < 10) cvheight = 10;
    $('#wordcanvas').height(cvheight);
    $('#wordcanvas').width(wd);

  });
    
// Alternatively register select event
timeline.on("select", function (selection){
    // If you set `multiselect: false` or leave it unset then only one item can selected at once.
    // Therefore you can just use [0] to access the first item in the items array
    if(selection.items.length > 0){
      const item = timewindowitems.get(selection.items[0]);  
      console.log('select event - title:', item.title);
      loadTopic(item.topic);
    }
    
    // If `multiselect: true` is set in the options then there could be multiple items selected.
    // The above code is therefore not valid, instead it must loop through the items.
    // Loop through these items.
    //   for (let i = 0; i < selection.items.length; i += 1){
    //     var item = items.get(selection.items[i]);
    //     console.log('select event - title:', i, item.title);
    //   }
  });  