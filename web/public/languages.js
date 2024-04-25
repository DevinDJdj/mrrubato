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

var dictable = null;
var DIC_LANG = 5;
var DIC_WORD = 0;
var DIC_TIMES = 2;
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

function loadDictionaries(){
    //find language in midi
    //find language in words "change language base" "change language to base"
    //need to use this more.  Probably more convenient.  
    dictable = new DataTable('#DictionaryTable');
    loadLanguages();
    //go through midiarray.  
    //should be in order.  
    //find sequences we need.  
    //load base langauge to start.  
//    loadLanguage("base");

    cl = [];
    cle = [];
    for (i=0; i<midiarray.length-5; i++){
        if (midiarray[i] == keybot+12 && midiarray[i+1] == keybot+5 && midiarray[i+2] == keybot+7 && midiarray[i+3] == keybot+12){
            //change language (add language)
            cl.push(i);
        }
        else if (midiarray[i]==keybot+12 && midiarray[i+1] == keybot+7 && midiarray[i+2] == keybot+5 && midiarray[i+3] == keybot+12){
            cle.push(i);
        }
    }
    numlangs = 0;
    for (i=0; i<cl.length; i++){
        //change language
        tempmidi = midiarray.slice(cl[i], cle[i]+4);
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
            loadLanguage(lang);
            numlangs++;
        }
    }

    if (numlangs == 0){
        //no language changes.  
        //just go through base language.  
        langstart["base"] = [0];
        langend["base"] = [midiarray.length];
        loadLanguage("base");
    }
    else{
        if (cl[0] > 0){
            langstart["base"] = [0];
            langend["base"] = [cl[0]];
            loadLanguage("base");
        }
    }

    //now go through the langstart and langend looking for words.  
    //need a better mechanism but for now just timeout to wait for all loadLanguage calls to complete.  
    setTimeout(function(){findWords();}, 3000);

}

function findWords(){
    for (const [key, value] of Object.entries(langstart)) {	
        for (j=0; j<value.length; j++){
            //maxwordlength
            temp = midiarray.slice(value[j], langend[key][j]);

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
                    }
                    for (i=0; i<indexes.length; i++){
                        if (typeof(wordtimes[key][v3]) === "undefined"){
                            wordtimes[key][v3] = [];
                        }
                        //get the index of this
                        wordindex = miditostrindex.indexOf(indexes[i]);
                        //value[j] is start of this language.
                        if (wordtimes[key][v3].indexOf(midiarray[ value[j] + wordindex ].time) < 0){
                            wordtimes[key][v3].push(midiarray[ value[j] + wordindex ].time);
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
function loadLanguage(lang){
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

                addDictRow(lang, key, value);
            }                    
        }
    });


}

//get languages from feedback midi.  search 
//dropdown for language selection, then load meanings into table.  
//load languages.js


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
                hyperlink += '<a href="#" onclick="seekTo(' + Math.round(times[i]/1000) + ');">' + Math.round(times[i]/1000) + '</a>, ';
                //this is a listing of what is in the pianoroll.  
                //also put here the color/icon/glyph/kanji of the word which is being displayed in the piano roll.  
                //how do we associate the user images?  
            }    
            d[DIC_TIMES] = hyperlink;
            this.data(d);
            this.invalidate(); // invalidate the data DataTables has cached for this row
        }
    
    });

}

function addDictRow(lang, word, row) {
    dictable.row
        .add([
            word,
            row['midi'],
            "", //times, will need to update this.  
            row['definition'],
            row['created'],
            lang
        ])
        .draw(false);    
}
