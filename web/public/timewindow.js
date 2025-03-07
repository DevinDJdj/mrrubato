
var backx = 1544;
var backy = 0;
var timewindowitems;
var timewindowgroups;
var alphabet = '2ABCDEFGHIJKLMNOPQRSTUVWXYZ';
var timelinefn = {};
var currenttimelinestart = 0;
var currenttimelineend = 0;
var gcounter = 0;

function changeBackgroundImage() {
//        let headingID = document.getElementById("GFG");
    let headingID = document.getElementById("timewindow");
    headingID.style.backgroundImage = "url('test/prolltest.jpg')";
    headingID.style.backgroundSize = "1544px 352px"; //half size
    headingID.style.backgroundPosition ="-3000px 100px";
    headingID.style.backgroundPosition = "0px 0px";
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

function groupFromName(g){
    g = g.replace('web/public/', '');
    const parts = g.split('/');
    if (parts.length > 1){
        const folderPath = parts.slice(0, -1).join('/');
        g = folderPath;
    }

    exists = vgroups.get().findIndex(x => (x.content === g));
    if (exists == -1){
        parent = vgroups.get().findIndex(x => x.content === g.charAt(0).toUpperCase());
        //parent = vgroups.findIndex(x => x.content === g.charAt(0).toUpperCase());
        if (parent == -1){
            console.log("bad name " + g);
        }
        else{
            if (isDate(g)){
                return 0;
            }
            else{
                newGroup = gcounter++;
                vgroups.get(parent).nestedGroups.push(newGroup);
                vgroups.add({id: newGroup, treeLevel: 2, nestedGroups: [], content: g});
                return newGroup;
            }
        }
    }
    else{
        return exists;
    }
    /*
    var pos = alphabet.indexOf(g.charAt(0).toUpperCase());
    if (pos > -1){
        return pos;
    }
    else{
        return alphabet.length-1;
    }
    */
}


//hide groups..
function hideGroups(){
    let  allGroupIds = vgroups.getIds();
    let temp = asSequence(allGroupIds);
    //custom criteria
    if(condition1)
        temp = temp.filter(it => !it.startsWith("Test"));
    if(condition2) 
        temp = temp.filter(it => !it.startsWith("ABC"));
    temp = temp.map(it => vgroups.get(it)).toArray();
    timeline.setGroups(temp)
    //timeline.redraw();
}

//hide items.  
function hideItems()
{
    let  allItemIds = items.getIds();

    let temp = asSequence(allItemIds);
    //custom criteria
   if(condition1)
      temp = temp.filter(it => !it.startsWith("Test"));
   if(condition2)
     temp = temp.filter(it => !it.startsWith("ABC"));

    temp = temp.map(it => items.get(it)).toArray();
    timeline.setItems(temp);

}

function updateTimelineBook(gs, fn=null){
    fullstrings = {};
    for (const [k2, v2] of Object.entries(gs)) {	//k2 = date  //v2 = array of content entries.  
        topicstrings = {};
        fullstrings[k2] = "";

        for (const [k3, d] of Object.entries(v2)) { //k3 = entry num, d = topic contents.  
            if (!(d.topic in topicstrings)){
                topicstrings[d.topic] = d;
            }
            else{
                topicstrings[d.topic].content += "\n" + d.content;
            }
            fullstrings[k2] += d.content + "\n";


        }
        for (const [k4, d] of Object.entries(topicstrings)){
            //gitstr = `<a href="#" onclick="loadTopic('${d.topic}');">${shortenName(d.topic)}</a><br> `;
            gitstr = d.content;
            g = groupFromName(d.topic);
            myitem = {
                id: idcounter,
                group: g,
                btype: 'book',
                content: d.topic,
                title: gitstr,
                start: new Date(d.d.substring(0,4) + "-" + d.d.substring(4, 6) + "-" + d.d.substring(6,8)), 
                style: "background-color: rgb(228, 222, 199);"
            }
            timeline.itemsData.add(myitem);
            idcounter++;

        }



    }
    for (const [k5, d] of Object.entries(fullstrings)){
        gitstr = d;
        g = groupFromName(k5);
        myitem = {
            id: idcounter,
            group: g,
            btype: 'book',
            content: k5,
            title: gitstr,
            start: new Date(k5.substring(0,4) + "-" + k5.substring(4, 6) + "-" + k5.substring(6,8)), 
            style: "background-color: rgb(228, 222, 199);"
        }
        timeline.itemsData.add(myitem);
        idcounter++;
    }
    timeline.setGroups(vgroups);    
    /*
    var ONE_DAY_IN_MS = 1000 * 60 * 60 * 24;
    var now = new Date();
    var nowInMs = now.getTime();
    var lastWeek = nowInMs - 10*ONE_DAY_IN_MS;
    timeline.setWindow(lastWeek, nowInMs);
    */    

}

function updateTimeline(fn, hide=false){
//    gitcommits.push({"url": data[this.indexValue].html_url, "filename": commitdata.files[i].filename, "changes": commitdata.files[i].changes, "d": mydate, "selected": true});
    
    for (gi=0; gi<gitcommits.length; gi++){

        if (fn !==null && gitcommits[gi].filename != fn){

        }
        else{
            exists = timeline.itemsData.get({
                filter: function (item) {
                    //return id from timeline matching id in props.items
                    return item.content === gitcommits[gi].filename && item.title == gitcommits[gi].url;
                }
            });
            if (!exists || exists.length ==0){
                g = groupFromName(gitcommits[gi].filename);
                myitem = {
                    id: idcounter,
                    group: g,
                    content: gitcommits[gi].filename,
                    btype: 'commit',
                    title: gitcommits[gi].url,
                    start: gitcommits[gi].d, 
                    style: "background-color: rgb(125, 230, 139);"
                }
                timeline.itemsData.add(myitem);
                idcounter++;
            }
            else{
                if (hide){
                    //this is 
                    exists[0].style='background-color: rgb(125, 230, 139);display: none;'
                }
                else{
                    //show again
                    exists[0].style='background-color: rgb(125, 230, 139);'
                }
                timeline.itemsData.update(exists);

                timeline.redraw();

            }
        }

    }
    timeline.setGroups(vgroups);
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

  timewindowitems = new vis.DataSet();

  timewindowgroups = new vis.DataSet();

  //#https://visjs.github.io/vis-timeline/examples/timeline/items/htmlContents.html
  var item7 = 'item7<br><a href="https://visjs.org" target="_blank">click here</a>';

// create data and a Timeline
var options = {};

  for (var i = 10; i >= 0; i--) { 
//    addItem(0, "item " + i + '<a href="#" onclick="logme(' + i + ')";>item' + i + '</a>', new Date(new Date().getTime() + i*100000));

  }

  var vgroups = new vis.DataSet();
  for (var g = 0; g < alphabet.length; g++) {
    vgroups.add({id: g, treeLevel: 1, nestedGroups: [], content: alphabet.charAt(g)});
  }
  gcounter = g;
  // Configuration for the Timeline
  // specify options
  start = new Date(new Date().getTime() - 30*24*60*60*1000);
  end = new Date(new Date().getTime() + 1*24*60*60*1000);
  currenttimelinestart = start.toISOString().substring(0,10).replace(/-/g, '');
  currenttimelineend = end.toISOString().substring(0,10).replace(/-/g, '');

  var options = {
    height: "500px", //height and width adjustment
    maxHeight: "800px",
    width: "900px",
    verticalScroll: true,
    stack: true,
    zoomKey: 'ctrlKey',
    start: start,
    end: end,
    margin: {
        axis: 5, 
        item: 5
    },
    orientation: {
        axis: "top" //none
    },
    rollingMode: {
      follow: false,
      offset: 0.9
    },
    showTooltips: true,
    tooltip: {
        overflowMethod: 'flip',
        template: function(originalItemData, parsedItemData) {
            //retrieve changes here and put them in the code window.  
            var color = originalItemData.btype == 'commit' ? 'red' : 'black';
            return `<span style="color:${color}">${originalItemData.content}</span>`;
          }
    
    }
  };

  // create a Timeline
  timeline = new vis.Timeline(container, timewindowitems, null, options);
  timeline.setGroups(vgroups);
  timeline.on('select', function (properties) {
    console.log('selected items: ' + properties.items);
    console.log(timewindowitems.get(properties.items));
    });

    timeline.on("rangechange", function ({start, end}){
        //this appears to be a 30 Hz refresh rate.  Probably dont need that much.  
        //depends on the movement rate.  
        if (timecounter%30==0){
            //console.log(start.toString(), end.toString());
            changeBackgroundLoc(start, end);
        }
        timecounter++;
    });
    
    
    
    timeline.on("rangechanged", function({ start, end, byuser }) {
        //pick up both these.  
//      if (byuser){
        console.log(start.toString(), end.toString());

        //get start and end YYYYMMDD
        start = start.toISOString().substring(0,10).replace(/-/g, '');
        end = end.toISOString().substring(0,10).replace(/-/g, '');
        currenttimelinestart = start;
        currenttimelineend = end;
        //refresh the word graph opacity and fonts.  
        zoomTopic(selectedtopic);
        getBookRefs(); //git.js
        /*
        var itemsView = new vis.DataView(items, { filter: 
            function(data) { 
                if ((start < data.end || data.start < end)) {
                    if ($.inArray(data.group, visibleGroups) == -1) {
                        visibleGroups.push(data.group);
                    }
                    return true;
                }
                return false; 
            }
        });
        
        var groupsView = new vis.DataView(groups, { filter: 
            function(data) {
                return $.inArray(data.id, visibleGroups) > -1;
            }
        });
        */
//      }        
    });

$('#timewindow').resizable();
$("#timewindow").resize(function () {
    var ht = $(this).height();
    var wd = $(this).width();
    if (ht < 400){
        ht = 400;
    }
    timeline.setOptions({ height: ht, width: wd });
    //adjust other div height.  
    $('#wordcanvas').height(ht+180);
    svg.height(ht+180);


  });
    




  timeline.on("itemover", function (selection){
    // If you set `multiselect: false` or leave it unset then only one item can selected at once.
    // Therefore you can just use [0] to access the first item in the items array

    const item = timewindowitems.get(selection.item);  
    mouseOverGit(item.title, item.content);

    
    // If `multiselect: true` is set in the options then there could be multiple items selected.
    // The above code is therefore not valid, instead it must loop through the items.
    // Loop through these items.
    //   for (let i = 0; i < selection.items.length; i += 1){
    //     var item = items.get(selection.items[i]);
    //     console.log('select event - title:', i, item.title);
    //   }
  });  

  timeline.on("itemout", function (selection){
    // If you set `multiselect: false` or leave it unset then only one item can selected at once.
    // Therefore you can just use [0] to access the first item in the items array

    const item = timewindowitems.get(selection.item);  
    mouseOutGit(item.title, item.content);
    
    // If `multiselect: true` is set in the options then there could be multiple items selected.
    // The above code is therefore not valid, instead it must loop through the items.
    // Loop through these items.
    //   for (let i = 0; i < selection.items.length; i += 1){
    //     var item = items.get(selection.items[i]);
    //     console.log('select event - title:', i, item.title);
    //   }
  });  
  
// Alternatively register select event
timeline.on("select", function (selection){
    // If you set `multiselect: false` or leave it unset then only one item can selected at once.
    // Therefore you can just use [0] to access the first item in the items array
    if(selection.items.length > 0){
      const item = timewindowitems.get(selection.items[0]);  
      console.log('select event - title:', item.title);
      if (selection.event.type=="tap"){
          loadTopic(item.content);
      }
    }
    
    // If `multiselect: true` is set in the options then there could be multiple items selected.
    // The above code is therefore not valid, instead it must loop through the items.
    // Loop through these items.
    //   for (let i = 0; i < selection.items.length; i += 1){
    //     var item = items.get(selection.items[i]);
    //     console.log('select event - title:', i, item.title);
    //   }
  });  