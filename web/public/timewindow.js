
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
function updateTimeline(gitcommits){
//    gitcommits.push({"url": data[this.indexValue].html_url, "filename": commitdata.files[i].filename, "changes": commitdata.files[i].changes, "d": mydate, "selected": true});
    for (gi=0; gi<gitcommits.length; gi++){

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
    addItem(0, "item " + i + '<a href="#" onclick="logme(' + i + ')";>item' + i + '</a>', new Date(new Date().getTime() + i*100000));

  }

  // Configuration for the Timeline
  // specify options
  var options = {
    height: "100px", //height and width adjustment
    width: "900px",
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
    