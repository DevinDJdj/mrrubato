var ChatID = 0;
var lastquery = '';
var MAX_LOCAL_QUERY_LENGTH = 10000;
var lastread = 0;
var reading = false;
var localprompt = 'please use the following content.  Each page is marked by --PAGETITLE-- and --END PAGETITLE--.  \
                        Please keep the response to less than 500 words.  If further information is needed, the user will ask another question.  \
                        You are trying to help explain the content to the user.  \
                        Use primarily this content to answer the question at the very end of the content marked by "Question:"  \
                      \
    '

function replaceLinksWithLastElement(str) {
    const linkRegex = /https?:\/\/[^\s"]+/g;
    return str.replace(linkRegex, (match) => {
        const urlParts = match.split('/');
        return urlParts[urlParts.length - 1]; 
    });
}

function insertCRs(answer){
    answer = answer.replace("\n", "<br>");
    return answer;
}

function formatAnswer(answer){
    answer = replaceLinksWithLastElement(answer);
    answer = insertCRs(answer);
    return answer;

}
    
function addChatRow(query, answer, source) {
    fanswer = formatAnswer(answer);
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
    if (ChatID%2==0){
        r.cells[2].innerHTML = '<font color="red">' + fanswer + '</font>';
    }
    else{
        r.cells[2].innerHTML = '<font color="black">' + fanswer + '</font>';
    }
    r.cells[3].innerHTML = getSourceHTML(source, ChatID);

    //return non-html string
    return r.cells[2].textContent || r.cells[2].innerText || "";
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

function getFileName(m){
    fn = m.substring(m.lastIndexOf("/")+1, m.lastIndexOf("."));
    return fn;
}



