//create management for dictionary.  
//edit = 5 keys
//do we want this start end structure?  
//perhaps an easier end structure.  
//add/edit word [12, 9, 10, 11, 12] .. [12,11,10,9,12]
//add/edit language [12, 2, 3, 4, 12] .. [12, 4, 3, 2, 12]
//change language [12, 5, 7, 12] .. [12, 7, 5, 12]

var langs = {};
var alllangs = {};
var langstart = {};
var langend = {};
var wordtimes = {};
var midiwords = {};


var currentwtindex = 0;
var currentvidtime = 0;
var wordplay = -1;

var vidbuffer = 10;
var dictable = null;
var DIC_LANG = 7;
var DIC_WORD = 0;
var DIC_PLAYALL = 1;
var DIC_TIMES = 4;
//config.js keybot
//do we want to allow for some function to adjust keybot/keytop?  

function loadLanguages(){
    ref = firebase.database().ref('/dictionary/languages');
	ref.on('value',(snap)=>{
	    if (snap.exists()){
            mylangs = snap.val();
            for (const [key, value] of Object.entries(mylangs)) {
                alllangs[value] = key;
            }                    
        }
    });

}

function loadDictionaries(user){
    //find language in midi
    //find language in words "change language base" "change language to base"
    //need to use this more.  Probably more convenient.  
//    dictable = new DataTable('#DictionaryTable');
        //column dropdown filter.  
        //not efficient but ok for now, really only want to call this once.  
        dictable = new DataTable('#DictionaryTable', {
            createdRow: function (row, data, dataIndex) {
                this.api()
                    .columns()
                    .every(function () {
                        let column = this;
        
                        // Create select element
                        let select = document.createElement('select');
                        select.add(new Option(''));
                        column.footer().replaceChildren(select);
        
                        // Apply listener for user change in value
                        select.addEventListener('change', function () {
                            column
                                .search(select.value, {exact: true})
                                .draw();
                        });
        
                        // Add list of options
                        column
                            .data()
                            .unique()
                            .sort()
                            .each(function (d, j) {
                                select.add(new Option(d));
                            });
                    });
            },

        });

    if (user==0){
        loadLanguages();
    }
    //go through midiarray.  
    //should be in order.  
    //find sequences we need.  
    //load base langauge to start.  
//    loadLanguage("base");

    cl = [];
    cle = [];
    for (i=0; i<midiarray[user].length-5; i++){
        if (midiarray[user][i] == keybot+12 && midiarray[user][i+1] == keybot+5 && midiarray[user][i+2] == keybot+7 && midiarray[user][i+3] == keybot+12){
            //change language (add language)
            cl.push(i);
        }
        else if (midiarray[user][i]==keybot+12 && midiarray[user][i+1] == keybot+7 && midiarray[user][i+2] == keybot+5 && midiarray[user][i+3] == keybot+12){
            cle.push(i);
        }
    }
    numlangs = 0;
    for (i=0; i<cl.length; i++){
        //change language
        tempmidi = midiarray[user].slice(cl[i], cle[i]+4);
        for (j=0; j<tempmidi.length; j++){
            tempmidi[j] = tempmidi[j] - keybot;
        }
        langmidi = tempmidi.join();
        if (typeof(alllangs[langmidi]) !=="undefined"){
            //find the language setting.  
            //so start base language = [12, 5, 7, 12]
            lang = alllangs[langmidi];

            if (typeof(langstart[lang]) === "undefined"){
                langstart[lang] = [];
                langend[lang] = [];
            }
            //keep sequential
            langstart[lang].push(cle[i]+4);

            if (cl.length > i+1){
                langend[lang].push(cl[i+1]);
            }
            else{
                langend[lang].push(midiarray.length);
            }
            loadLanguage(lang, user);
            numlangs++;
        }
    }

    if (numlangs == 0){
        //no language changes.  
        //just go through base language.  
        langstart["base"] = [0];
        langend["base"] = [midiarray[user].length];
        loadLanguage("base", user);
    }
    else{
        if (cl[0] > 0){
            langstart["base"] = [0];
            langend["base"] = [cl[0]];
            loadLanguage("base", user);
        }
    }

    //now go through the langstart and langend looking for words.  
    //need a better mechanism but for now just timeout to wait for all loadLanguage calls to complete.  
    setTimeout(function(){findWords(user);
        //set up to highlight video times
        setInterval(function(){
            updateVidTimes(user);     
            checkCommands();
        }, 1000);        
    }, 5000);

}

