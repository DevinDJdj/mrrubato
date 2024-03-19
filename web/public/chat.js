var ChatID = 0;

function loadVideo(secs, v){
    if (v !=""){
        if (v == video){
            player.seekTo(secs);
        }
        else{
            video = v;
            player.loadVideoById(video);
            //load data and transcript from this video.  
            if (uid != null){

                ref = firebase.database().ref('/misterrubato/' + video);
                ref.on('value',(snap)=>{
                    if (snap.exists()){
                        item = snap.val();
                        console.log(snap.val());
                        $('#iterationsh').html(makeTimeLinks(snap.val().snippet.description))
                        
                        //get previous iterations of this.  Probably dont need here.  
                        title = snap.val().snippet.description.split('\n')[0];
                        console.log(title);
                    }
                });

                //should just use this object.  

                //get the data from the database.  
                firebase.database().ref('/misterrubato/' + video + '/comments/' + uid).once('value')
                .then((snapshot) => {
                    if (snapshot.exists()) {
                        loadPreviousComments(snapshot);
                    }
                    
                });

                firebase.database().ref('/misterrubato/' + video + '/transcript').once('value')
                        .then((snapshot) => {
                            if (snapshot.exists()){
                                loadTranscript(snapshot);
                            }
                            else{
                                console.log('No transcript');									
                                //should never occur
                            }
                        });
            }
            //ontimer.. wait for video to load.  
            setTimeout(() => {
                if (player.getPlayerState() == 1) {
                    player.seekTo(secs);
                }
                else {
                    ytSeconds = secs;
                    player.playVideo();
                }
            }, 2000);
        }
    }
}

function addChatRow(query, answer, source) {
    answer = answer.replaceAll("\n", "<br>");
    var t = document.getElementById("ChatTable");
    var rows = t.getElementsByTagName("tr");
    var r = rows[0];
    ChatID += 1;
    t.insertRow(1);
    r = rows[1]; //always insert after the header row any new info.  
    r.style.border = "1px solid #000"
    // the same as
    r.style.borderWidth = "1px";
    r.style.borderColor = "#000";
    r.style.borderStyle = "solid";
    for (i=0; i<4; i++){
        r.insertCell(i);
    }
    r.cells[0].innerHTML = ChatID;
    r.cells[1].innerHTML = query;
    r.cells[2].innerHTML = answer;
    r.cells[3].innerHTML = getSourceHTML(source, ChatID);
}


function getSourceHTML(sources, rowid){
    allsources = '<table><tr>';
    for (i=0; i<sources.length; i++){
        vid = getVidFromMetadata(sources[i].metadata);
        //get vid details
        allsources += '<td width="25%">';
        if ((i+rowid)%2==0){
            allsources += '<font color="red">';
        }
        allsources += makeTimeLinks(sources[i].content, vid);
        if ((i+rowid)%2==0){
            allsources += '</font>';
        }
        allsources += '</td>';
    }
    allsources += '</tr></table>';
    return allsources;

}

function getVidFromMetadata(m){
    vid = m.substring(m.lastIndexOf("/")+1, m.lastIndexOf("."));
    return vid;
}



function getSecsFromTime(time){
    minsec = time.split(":");
    if (minsec == time)
        return 0;
    //console.log(+parseInt(minsec[0])*60 + +parseInt(minsec[1]));
    return +parseInt(minsec[0])*60 + +parseInt(minsec[1]);
    
}

function makeTimeLinks(desc, vid){
    desc = desc.replaceAll("\n", "<br>");
//    desc = desc.replace(")", ")<br>");
    const regExp = /\(([^)]+)\)/g;
    regExp2 = /\d+\:\d\d?/g;
    const matches = [...desc.matchAll(regExp2)].flat();
    for (var i=0; i<matches.length; i++){
        secs = getSecsFromTime(matches[i]);
        if (secs > 0){
            desc = desc.replace(matches[i], '<a href="#" onclick="loadVideo(' + secs + ', &quot;' + vid + '&quot;);">' + matches[i] + '</a>');
        }

    }
//    console.log(matches);
    return desc;
}
