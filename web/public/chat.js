var ChatID = 0;
var lastquery = '';
var MAX_LOCAL_QUERY_LENGTH = 60000;
var chatmessages = [];
var lastread = 0;
var reading = false;
var localprompt = 'I am a software engineer, investigating the source code and notes provided.  \n\
                   please use ONLY the context provided to answer the @@Question.  \n\
                   Each topic is marked by ** for example **MYTOPIC \n\
                   Keep the response short and less than 300 words.  If further information is needed, the user will ask another question.  \n\
                   You are trying to help summarize and explain the key points of the content provided.  \n\
                   Explain the key points of the content provided.  Then try to make one suggestion to improve the source code.  \n\
                   Make a short summary answer to the question \n\
                   @@Question:  \n\
    '

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
    
function addChatRow(query, answer, source) {
    chatmessages.push({"query": query, "answer": answer});
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