function findWords(user){
    for (const [key, value] of Object.entries(langstart)) {	
        for (j=0; j<value.length; j++){
            //maxwordlength
            temp = midiarray[user].slice(value[j], langend[key][j]);

            miditostrindex = [];
            tempstr = "";
            for (mi=0; mi<temp.length; mi++){
                miditostrindex.push(tempstr.length);
                tempstr += temp[mi].note + ",";
            }
            //get the representation of the notes.  
            //this is inside of the language representation.  
            //value[j] is start of this language.  
            //full array of midi.  
            //just go through words and find any instance.  
            for (const [k2, v2] of Object.entries(langs[key])) {	//k2 = length of midiseq, v2 = array of words
                for (const [k3, v3] of Object.entries(langs[key][k2])) { //k3 = midi seq, v3 = word
                    const indexes = [...tempstr.matchAll(new RegExp(k3, 'gi'))].map(a => a.index);
                    //is this fast enough?  if we have only a few words in the language yes.  
                    //but if we get lots of words, probably want to change this logic to build some sort of array search.  
                    //also really need to search from longest to shortest.  
                    //at the moment leave as is.  
                    console.log(indexes); // [2, 25, 27, 33]
                    if (typeof(wordtimes[key]) === "undefined"){                        
                        wordtimes[key] = {};
                        midiwords[key] = {};
                    }
                    for (i=0; i<indexes.length; i++){
                        if (typeof(wordtimes[key][v3]) === "undefined"){
                            wordtimes[key][v3] = [];
                            midiwords[key][v3] = [];
                        }
                        //get the index of this
                        wordindex = miditostrindex.indexOf(indexes[i]);
                        //value[j] is start of this language.
                        if (wordtimes[key][v3].indexOf(midiarray[user][ value[j] + wordindex ].time) < 0){
                            wordtimes[key][v3].push(midiarray[user][ value[j] + wordindex ].time);
                            //push the whole midi struct.  to use later
                            midiwords[key][v3].push(midiarray[user][value[j] + wordindex]);
                            //we should have the user here to filter by.  words[key][v3][i].user
                            //filters are lang, word, user
                            //just get from the datatable and run though by time.  

                        }
                        //wordtimes[lang][word] = [time1, time2, time3]
                        //add this to the table.  
                    }
                    if (indexes.length > 0){
                        setTimes(key, v3, wordtimes[key][v3]);
                    }
                }
            }
        }
    }

}
function loadLanguage(lang, user){
    if (typeof(langs[lang]) !== "undefined"){
        mydic = langs[lang];
        for (const [key, value] of Object.entries(mydic)) {	
            //just adding an entry for each user.  
            //not sure this is the best way, but for now.  
            addDictRow(lang, key, value, user);
        }                    
    }

    else{
        //get lang from DB.  
        ref = firebase.database().ref('/dictionary/language/' + lang);
        ref.on('value',(snap)=>{
            if (snap.exists()){
                mydic = snap.val();
                langs[lang] = {};
                for (const [key, value] of Object.entries(mydic)) {	
                    m = value.midi.split(",");
                    //lang["base"]["length"]["midiseq"] = word
                    if (typeof(langs[lang][m.length]) === "undefined"){
                        langs[lang][m.length] = {};
                    }
                    langs[lang][m.length][value.midi] = key; //midiseq -> word lookup.  

                    addDictRow(lang, key, value, user);
                }                    
            }
        });
    }

}

//get languages from feedback midi.  search 
//dropdown for language selection, then load meanings into table.  
//load languages.js
function getHighlightArray(t, dur, user=0, trk=0){
    
    if (midiarray[user].length == 0){
        return 0;
    }

    i = Math.round(midiarray[user].length*t/dur);

    if (i>0 && i<midiarray[user].length-1 && midiarray[user][i].time < t-vidbuffer*1000){
        while (i < midiarray[user].length-1 && midiarray[user][i].time < t-vidbuffer*1000){
            i++;
        }
        return i;
    }
    else {
        while (i>=0 && midiarray[user][i].time > t-vidbuffer*1000){
            i--;
        }
        return i+1;
    }
}

