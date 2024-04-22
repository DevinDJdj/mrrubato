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

function loadAllLanguages(){
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

function loadAll(){
    //find language in midi
    const dictable = new DataTable('#DictionaryTable');
    loadAllLanguages();
    //go through midiarray.  
    //should be in order.  
    //find sequences we need.  
    //load base langauge to start.  
    loadLanguage("base");
    cl = [];
    cle = [];
    for (i=0; i<midiarray.length-5; i++){
        if (midiarray[i] == 12 && midiarray[i+1] == 5 && midiarray[i+2] == 7 && midiarray[i+3] == 12){
            //change language (add language)
            cl.push(i);
        }
        else if (midiarray[i]==12 && midiarray[i+1] == 7 && midiarray[i+2] == 5 && midiarray[i+3] == 12){
            cle.push(i);
        }
    }
    for (i=0; i<cl.length; i++){
        //change language
        langmidi = midiarray.slice(cl[i]+4, cle[i]).join();
        if (typeof(alllangs[langmidi]) !=="undefined"){
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
        }
    }

    //now go through the langstart and langend looking for words.  
    for (const [key, value] of Object.entries(langstart)) {	
        for (j=0; j<value.length; j++){
            //maxwordlength
            temp = midiarray.slice(value[j], langend[key][j]).join();
            //value[j] is start of this language.  
            //full array of midi.  
            //just go through words and find any instance.  
            for (const [k2, v2] of Object.entries(langs[key])) {	//k2 = length of midiseq, v2 = array of words
                for (const [k3, v3] of Object.entries(langs[key][k2])) {
                    const indexes = [...temp.matchAll(new RegExp(k3, 'gi'))].map(a => a.index);
                    console.log(indexes); // [2, 25, 27, 33]
                    if (typeof(wordtimes[key]) === "undefined"){                        
                        wordtimes[key] = {};
                    }
                    for (i=0; i<indexes.length; i++){
                        if (typeof(wordtimes[key][v3]) === "undefined"){
                            wordtimes[key][v3] = [];
                        }
                        wordtimes[key][v3].push(midiarray[ value[j] + indexes[i] ].time);
                        //add this to the table.  
                    }
                }
            }
        }
    }
}

function loadLanguage(lang){
    //get lang from DB.  
    ref = firebase.database().ref('/dictionary/language' + lang);
	ref.on('value',(snap)=>{
	    if (snap.exists()){
            mydic = snap.val();
            langs[lang] = {};
            langmaxwordlength[lang] = 0;
            langminwordlength[lang] = 1000;
            for (const [key, value] of Object.entries(mydic)) {	
                m = value.split(",");
                //lang["base"]["length"]["midiseq"] = word
                if (langs[lang][m.length] === "undefined"){
                    langs[lang][m.length] = {};
                }
                langs[lang][m.length][value] = key; //midiseq -> word lookup.  

                addDictRow(lang, key, value);
            }                    
        }
    });


}

//get languages from feedback midi.  search 
//dropdown for language selection, then load meanings into table.  
//load languages.js


function setTimes(lang, word, times){
    var word = dictable
    .rows( function ( idx, data, node ) {
        return (data.lang === lang  && data.word=== word) ?
            true : false;
    } )
    .data(); 
    console.log(word);   
    word[0]['times'] = times;

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
