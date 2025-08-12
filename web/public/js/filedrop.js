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

export function processFile(file) {
    // Example processing function, e.g., read the file or upload it.
    console.log("Processing file: " + file.name);
    // You can add your file processing logic here.
    // For example, you could read the file content or upload it to a server.
}