function updateVidTimes(user=0, trk=0){
    //update video times for the below link IDs.  
    dur = 0;
    if ((useyoutube || watch) && player.getCurrentTime){
        const now = Date.now();
        var temptime = player.getCurrentTime();
        abstime = Math.round(temptime * 1000);
        dur = player.getDuration()*1000;
    }
    else{
        //use the other player time.  
        const now = Date.now();
        var temptime = player2.currentTime;
        abstime = Math.round(temptime * 1000);
        dur = player2.duration*1000;
    }
    currentvidtime = abstime;
    starth = getHighlightArray(abstime, dur, user, trk);


    for (i=starth; i< midiarray[user].length; i++){
        //expect this in order.  
        //need better search algorithm here.  
        if (midiarray[user][i].time > abstime + vidbuffer*1000){
            break;
        }
        //highlight the IDs for this time.  
        //this is undefined if these are new notes.  
        var obj = document.getElementById("feed" + Math.round(midiarray[user][i].time));
        if (typeof(obj) !== "undefined" && obj !== null){
            obj.style.color = "red";
        }
    }
}

function seekNext(lang, word){
    if (wordplay >= 0){
        wt = wordtimes[lang][word];
        if (currentwtindex > -1 && currentwtindex < wt.length){
            if (currentvidtime > wt[currentwtindex]+vidbuffer*1000){
                currentwtindex++;
                seekTo((wt[currentwtindex]-vidbuffer*1000)/1000);
                setTimeout(() => {seekNext(lang, word)}, vidbuffer*2*1000+2000);  //add one second so we dont time out because of lag.  
            }
            else{
                //not in sync.  
//                setTimeout(() => {seekNext(lang, word)}, 2000);
            }
        }
    }

}

function seekAll(lang, word, index=0){

    if (wordplay >= 0){
        wt = wordtimes[lang][word];
        if (currentwtindex > -1 && currentwtindex < wt.length){
            seekTo((wt[currentwtindex]-vidbuffer*1000)/1000);
            setTimeout(() => {seekNext(lang, word)}, vidbuffer*2*1000+2000); //add one second so we dont time out because of lag. 
        }
        else{
            wordplay = -1;
            currentwtindex = -1;
        }
    }
}

function setTimes(lang, word, times){
//    table.row( 0 ).data( newData ).draw();

    dictable.rows().every(function () {
        //brute force search, not great.  
        var d = this.data();
        if (d[DIC_LANG] === lang && d[DIC_WORD] === word) {
            hyperlink = "";
            for (i=0; i<times.length; i++){
                //think this is milliseconds.  
                //think this should display ok.  
                //use id link feed + time for highlight operations.  Highlight the time on timer.  
                hyperlink += '<a id="feed' + Math.round(times[i]) + '" href="#" onclick="seekTo(' + Math.round(times[i]/1000) + ');">' + Math.round(times[i]/1000) + '</a>, ';
                //this is a listing of what is in the pianoroll.  
                //also put here the color/icon/glyph/kanji of the word which is being displayed in the piano roll.  
                //how do we associate the user images?  
            }    
            d[DIC_TIMES] = hyperlink;
            d[DIC_PLAYALL] = '<a href="#" onclick="wordplay=1;seekAll(\'' + lang + '\', \'' + word + '\');"><img src="images/play.png" /></a>';
            d[DIC_PLAYALL] += '<a href="#" onclick="wordplay=-1;"><img src="images/pause.png" /></a>';
            d[DIC_PLAYALL] += '<a href="#" onclick="wordplay=1;currentwtindex=currentwtindex-1;seekAll(\'' + lang + '\', \'' + word + '\');"><img src="images/backward.png" /></a>';
            d[DIC_PLAYALL] += '<a href="#" onclick="wordplay=1;currentwtindex=currentwtindex+1;seekAll(\'' + lang + '\', \'' + word + '\');"><img src="images/forward.png" /></a>';
            d[DIC_PLAYALL] += '<a href="#" onclick="wordplay=-1;currentwtindex=-1;"><img src="images/stop.png" /></a>';
            //unable to track multiple indexes multiple with separate stop buttons, so probably should just have one stop button.  
            this.data(d);
            this.invalidate(); // invalidate the data DataTables has cached for this row
        }
    
    });
    dictable.columns.adjust().draw();
}

function addDictRow(lang, word, row, user) {
    dictable.row
        .add([
            word,
            "", //play all
            row['midi'],
            user,
            "", //times, will need to update this.  
            row['definition'],
            row['created'],
            lang
        ])
        .draw(false);    
}
