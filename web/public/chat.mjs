var ChatID = 0;
var lastquery = '';
var MAX_LOCAL_QUERY_LENGTH = 60000;
var chatmessages = [];
var lastread = 0;
var reading = false;

export var chathistory = [];

function replaceLinksWithLastElement(str) {
    const linkRegex = /https?:\/\/[^\s"]+/g;
    return str.replace(linkRegex, (match) => {
        const urlParts = match.split('/');
        return urlParts[urlParts.length - 1]; 
    });
}

function insertCRs(answer){
    answer = answer.replace(/(\r\n|\n|\r)/g, "<br>");
    return answer;
}

function bold(text){
    var bold = /\*\*(.*?)\*\*/gm;
    var html = text.replace(bold, '<strong>$1</strong>');            
    return html;
}

function formatAnswer(answer){
    answer = replaceLinksWithLastElement(answer);
    answer = insertCRs(answer);
    answer = bold(answer);
    return answer;

}


function getSourceHTML(sources, rowid){
    let allsources = '<table><tr>';
    for (let i=0; i<sources.length; i++){
        let vid = getVidFromMetadata(sources[i].metadata);
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
    let vid = m.substring(m.lastIndexOf("/")+1, m.lastIndexOf("."));
    return vid;
}

function getFileName(m){
    let fn = m.substring(m.lastIndexOf("/")+1, m.lastIndexOf("."));
    return fn;
}


export function getLastQuery(){
    return lastquery;
}
export function setLastQuery(query){
    lastquery = query;
}

export function buildChatTable(){
    //return HTML table for chat history.  
}

export function addChatHistory(query, context, prompt="", topic="", sources=[]){
    //localprompt from config.js
    //currenttopic from git.js
    chathistory.push({"query": query, "prompt": prompt, "context": files, "topic": topic, "answer": '', "sources": sources, "timestamp": new Date().toISOString()});
    //send to firebase.  
    //dont need to send full content of files?  just the names for now.  Should be able to git files from certain point in time if needed.  
}

export function addChatRow(query, answer, prompt="", topic="", sources=[]) {
    chatmessages.push({"query": query, "answer": answer});
    let fanswer = formatAnswer(answer);
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
    for (let i=0; i<4; i++){
        r.insertCell(i);
    }
    r.cells[0].innerHTML = ChatID;
    r.cells[1].innerHTML = "@@" + query;
    if (ChatID%2==0){

        r.cells[2].innerHTML = "@@" + query + '<br><font color="red">==<br>' + fanswer + '</font>';
    }
    else{
        r.cells[2].innerHTML = "@@" + query + '<br><font color="black">==<br>' + fanswer + '</font>';
    }
    r.cells[3].innerHTML = getSourceHTML(sources, ChatID);

    //return non-html string
    return r.cells[2].textContent || r.cells[2].innerText || "";
}


export function GetRecentChat(){
    let ctx = "";
    for (let ci=0; ci<chatmessages.lengh; ci++){
        let a = chatmessages[ci].answer.replaceAll("**", "__");
        a = a.replaceAll("@@", "__");
        a = a.replaceAll("==", "--");
        ctx += "@@" + chatmessages[ci].query + "\n\n==" + a + "\n\n";
    }
    return ctx;
}
