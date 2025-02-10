
export var rssitems = [];

function parseHTML(html){
    const tempElement = document.createElement('div');
    tempElement.innerHTML = html;
    const decodedString = tempElement.textContent;    
    var regExp = /\(([^)]+)s\)/g;
    var replaceWith = "<a href=\"https://$1\">$1</a>";
    let formatted = decodedString.replace(regExp, function(match, capture){
        let timeindex = capture.lastIndexOf("=");
        if (timeindex < 0){
            return match;
        }
        else{
            return "<a href=\"https://" + capture + "\">" + getTimeFromSecs(capture.substring(timeindex+1)) + "</a>";
        }
    });    
    return formatted;
}

function getID(str){
    let idstr = str.substring(str.lastIndexOf('?')+1);
    idstr = idstr.replace(/[^0-9]/g, '');
    return idstr;
}

export function getRSS(d=""){
    let id = -1;
    if (urlParams["id"]){
        id = urlParams["id"];
    }

    if (d==""){
        let date = new Date();
        d = date.toISOString().slice(0,10).replace(/-/g,"");
    }
    

    fetch(rssurl + d.substring(0,4) + "/" + d + "/rss.xml")
    .then(response => response.text())
    .then(str => new window.DOMParser()
    .parseFromString(str, "text/xml"))
    .then(data => {
            // of the matched selector.
            const items = data.querySelectorAll("item");

            let htmlOutput = ``;
            /* The concatenation of htmlOutput 
               string is applied for each item 
               element of array. querySelector 
               fetches first element of the descendant */

            items.forEach(itemElement => {
                console.log(itemElement);
                htmlOutput += `
                    <div id=\"${getID(itemElement.querySelector("link").innerHTML)}\" >
                        <h3>                                               
                            <a href=
                            "/chat.html?query=${itemElement.querySelector("title").innerHTML}" 
                                   target="_blank" rel="noopener">                                
                                 ${itemElement.querySelector("title").innerHTML}
                                <button style=
                                "border-radius:8px;
                                background-color:rgb(32, 94, 170);
                                color:white;border:none">
                                     RSS
                                </button>
                            </a>                            
                        </h3>
                        <p>
                           ${parseHTML(itemElement
                        .querySelector("description").innerHTML)}
                        <p>                        
                    </div>
                    `;
            });
            rssitems = items;

            // Returns the htmlOutput string
            // in the HTML body element
            // Check whether your query returns null
            var input = 
                document.getElementById("RSSfeedID");
            if (input) {
                input.innerHTML = htmlOutput;
            }
            document.body.style.backgroundColor = "rgb(203, 245, 245)";

            setTimeout(() => {
                if (id > -1){
                    const element = document.getElementById(d + id);

                    // Scroll to the element
                    if (element) {
                      element.scrollIntoView(); 
                    }
//                    window.location.hash = d + id; 
                }
    
            }, "1000");
                    
        });


}        

