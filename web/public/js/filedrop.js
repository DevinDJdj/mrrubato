//filedrop setup.  

export function loadFileDrop() {
    //filedrop.js
    //load the filedrop component.  
    let dropZone = document.getElementById("drop_zone");
    if (dropZone) {
        dropZone.addEventListener("dragover", FUNCS.FILEDROP.handleDragOver, false);
        dropZone.addEventListener("drop", FUNCS.FILEDROP.handleFileSelect, false);
    } else {
        console.error("Drop zone not found.");
    }
}

export function handleDragOver(event) {
    event.stopPropagation();
    event.preventDefault();
    event.dataTransfer.dropEffect = "copy"; // Explicitly show this is a copy.
}

export function handleFileSelect(event) {
    event.stopPropagation();
    event.preventDefault();

    let files = event.dataTransfer.files; // FileList object.
    if (files.length > 0) {
        for (let i = 0; i < files.length; i++) {
            let file = files[i];
            console.log("File dropped: " + file.name);
            // Process the file as needed, e.g., upload or read it.
            FUNCS.FILEDROP.processFile(file);
        }
    } else {
        console.error("No files dropped.");
    }
}


function splitTextIntoChunks(text, recommendedLength=800, emptyLinesThreshold=3) {
    const lines = text.split(/\r?\n/);
    const chunks = [];
    let currentChunk = [];
    let consecutiveEmptyLines = 0;
    let totalLength = 0;
  
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
  
      if (line.trim() === "") { // Check for empty lines (after trimming whitespace)
        consecutiveEmptyLines++;
      } else {
        consecutiveEmptyLines = 0; // Reset count if a non-empty line is found
      }
  
      currentChunk.push(line);
        totalLength += line.length;
  
      if (consecutiveEmptyLines >= emptyLinesThreshold || totalLength > recommendedLength || i === lines.length - 1) {
        // If threshold met or end of text, add currentChunk to chunks
        chunks.push(currentChunk.join("\n")); // Join lines back with newlines
        currentChunk = []; // Start a new chunk
        totalLength = 0; // Reset length for new chunk
        consecutiveEmptyLines = 0; // Reset for next chunk
      }
    }
    return chunks;
}

export async function processFile(file) {
    // Example processing function, e.g., read the file or upload it.
    console.log("Processing file: " + file.name);
    //save to db.  
    //only in rec.html for now.  
    if (typeof(recDB) === 'undefined'){
        console.error("No recDB defined");
        return;
    }
    //fname
    //get date from filename.  
    //get text from file.  
    let text = "";
    
    //need better check here.  
    if (file && (file.type.startsWith("text/") || file.type.endsWith("/json"))){
        const reader = new FileReader();
        reader.onload = function(e) {
          document.getElementById('fullDocument').value = e.target.result;
          text = e.target.result;

          recDB.saveFile(0, $('#category').val(), recname, version, file.name, $('#mycomments').val(), text, 0, null, 
          function(res){
              console.log(res);
              $('#statusmessage').html('saved! ' + recname + ' ' + version + ' ' + file.name + '<br/>');
          });

          chunks = splitTextIntoChunks(text);
          for (let i=0; i<chunks.length; i++){
                vecDB.getEmbedding(chunks[i]).then((vector) => {
                    console.log("Embedding vector:", vector);
                    vecDB.saveVec(chunks[i], vector, $('#category').val(), 0, function(res){
                        console.log("Vector saved:", res);
                        $('#statusmessage').append(' Vector saved!<br/>');
                    });
                });
          }  
          //use JSON possibly for other things.  
          if (file.type.endsWith("/json")){
            try {
                let json = JSON.parse(text);
                console.log("Parsed JSON:", json);
            } catch (error) {
                console.error("Error parsing JSON:", error);
            }
          }

        }
        reader.readAsText(file);
    }    
    else{
        text = await processFileOCR(file);
        document.getElementById('fullDocument').value = text;
        recDB.saveFile(0, $('#category').val(), recname, version, file.name, $('#mycomments').val(), text, 0, null, 
        function(res){
            console.log(res);
            $('#statusmessage').html('saved! ' + recname + ' ' + version + ' ' + file.name + '<br/>');
        }
        );
    }
    return text;

    // You can add your file processing logic here.
    // For example, you could read the file content or upload it to a server.
}
