
//dont need to load anything else, this is default language.  
keymaps["meta"].chat = function (transcript){
    let executed = false;
    transcript = transcript.trim();
    //find and handle command.  

    if (transcript.toLowerCase().startsWith("highlight")){
        //skip to next event?  
        tokens = transcript.split(" ");
        //logic check is in prior function
        if (tokens.length > 4){
            let x = parseFloat(tokens[1]);
            let y = parseFloat(tokens[2]);
            let x1 = parseFloat(tokens[3]);
            let y1 = parseFloat(tokens[4]);
            highlightVideo(x, y, x1, y1);
            executed = true;

        }
        else if (tokens.length > 2){
            let x = parseFloat(tokens[1]);
            let y = parseFloat(tokens[2]);
            highlightVideo(x, y);
            executed = true;
        }
    }

    else if (transcript.toLowerCase().startsWith("comment")){
        //make this comment to next event?  
        transcript = transcript.substr(transcript.indexOf(" ") + 1);
        transcript = "--" + transcript; //add -- to the start of the comment.
        return transcript; //return modified transcript
    }
    else if (transcript.toLowerCase().startsWith("skip")){
        //skip to next event?  
        tokens = transcript.split(" ");
        //logic check is in prior function
        if (tokens.length > 1 && tokens[1] !=""){
            let skip = parseFloat(tokens[1]);
            skipVideo(skip);
            executed = true;
        }
    }
    else if (transcript.toLowerCase().startsWith("jump")){
        //skip to next event?  
        tokens = transcript.split(" ");
        //logic check is in prior function
        if (tokens.length > 1 && tokens[1] !=""){
            let jump = parseFloat(tokens[1]);
            jumpVideo(jump);
            executed = true;
        }
    }
    else if (transcript.toLowerCase() == "back"){
        //skip to previous event?
    }
    else if (transcript.toLowerCase() == "stop"){
        window.speechSynthesis.cancel();
        executed = true;
    }
    else if (transcript.toLowerCase() == "play"){
        //play video
        playVideo();
        executed = true;
    }
    else if (transcript.toLowerCase() == "pause"){
        //pause video
        pauseVideo();
        executed = true;
    }
    else if (transcript.toLowerCase().startsWith("set octave")){
        //adjust playback speed of video.  
        tokens = transcript.split(" ");
        //logic check is in prior function
        if (tokens.length > 2 && tokens[2] !=""){
            if (tokens.length > 3 && tokens[3] !=""){
                let octave = parseInt(tokens[2]);
                lang = tokens[3];
                setOctave(octave, lang);
                executed = true;

            }
            else{
                let octave = parseInt(tokens[2]);
                setOctave(octave);
                executed = true;
            }


        }
    }
    else if (transcript.toLowerCase().startsWith("set speed")){
        //adjust playback speed of video.  
        tokens = transcript.split(" ");
        //logic check is in prior function
        if (tokens.length > 2 && tokens[2] !=""){
            let speed = parseFloat(tokens[2]);
            setVideoSpeed(speed);
            executed = true;
        }
    }
    else if (transcript.toLowerCase().startsWith("set volume")){
        //adjust playback speed of video.  
        tokens = transcript.split(" ");
        //logic check is in prior function
        if (tokens.length > 2 && tokens[2] !=""){
            let volume = parseFloat(tokens[2]);
            if (volume == 0.5){
                //mute piano sounds
                playfeedback = false;
            }
            else if (volume == 1){
                //unmute piano sounds
                playfeedback = true;
            }
            else{
                //maybe want a different function for this, but for now its ok I guess.  
                setFeedbackVolume(volume);
            }
            setVideoVolume(volume);
            executed = true;
        }
    }
    //filter clear, filter add, filter remove
    else if (transcript.toLowerCase().startsWith("filter clear")){
        tokens = transcript.split(" ");
        if (tokens.length > 2){
            let func = tokens[2];
            if (func == "word"){
                //clear filter by word                
            }
            else if (func == "language"){
                //clear filter by language

            }
            else if (func == "user"){
                //clear filter by user, probably need to be able to name users.  
            }
            executed = true;
        }
    }

    else if (transcript.toLowerCase().startsWith("filter add")){
        tokens = transcript.split(" ");
        if (tokens.length > 3){
            let func = tokens[2];
            let filter = "";
            if (func == "word"){
                //filter by word
                filter = tokens.slice(3, tokens.length).join(" ");
            }
            else if (func == "language"){
                //filter by language
                filter = tokens.slice(3, tokens.length).join(" ");
            }
            else if (func == "user"){
                //filter by user, probably need to be able to name users.  
                filter = tokens.slice(3, tokens.length).join(" ");
            }
            executed = true;
        }
    }
    else if (transcript.toLowerCase().startsWith("filter remove")){
        tokens = transcript.split(" ");
        if (tokens.length > 3){
            let func = tokens[2];
            let filter = "";
            if (func == "word"){
                //filter by word
                filter = tokens.slice(3, tokens.length).join(" ");
            }
            else if (func == "language"){
                //filter by language
                filter = tokens.slice(3, tokens.length).join(" ");
            }
            else if (func == "user"){
                //filter by user, probably need to be able to name users.  
                filter = tokens.slice(3, tokens.length).join(" ");
            }
            executed = true;
        }
    }
    else if (transcript.toLowerCase().startsWith("change language")){
        //
        tokens = transcript.split(" ");
        if (tokens.length > 3){
            midi = tokens[tokens.length-1];
            lang = tokens.slice(2, tokens.length-1).join(" ");
            changeLanguage(lang, midi);
            executed = true;
        }
        else if (tokens.length == 3){
            //accept midi or language name.  
            midi = tokens[2];
            if (hasNumber(midi)){
                changeLanguage(midi);
            }
            else{
                lang = tokens[2];
                selectLanguage(lang);
            }
            executed = true;
        }
    }
    else if (transcript.toLowerCase().startsWith("add language")){
        //
        tokens = transcript.split(" ");
        if (tokens.length > 3){
            midi = tokens[tokens.length-1];
            lang = tokens.slice(2, tokens.length-1).join(" ");
            if (hasNumber(midi)){ //check if we have actually put in the midi.  
                addLanguage(lang.trim(), midi);
                executed = true;
            }

        }
    }
    else if (transcript.toLowerCase().startsWith("add word")){
        tokens = transcript.split(" ");
        if (tokens.length > 3){
            midi = tokens[tokens.length-1];
            //for now single word?  I dont think it matters, logic allows for multiple words.  
            //but we do need to time the speech and the midi well if we want to use the 4s timeout.  
            let word = tokens.slice(2, tokens.length-1).join(" ");
            if (hasNumber(midi)){ //check if we have actually put in the midi.
                let newmidi = addWord(word.trim(), midi);
                transcript = transcript.replace(midi, newmidi); //replace midi with new midi
                transcript = currentlanguage + ":" + transcript; //add language to transcript
                return transcript; //return modified transcript
            }
        }
    }
    else if (transcript.toLowerCase().startsWith("add tag")){
        tokens = transcript.split(" ");
        if (tokens.length >= 3){
            midi = tokens[tokens.length-1];
            //for now single word?  I dont think it matters, logic allows for multiple words.  
            //but we do need to time the speech and the midi well if we want to use the 4s timeout.  
            let tag = tokens.slice(2, tokens.length-1).join(" ");
            if (hasNumber(midi)){ //check if we have actually put in the midi.
                addTag(tag.trim(), "", midi);
                executed = true;
            }
            else{
                tag = tokens.slice(2, tokens.length).join(" ");
                addTag(tag.trim());
                executed = true;
            }
        }
    }
    else if (transcript.toLowerCase().startsWith("remove tag")){
        tokens = transcript.split(" ");
        if (tokens.length >= 3){
            midi = tokens[tokens.length-1];
            //for now single word?  I dont think it matters, logic allows for multiple words.  
            //but we do need to time the speech and the midi well if we want to use the 4s timeout.  
            let tag = tokens.slice(2, tokens.length-1).join(" ");
            if (hasNumber(midi)){ //check if we have actually put in the midi.
                console.log("error removing tag " + tag.trim() + " " + midi); 
                removeTag(tag.trim(), "", midi);
                executed = true;
            }
            else{
                tag = tokens.slice(2, tokens.length).join(" ");
                removeTag(tag.trim());
                executed = true;
            }
        }
    }

    
    return executed;

}
