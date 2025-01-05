var db = null;

async function train(){
    await transferRecognizer.train({
        epochs: 25,
        callback: {
            onEpochEnd: async (epoch, logs) => {
            console.log(`Epoch ${epoch}: loss=${logs.loss}, accuracy=${logs.acc}`);
            }
        }
        });
    const serialized = transferRecognizer.serializeExamples();
    //Uncaught (in promise) RangeError: Maximum call stack size exceeded
//    const base64String = btoa(String.fromCharCode.apply(null, new Uint8Array(serialized)));
//    localStorage.setItem('speechcommands', base64String); 

    var request = window.indexedDB.open("speechcommands");

    request.onerror = event => {
    console.error("Database error: " + event.target.errorCode);
    };
    request.onsuccess = event => {
    db = event.target.result;
    var trans = db.transaction("speechcommands", 'readwrite'); // or "readwrite"
    trans.objectStore("speechcommands").put(serialized, "test");
    };


    
}

async function listen(){
    //#https://github.com/tensorflow/tfjs-models/blob/master/speech-commands/src/browser_fft_recognizer.ts
    //Error: Mismatch between the last dimension of model's output shape (20) and number of words (5).
    var words = transferRecognizer.wordLabels();
    while (words.length < 19){
        words = transferRecognizer.wordLabels();
        console.log("generating fake data ... be quiet...");
        var entry = words.length.toString();
        await transferRecognizer.collectExample("noise" + entry);
        await transferRecognizer.collectExample("noise" + entry);        
    }

    await transferRecognizer.listen(result => {
        // - result.scores contains the scores for the new vocabulary, which
        //   can be checked with:
            const words = transferRecognizer.wordLabels();
            // `result.scores` contains the scores for the new words, not the original
            // words.
            for (let i = 0; i < words.length; ++i) {
                console.log(`score for word '${words[i]}' = ${result.scores[i]}`);
            }
            scores = Array.from(result.scores).map((s, i) => ({score: s, word: words[i]}));
            // Find the most probable word.
            scores.sort((s1, s2) => s2.score - s1.score);
            document.querySelector('#console').textContent = scores[0].word;
        }, 
        {
            probabilityThreshold: 0.75
        }); //adjust if necessary.  Maybe 0.8
    
}

async function collect(str){
    await transferRecognizer.collectExample(str);
    console.log(transferRecognizer.countExamples());
}

const baseRecognizer = speechCommands.create('BROWSER_FFT');
let transferRecognizer;

async function app() {
    //'18w' (default): The 20 item vocaulbary, consisting of: 'zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'up', 'down', 'left', 'right', 'go', 'stop', 'yes', and 'no', in addition to 'background_noise' and 'unknown'.
    
    await baseRecognizer.ensureModelLoaded();
    transferRecognizer = baseRecognizer.createTransfer('colors');

    // Each instance of speech-command recognizer supports multiple
    // transfer-learning models, each of which can be trained for a different
    // new vocabulary.
    // Therefore we give a name to the transfer-learning model we are about to
    // train ('colors' in this case).


    //        transferRecognizer.loadExamples(serialized);
    var request = window.indexedDB.open("speechcommands");

    request.onerror = event => {
    console.error("Database error: " + event.target.errorCode);
    };
    request.onsuccess = event => {
        db = event.target.result;
        if( db.objectStoreNames.contains("speechcommands") ){
            var trans = db.transaction("speechcommands");
            const request = trans.objectStore("speechcommands").get("test");
            request.onerror = (event) => {
            // Handle errors!
            };
            request.onsuccess = (event) => {
            // Do something with the request.result!
            console.log(`${request.result}`);
            transferRecognizer.loadExamples(request.result, clearExisting=false);
            //#https://github.com/tensorflow/tfjs-models/blob/master/speech-commands/src/browser_fft_recognizer.ts
            //Error: Mismatch between the last dimension of model's output shape (20) and number of words (3). still get this even with clearExisting=false
            console.log(transferRecognizer.countExamples());
            };
        }
        else{
        }
    };

    // This event is only implemented in recent browsers
    request.onupgradeneeded = (event) => {
        // Save the IDBDatabase interface
        const db = event.target.result;
    
        // Create an objectStore for this database
        const objectStore = db.createObjectStore("speechcommands", { autoIncrement:true });
    };            


    /*
    const b64String = localStorage.getItem('speechcommands');
    if (b64String !==null){
        const binaryString = atob(base64String);
        const uint8Array = new Uint8Array(binaryString.length);
    
        for (let i = 0; i < binaryString.length; i++) {
        uint8Array[i] = binaryString.charCodeAt(i);
        }
    
        const arrayBuffer = uint8Array.buffer; 

        transferRecognizer.loadExamples(arrayBuffer, clearExisting=false);
    }
    */
    // Call `collectExample()` to collect a number of audio examples
    // via WebAudio.
    /*
    document.querySelector('#console').textContent = 'red';
    await transferRecognizer.collectExample('red');
    document.querySelector('#console').textContent = 'green';
    await transferRecognizer.collectExample('green');
    document.querySelector('#console').textContent = 'blue';
    await transferRecognizer.collectExample('blue');
    document.querySelector('#console').textContent = 'red';
    await transferRecognizer.collectExample('red');
    // Don't forget to collect some background-noise examples, so that the
    // trasnfer-learned model will be able to detect moments of silence.
    document.querySelector('#console').textContent = 'NOISE';
    await transferRecognizer.collectExample('_background_noise_');
    document.querySelector('#console').textContent = 'green';
    await transferRecognizer.collectExample('green');
    document.querySelector('#console').textContent = 'blue';
    await transferRecognizer.collectExample('blue');
    document.querySelector('#console').textContent = 'NOISE';
    await transferRecognizer.collectExample('_background_noise_');
    // ... You would typically want to put `collectExample`
    //     in the callback of a UI button to allow the user to collect
    //     any desired number of examples in random order.
    */
    // You can check the counts of examples for different words that have been
    // collect for this transfer-learning model.
    console.log(transferRecognizer.countExamples());
    // e.g., {'red': 2, 'green': 2', 'blue': 2, '_background_noise': 2};

    // Start training of the transfer-learning model.
    // You can specify `epochs` (number of training epochs) and `callback`
    // (the Model.fit callback to use during training), among other configuration
    // fields.

    // After the transfer learning completes, you can start online streaming
    // recognition using the new model.

    // Stop the recognition in 10 seconds.
//    setTimeout(() => transferRecognizer.stopListening(), 10e3);

}
    
app();

