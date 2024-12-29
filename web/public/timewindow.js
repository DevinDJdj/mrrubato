
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


function logme(i){
    console.log(items[i]);
}
  var container = document.getElementById('timewindow');

  var items = new vis.DataSet();

  //#https://visjs.github.io/vis-timeline/examples/timeline/items/htmlContents.html
  var item7 = 'item7<br><a href="https://visjs.org" target="_blank">click here</a>';

// create data and a Timeline
var options = {};

  for (var i = 10; i >= 0; i--) { 
    items.add({
        id: i,
        content: "item " + i + '<a href="#" onclick="logme(' + i + ')";>item' + i + '</a>',
        start: new Date(new Date().getTime() + i*100000)
    });
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
  timeline = new vis.Timeline(container, items, null, options);
  timeline.on('select', function (properties) {
    console.log('selected items: ' + properties.items);
    console.log(items.get(properties.items));
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
    