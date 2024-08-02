//create management for dictionary.  
//edit = 5 keys
//do we want this start end structure?  
//perhaps an easier end structure.  
//add/edit word [12, 9, 10, 11, 12] .. [12,11,10,9,12]
//add/edit language [12, 2, 3, 4, 12] .. [12, 4, 3, 2, 12]
//change language [12, 5, 7, 12] .. [12, 7, 5, 12]

var langs = {};
var langsa = {};
var octaves = {};
var alllangs = {};
var alllangsa = {};
var langstart = {};
var langend = {};
var wordtimes = {};
var midiwords = {};


var currentwtindex = 0;
var currentvidtime = 0;
var currentlanguage = "base";
var wordplay = -1;

var dictable = null;
var autodic = null;
var metadic = null;
var DIC1_WORD = 0;
var DIC1_KEYS = 1;
var DIC1_LANG = 2;
var DIC1_MEANING = 3;

var DIC_LANG = 7;
var DIC_WORD = 0;
var DIC_PLAYALL = 1;
var DIC_KEYS = 2;
var DIC_USER = 3;
var DIC_TIMES = 4;
var DIC_CREATED = 5;
//config.js keybot
//do we want to allow for some function to adjust keybot/keytop?  

//add definition MIDI my definition of this word.  
//think we need to allow for stoppage or just keep the transcript pending.  

function reinitLanguages(){
    langs = {};
    langsa = {};
    alllangs = {};
    alllangsa = {};
    langstart = {};
    langend = {};
    wordtimes = {};
    midiwords = {};
    currentwtindex = 0;
    currentvidtime = 0;
    currentlanguage = "base";
    wordplay = -1;
    destroyDics();    
}

function changeColor(word, color){

}


//should really be able to see the users transcript in words, so when clicking a user, we show his transcript.  
//list all user icons/names next to your own to be clicked
function updateState(transcript="", lang=""){
    //function to get the state of the entire transcript up to this point.  
    //this is a bit of a mess.  Need to clean up.
    //get the state info and 
    //for now just show latest entry.  
    //use midi array with current language and meta.  
    mytranscript = $('#mycomments').val();
    mystate = "";
    mystate += currentlanguage + ": " + midiarray[currentmidiuser][currentlanguage].length + "<br>";
    mystate += "meta: " + midiarray[currentmidiuser]["meta"].length + "<br>";
    mystate += "last entry: " + transcript + "<br>";
    mystate += "current video time: " + currentvidtime + "<br>";
    if (lastnote !==null){
        mystate += "Last Note: " + lastnote.note + "<br>";
    }
    $('#currentstate').html(mystate);

}



function addUser(user, group){ //add user to group 
    //can only do if this is our user or we are admin.  
    //otherwise add request is sent to the user.  too many details...
    

}

//function newUser(user){} //only users existing in DB can be added?  
//DB existence depends on if they have logged in or not.  


function addGroup(group, group){ //add group to group
    //can only do if this is our user or we are admin.  

}

function newGroup(group){

}

function getUsersFromGroup(group, nesting = 1){
    //get users from this group and any "subgroups" such an annoying structure to deal with.  
    //just get the full group structure locally and then do the filtering for now?  
    //no this is not scalable.  make a IN ( ) query once.  
}



function removeTag(tag, videoid=""){
    removeTagUI(tag);
    if (videoid==""){
        videoid=video;
    }
    //remove from tag lookup.  
    tagrref = firebase.database().ref('/tags/' + tag + '/videos/' + videoid);
    tagrref.remove().then(function() {
        console.log("Remove succeeded.");
    });
    //remove from video tags
    let prefix = '/misterrubato/';
    if (watch === true){
        prefix = '/watch/';
    }
    tagvref = firebase.database().ref(prefix + videoid + '/tags/' + tag);
    tagvref.remove().then(function() {
        console.log("Remove succeeded.");
    });


}

function addTag(tag, videoid="", midi=null){
    //once a tag is in the DB, there is no deleting it, but we can remove from videos, I think this is fine for now.  
    //topics must start with certain midi sequence.  1,1 or should they just be a word.  Dont necessarily need a word.  
    //so I think separate.  start with 1,1 or some easy identifier.  
    //they can be just a normal word after this if a word exists.  
    //make sure to use unique variables as the .then is a promise.
    addTagUI(tag);
    if (videoid==""){
        videoid=video;
    }

    now = new Date();
    if (midi !==null){
        tagaref = firebase.database().ref('/tags/' + tag);
        tagaref.once('value')
        .then((snap) => {
            if (snap.exists()){
                let mymidi = snap.val().midi;
                if (mymidi != midi){
                    tagaref.update({"midi": midi, "updated": now.toISOString().substring(0, 10).replaceAll('-','')});
                }
            }
            else{
                //probably should include create user and update user etc.  
                obj = {"midi": midi, "color": 0, "created": now.toISOString().substring(0, 10).replaceAll('-',''), "updated": now.toISOString().substring(0, 10).replaceAll('-','') };
                tagaref.set(obj);
            }
        });
    }
    else{
        //add to tag lookup.  
        tagaref = firebase.database().ref('/tags/' + tag + '/videos/' + videoid);
        tagaref.once('value')
        .then((snap) => {
            if (snap.exists()){
            }
            else{
                //probably should include create user and update user etc.  
                obj = {"added": now.toISOString().substring(0, 10).replaceAll('-','')};
                tagaref.set(obj);
            }
        });
        
        //add to video tags
        let prefix = '/misterrubato/';
        if (watch === true){
            prefix = '/watch/';
        }
        tagvref = firebase.database().ref(prefix + videoid + '/tags/' + tag);
        tagvref.once('value')
        .then((snap) => {
            if (snap.exists()){
            }
            else{
                //probably should include create user and update user etc.  
                obj = {"added": now.toISOString().substring(0, 10).replaceAll('-','')};
                tagvref.set(obj);
            }
        });
    }

}

function addWord(word, midi){
    wordref = firebase.database().ref('/dictionary/language/' + currentlanguage + "/" + word);
	wordref.once('value')
    .then((snap) => {
        now = new Date();
        if (snap.exists()){
            let mymidi = snap.val().midi;
            if (mymidi != midi){
                wordref.update({"midi": midi, "updated": now.toISOString().substring(0, 10).replaceAll('-','')});
            }
        }
        else{
            //probably should include create user and update user etc.  
            obj = {"midi": midi, "color": 0, "created": now.toISOString().substring(0, 10).replaceAll('-',''), "updated": now.toISOString().substring(0, 10).replaceAll('-','') };
            wordref.set(obj);
        }
    });

}


function addLanguage(lang, midi){
    langref = firebase.database().ref('/dictionary/languages/' + lang);
	langref.once('value')
    .then((snap) => {
        now = new Date();
        if (snap.exists()){
            let mymidi = snap.val().midi;
            if (mymidi != midi){
                langref.update({"midi": midi, "updated": now.toISOString().substring(0, 10).replaceAll('-','')});
            }
        }
        else{
            //probably should include create user and update user etc.  
            obj = {"midi": midi, "created": now.toISOString().substring(0, 10).replaceAll('-',''), "updated": now.toISOString().substring(0, 10).replaceAll('-','') };
            langref.set(obj);
        }
    });

    //initialize language with test word.  
    langref1 = firebase.database().ref('/dictionary/language/' + lang + '/abc');
	langref1.once('value')
    .then((snap1) => {
        now = new Date();
        if (snap1.exists()){

        }
        else{
            //probably should include create user and update user etc.  
            midi = "1,1,1";
            obj = {"midi": midi, "definition": "first word", "created": now.toISOString().substring(0, 10).replaceAll('-',''), "updated": now.toISOString().substring(0, 10).replaceAll('-','') };
            langref1.set(obj);
        }
    });

}


function setOctave(octave, lang=""){
    if (lang==""){
        lang = currentlanguage;
    }
    keybot[lang] = octave*12;
    /*
    for (const [key, value] of Object.entries(langsa[lang])) {	
        value.midi = convertKeys(value.midi, keybot[lang]/12);
        m = value.midi.split(",");
        langs[lang][m.length][value.midi] = key; //full word info.  
        //reset inline conversion.  
    }
    */
    labelDicRedraw();

}

function changeLanguage(midi){
    //find the language.  
    lang = lang.toLowerCase().replaceAll(" ", "_");
    if (typeof(alllangs[midi]) !== "undefined"){
        lang = alllangs[midi];
        currentlanguage = lang;
        initLangData(lang);
    }
    else{
        console.log("Language not found" + midi);
    }
}

function selectLanguage(lang){
    lang = lang.toLowerCase().replaceAll(" ", "_");
    if (Object.values(alllangs).includes(lang) > -1){
        currentlanguage = lang;
        initLangData(lang);
//        $('.langlabel').html('<a id="langlink" href="#" onclick="filterDicManual();return false;">' + currentlanguage + '</a>');
    }
    else{
        console.log("Language not found" + lang);    
    }
}

function loadLanguages(){
    langsref = firebase.database().ref('/dictionary/languages');
	langsref.once('value')
    .then((snap) => {
	    if (snap.exists()){
            let mylangs = snap.val();
            for (const [key, value] of Object.entries(mylangs)) {
                alllangs[value.midi] = key;
                alllangsa[key] = value; //additional info on the language.  langname -> all values.  
            }                    
        }
    });

}

function addLangLabel(lang){
    langa = lang.toLowerCase().replaceAll(" ", "_");
    langlink = document.getElementById("langlink_" + langa);
    if (typeof(langlink) === "undefined" || langlink === null){
        $('.langlabel').append(' <a id="langlink_' + langa + '" href="#">' + lang + '</a> ');
        langlink = document.getElementById("langlink_" + langa);
        langlink.onclick = function() { filterDicManual(lang); return false; };
    }

}

//this is the initial function to load everything.  
function initLangData(lang, user=-1){
    if (user==-1){
        user = currentmidiuser;
    }

    if (typeof(midiarray[user][lang]) === "undefined"){
        midiarray[user][lang] = [];
        keybot[lang] = 48;

        //if never used before.  
        let loaded = false;
        for (i=0; i<midiarray.length; i++){
            if (typeof(midiarray[i][lang]) !== "undefined"){
                loaded = true;
            }
        }
        if (!loaded){
            loadLanguage(lang, user);
        }
        addLangLabel(lang);
    }
/*
    if (typeof(langstart[lang]) === "undefined"){
        langstart[lang] = {};
        langend[lang] = {};
    }
    if (typeof(langstart[lang][user])==="undefined"){
        langstart[lang][user] = [];
        langend[lang][user] = [];
    }
*/

}

function loadLanguageScript(lang){
    let scriptEle = document.createElement("script");
    scriptEle.setAttribute("src", "languages/" + lang + ".js");
    scriptEle.setAttribute("type", "text/javascript");
    scriptEle.setAttribute("async", true);
    document.body.appendChild(scriptEle);
    
      // success event 
      scriptEle.addEventListener("load", () => {
        console.log("Language loaded " + lang);
      });
       // error event
      scriptEle.addEventListener("error", (ev) => {
        console.log("Error loading language " + lang, ev);
      });
    
}


function convertKeys(midikeys, octaveshift=0, keyshift=0){
    midikeys = midikeys.split(",");
    for (i=0; i<midikeys.length; i++){
        midikeys[i] = parseInt(midikeys[i]) + octaveshift*12+keyshift;
    }
    midikeys = midikeys.join(",");
    return midikeys;
}

function loadMetaLanguage(lang="meta", user=0){
    console.log('Load Meta Language start ' + Date.now());

    //do we just loadLanguage(meta, 0)
    //need to add this to the languages if we want to do this.  
    //lets just work from the code.  
    //keymap comes from speech.js
    //keymap.keydict[""]
    add = 0;
    if (typeof(midiarray[user][lang]) === "undefined"){
        midiarray[user][lang] = [];
    }
    if (langs[lang] === undefined){
        langs[lang] = {};
        langsa[lang] = {};
        add = 1;
    }
    today = new Date().toISOString().substring(0, 10).replaceAll('-','');
    for (const [key, value] of Object.entries(keymap.keydict[""])) {	
        if (typeof(langs[lang][key]) === "undefined"){
            langs[lang][key] = {};
        }

        for (const [key2, value2] of Object.entries(value)) {
            
            //rebuild keys with keybot.  
            //we can change keybot/keytop if we want.  

            key2a = convertKeys(key2, keybot[lang]/12); //get keys + keybot

            langs[lang][key][key2a] = value2; //midiseq -> word lookup.  

            temp = {"word": value2, "midi": key2, "user": user, "times": 0, "definition": value2, "created": today, "lang": lang};
            langsa[lang][value2] = temp; //full word info.  


            addDictRow(lang, value2, temp, user, add);
        }
    }                    
    addLangLabel("meta");
    console.log('Load Meta Language end ' + Date.now());
    metadic.draw();

}


//move language to a different octave.  
function moveLanguage(lang, user, octave=0){

}

function loadLanguage(lang, user){
    lang = lang.toLowerCase().replaceAll(" ", "_");
    if (typeof(langs[lang]) !== "undefined"){
        mydic = langs[lang];
        mydica = langsa[lang];
        for (const [key, value] of Object.entries(mydica)) {	
            //just adding an entry for each user.  
            //not sure this is the best way, but for now.  
            //should really only load the words which exist in the feedback.  
            //this is length -> words.  so need nested array.  
            //why did we save like this, not sure if we actually need.  
            addDictRow(lang, key, value, user);
        }
        obj = {"word": "test", "midi": "1,1", "user": user, "times": 0, "definition": "test", "created": "20210101", "lang": lang};
        langsa[lang]["test"] = obj;
        addDictRow(lang, "test", obj, user);
    }

    else{
        //get lang from DB.  
        langref = firebase.database().ref('/dictionary/language/' + lang);
        langref.once('value')
        .then((snap) => {
            if (snap.exists()){
                add = 0;
                if (typeof(langs[lang]) === "undefined"){
                    //only add to the lookup dict if it has not been added yet.  
                    add = 1;
                }       
                mydic = snap.val();
                langs[lang] = {};
                langsa[lang] = {};
                //set up octaves for language.  
                //if we do this, we need to save the octave information.  
                //perhaps we can just allow this to be done each time, and so the full recording will have octave information.  
                //at start of meta track, save all of these changes if we put into settings.  
                //not sure if we need user based settings.  
                octaves[lang] = 0;

                addLangLabel(lang);
            //dynamic functions for this language.  
                loadLanguageScript(lang);             

                for (const [key, value] of Object.entries(mydic)) {	
                    m = value.midi.split(",");
                    //lang["base"]["length"]["midiseq"] = word
                    if (typeof(langs[lang][m.length]) === "undefined"){
                        langs[lang][m.length] = {};
                    }
                    
                    langsa[lang][key] = value; //full word info.  

                    addDictRow(lang, key, value, user, add);

                    keymaps[lang].addWord(key, value);

                    key2a = convertKeys(value.midi, keybot[lang]/12);
                    langs[lang][m.length][key2a] = key; //midiseq -> word lookup.  

                    //convert keys down for now.  Probably get rid of this, converting to 0 based.  
                    //except for lookup.  
                    //shift keys down.  

                                
                }
                //populate the filters.  
                if (typeof(langs[lang][2]) === "undefined"){
                    langs[lang][2] = {};
                }
                obj = {"word": "test", "midi": "1,1", "user": user, "times": 0, "definition": "test", "created": "20210101", "lang": lang};
                langsa[lang]["test"] = obj;
                addDictRow(lang, "test", obj, user);
                key2a = convertKeys(obj.midi, keybot[lang]/12);
                langs[lang][m.length][key2a] = "test"; //midiseq -> word lookup.  

            }
        });

    }

}

function unfilterDicManual(lang="current"){
    currentselection = $('#lang').select2('data');
    if (currentselection.length > 0){
        const idx = currentselection.findIndex((l) => l.text == (lang));//  userindex = users.findIndex((u) => u.uid == (uid));        
        currentselection.splice(idx, 1);
        if (currentselection.length == 0){
            $('#lang').val(null).trigger('change');//$('#lang').select2('val', null);
        }
        else{
            $('#lang').select2('val', currentselection);
        }
//        dictable.draw();
    }
    langa = lang.toLowerCase().replaceAll(" ", "_");
    langlink = document.getElementById("langlink_" + langa);
    if (typeof(langlink) === "undefined" || langlink === null){
    }
    else{
        langlink.innerHTML = lang;
        langlink.onclick = function() { filterDicManual(lang); return false; };
    }
}
//quick filter for languages.  
function filterDicManual(lang="current"){
    currentselection = $('#lang').select2('data');
    currentselection.push(lang);
    $('#lang').select2('val', currentselection);
    langa = lang.toLowerCase().replaceAll(" ", "_");
    langlink = document.getElementById("langlink_" + langa);
    if (typeof(langlink) === "undefined" || langlink === null){
    }
    else{
        langlink.innerHTML = "*" + lang + "*";
        langlink.onclick = function() { unfilterDicManual(lang); return false; };
    }
}


//this is run each time the checkCommands is done which pulls the midi.  
function filterDicAuto(transcript, lang="base"){
    if (autodic !== null && transcript !="" && transcript.length > 2){
        var isMidi = /^[0-9,]*$/.test(transcript);
        if (isMidi){
            autodic.columns().search(''); //clear all filters.
//            $('#keys').select2('val', ['good'])
            transcript = transcript.slice(0,-1); //remove last comma.

            transcripta = convertKeys(transcript, -keybot[lang]/12);


            autodic.column(DIC1_KEYS).search(transcripta).draw();

            transcriptb = convertKeys(transcript, -keybot["meta"]/12);
            metadic.column(DIC1_KEYS).search(transcriptb).draw();

            getFullPiano(transcript); //dont use converted keys for this.  
        }
        else{
            autodic.columns().search(''); //clear all filters.
            metadic.columns().search('');
            autodic.column(DIC1_LANG).search(lang).draw();
            autodic.column(DIC1_WORD).search(transcript).draw();
            metadic.column(DIC1_WORD).search(transcript).draw();

        }
    }
    if (autodic !==null && transcript == ""){
        autodic.columns().search(''); //clear all filters.
        autodic.column(DIC1_LANG).search(currentlanguage).draw();
        metadic.columns().search('');
        metadic.draw();
    }
    //only update if we have transcript.  
    updateState(transcript, currentlanguage);
}

function createAutoDic(user){
    if (user==0){
        autodic = new DataTable('#autodic', {
            /*
            columns: [
                { data: 'word' },
                { data: 'playall' },
                { data: 'midisequence' },
                { data: 'user' },
                { data: 'times' },
                { data: 'meaning' },
                { data: 'created' },
                { data: 'lang' }
            ],
            */
            columnDefs: [{ visible: false, targets: DIC1_LANG }],
            searching: true, paging: false,
            info: false, dom: 'lrt',
                createdRow: function (row, data, dataIndex) {
                    this.api()
                        .columns()
                        .every(function () {

                            let column = this;
                            if (column.visible()){
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
                                //could be more efficient
                                column
                                .data()
                                .unique()
                                .sort()
                                .each(function (d, j) {
                                    select.add(new Option(d));

                                });
                            
                            }
                        });
            },

        });
    
    }
}


function createMetaDic(user){
    if (user==0){
        metadic = new DataTable('#metadic', {
            /*
            columns: [
                { data: 'word' },
                { data: 'playall' },
                { data: 'midisequence' },
                { data: 'user' },
                { data: 'times' },
                { data: 'meaning' },
                { data: 'created' },
                { data: 'lang' }
            ],
            */
            columnDefs: [{ visible: false, targets: DIC1_LANG }],
            searching: true, paging: false,
            info: false, dom: 'lrt',
                createdRow: function (row, data, dataIndex) {
                    this.api()
                        .columns()
                        .every(function () {

                            let column = this;
                            if (column.visible()){
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
                                //could be more efficient
                                column
                                .data()
                                .unique()
                                .sort()
                                .each(function (d, j) {
                                    select.add(new Option(d));

                                });
                            
                            }
                        });
            },

        });
    
    }
}

function destroyDics(){
    if (autodic !== null){
        autodic.clear().draw();
    }
    if (metadic !== null){
        metadic.clear().draw();
    }
    if (dictable !== null){
        dictable.clear().draw();
    }
//do we need this?  
//2nd empty html
//$(tableId + " tbody").empty();
//$(tableId + " thead").empty();

}

function labelDicRedraw(){
    let fullpcanvas_labels = document.getElementById("fullpcanvas_labels");    
    var context = fullpcanvas_labels.getContext("2d");
    context.clearRect(0, 0, fullpcanvas_labels.width, fullpcanvas_labels.height);
    //pull all languages used.  
    labelDic(currentlanguage);
    labelDic("meta");
}

function labelDic(lang){
    let fullpcanvas_labels = document.getElementById("fullpcanvas_labels");    
    var context = fullpcanvas_labels.getContext("2d");
    context.fillStyle = "red";
    context.font = "bold 12px Arial";
    context.textAlign = 'left';
    x = keybot[lang];
    y = 16;
    context.fillText("     " + lang, ((x+3)/88)*fullpcanvas_labels.width, y);
    context.strokeStyle = "red";
    context.lineWidth = 2;
    context.beginPath();
    context.rect(((x+3)/88)*fullpcanvas_labels.width, 0, ((24)/88)*fullpcanvas_labels.width, fullpcanvas_labels.height-2);
    context.stroke();

}

function getFullPiano(midikeys=null, midikeys2=null){
    let fullpcanvas = document.getElementById("fullpcanvas");    
    let RedKeys = [];
    if (midikeys !== null){
//        midikeys = convertKeys(midikeys, keybot[currentlanguage]/12, 3); //get keys + keybot + shift 3 for 88-key.  
        //still need the shift
        midikeys = convertKeys(midikeys, 0, 3); //get keys + shift 3 for 88-key.
        RedKeys = midikeys.split(",");
        RedKeys = RedKeys.map(function (x) { 
            return parseInt(x, 10); 
        });
    }
    DrawKeyboard(fullpcanvas, RedKeys);

    labelDic("meta");
    labelDic(currentlanguage);

//    const img    = pcanvas.toDataURL('image/png');
//    document.getElementById("generatedkeys4").src = img4;
//    return img;

}

function getMiniPiano(midikeys){
    let pcanvas = document.getElementById("pcanvas");    
    let RedKeys = midikeys.split(",");
    RedKeys = RedKeys.map(function (x) { 
        return parseInt(x, 10); 
    });
    DrawKeyboard(pcanvas, RedKeys, 25, 15);
    const img    = pcanvas.toDataURL('image/png');
//    document.getElementById("generatedkeys4").src = img4;
    return img;

}


function loadDictionaries(user){
    //find language in midi
    //find language in words "change language base" "change language to base"
    //need to use this more.  Probably more convenient.  
//    dictable = new DataTable('#DictionaryTable');
        //column dropdown filter.  
        //not efficient but ok for now, really only want to call this once.  

    if (user==0 && dictable == null){
//        destroyDics();
        createAutoDic(user);
        createMetaDic(user);

        dictable = new DataTable('#DictionaryTable', {
        /*
        columns: [
            { data: 'word' },
            { data: 'playall' },
            { data: 'midisequence' },
            { data: 'user' },
            { data: 'times' },
            { data: 'meaning' },
            { data: 'created' },
            { data: 'lang' }
        ],
        */
            rowCallback: function (row, data) {
                /*
                if (row[DIC_WORD] == 'test') { //initialize this data.  
                    dictable.rows().invalidate().draw();
                }
                */
            },
            columnDefs: [
                {
                    targets: DIC_USER,
                    render: function (data, type, row, meta) {
                        return '<img height="40px" src="' + users[ row[DIC_USER] ].pic + '" /><br>' + users[ row[DIC_USER] ].name; 
                    }
                },
                {
                    //langs[lang][ row[DIC_WORD] ] = word.  
                    targets: DIC_KEYS,
                    render: function (data, type, row, meta) {
                        tmp = langsa[ row[DIC_LANG] ][ row[DIC_WORD] ];
                        if (typeof(tmp) === "undefined"){
                            tmp = null
                        }
                        if (tmp !==null && (!("img" in tmp) || typeof(tmp["img"]) === "undefined")){
                            tmp["img"] = getMiniPiano(row[DIC_KEYS]);
                        }
                        return '<img width="110px" height="22px" src="' + tmp["img"] + '" alt="' + row[DIC_KEYS] + '" /><br>' + row[DIC_KEYS]; 
                    }
                },
                {
                    targets: DIC_TIMES,
                    width: '40%'
                }

            ],            
        //    initComplete: function () {
//                count = 0;
            createdRow: function (row, data2, dataIndex) {
//                $(row).hide();
                if (data2[DIC_WORD] == "test"){
                    this.api().columns().every( function () {
                    var title = this.header().textContent;
                    
                    if (title !=="times"){ //dont want the filter here.  
                        var column = this;
                        var select = $('<select id="' + title + '" class="select2" ></select>')
                            .appendTo( $(column.footer()).empty() )
                            .on( 'change', function () {
                            //Get the "text" property from each selected data 
                            //regex escape the value and store in array
                            var data = $.map( $(this).select2('data'), function( value, key ) {
                                return value.text ? '^' + $.fn.dataTable.util.escapeRegex(value.text) + '$' : null;
                                        });
                            
                            //if no data selected use ""
                            if (data.length === 0) {
                                data = [""];
                            }
                            
                            //join array into string with regex or (|)
                            var val = data.join('|');
                            
                            //search for the option(s) selected
                            column
                                    .search( val ? val : '', true, false )
                                    .draw();
                            } );
        
                        column.data().unique().sort().each( function ( d, j ) {
                            if (column[0][0]==DIC_USER){ //not sure why I use this column[0][0] but it works.  Surely better way.  
                                select.append( '<option value="'+d+'">'+users[d].name+'</option>' );
                            }
                            else{
                                select.append( '<option value="'+d+'">'+d+'</option>' );
                            }
                        } );
                    
                        //use column title as selector and placeholder
                        $('#' + title).select2({
                            multiple: true,
                            closeOnSelect: false,
                            placeholder: "Select a " + title
                        });
                        
                        //initially clear select otherwise first option is selected
                        $('.select2').val(null).trigger('change');
                    }
                        
                    } );
                }
            }
        });
    
            /*
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
                        //could be more efficient
                        column
                            .data()
                            .unique()
                            .sort()
                            .each(function (d, j) {
                                if (column[0][0]==DIC_USER){ //not sure why I use this column[0][0] but it works.  Surely better way.  
                                    select.add(new Option(users[d].name));
                                }
                                else{
                                    select.add(new Option(d));
                                }

                            });
                    });
                },

            });
            */

        loadLanguages();
        loadMetaLanguage();
    //do we want all languages or not?  
    }
    //go through midiarray.  
    //should be in order.  
    //find sequences we need.  
    //load base langauge to start.  
//    loadLanguage("base");

    for (const [lang, value] of Object.entries(midiarray[user])) {
        loadLanguage(lang, user);
//        initLangData(lang, user);
    }

    //now go through the langstart and langend looking for words.  
    //need a better mechanism but for now just timeout to wait for all loadLanguage calls to complete.  
    setTimeout(function(){findWordsA(user);
        //set up to highlight video times
        setInterval(function(){
            updateVidTimes(user);     
            //all languages checkCommands.  

            //actually execute commands.  
            //if we include the language in the currentmidi.  
            let midi = getMidiRecent();
            let langs = getLangsFromMidi(midi);
            let t = "";
            for (let li=0; li<langs.length; li++){
                t = checkCommands(langs[li]);
            }
            
            [t2, lang] = findCommand(t); //this points to speech.js->findCommand
            //do we need this?  

            $('#mycommand').val(t.trim()); //incomplete command.  
            filterDicAuto(t2.trim(), lang);
            //filter commands.  autodic and metadic.  
            //if only midi.  

        }, 500);
    }, 5000);

}

//keep track of the current language here.  
//just update the indexes each time something is played until there is another language change.  
//ok, now we would need multiple tracks if we want simultaneous languages.  Or make start/end, a time instead of an index.  
//yeah this is easier.  Just use the video time instead of the midiarray index.  
//ok so we need an additional nest for "lang"  -> midiarray[user][lang][index]
//then we are able to add to a different track for each language.  
//need to adjust midifeedback load.  getMidiFeedback
//

function getLangsFromMidi(midi){
    //right now just return the first.  
    langs = [];
    if (midi !== null && midi.length > 0){ 
        for (const [key, value] of Object.entries(keybot)) {
            if (midi[0].note >= value && midi[0].note <= value + 24){
                langs.push(key);
            }
        }
    }   
    return langs;
}

function updateLangRange(lang, user, start, end){
    let idx = 0;
    for (let i=0; i< langstart[lang][user].length; i++) {
        if (langstart[lang][user][i] < start){
        }
        else{
            idx = i;
            i = langstart[lang][user].length;
            //break;
        }
    }
    langstart[lang][user].splce(idx, 0, start);
    langend[lang][user].splice(idx, 0, end);
}


function findWordsA(user){
    console.log('Findwords start ' + Date.now());
    //should load meta array first.  Or we really need to do this logic in time, not order of language?  
    //right now we have no easy way to search time across languages.  
    //essentially we would need to make a string of each language and check all times until the minimum time from all other languages.  
    //this is not efficient?  
    //also really need to search from longest to shortest.  

    //pseudo-code
    /*
        find all word in meta
        for each word in meta
            save any set octave or set language commands
        for each language in midiarray
            we can search through the midiarray for any language until set language or set octave.  
            locally run the set octave or set language, then continue the tempstr.  
            Dont think this changes the tempstr.  Just changes what we should be searching.  
            So we will have to search through all languages up until the set octave or set language commands.  
            Then start a new tempstr until the next set octave or set language command.  
            This changes the langs[lang][midiseq.length][midiseq] = word array
            This algorithm may actually be slightly faster.  Hard to say the efficiency of the tempstr.matchAll with large strings.  

    */

    for (const [lang, value] of Object.entries(midiarray[user])) {
        temp = value;
        key = lang;
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
        if (typeof(langs[key]) === "undefined"){
            //no words defined yet, really shouldnt occur much.  
            //the Object.entries is not smart enough to handle this.
        }
        else{
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
                        if (wordtimes[key][v3].indexOf(value[wordindex ].time) < 0){
                            wordtimes[key][v3].push(value[wordindex ].time);
                            //push the whole midi struct.  to use later
                            midiwords[key][v3].push(value[wordindex]);
                            //we should have the user here to filter by.  words[key][v3][i].user
                            //filters are lang, word, user
                            //just get from the datatable and run though by time.  

                        }
                        //wordtimes[lang][word] = [time1, time2, time3]
                        //add this to the table.  
                    }
                    if (indexes.length > 0){
                        setTimes(key, v3, wordtimes[key][v3], user);
                    }
                }
            }
        }
    }
    console.log('Findwords end ' + Date.now());

}


function findWords(user){

    for (const [key, value] of Object.entries(langstart)) {	
        if (typeof(value[user]) !=="undefined" && value[user].length > 0){
            for (j=0; j<value[user].length; j++){
                //maxwordlength
                temp = midiarray[user].slice(value[user][j], langend[key][user][j]);

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
                            if (wordtimes[key][v3].indexOf(midiarray[user][ value[user][j] + wordindex ].time) < 0){
                                wordtimes[key][v3].push(midiarray[user][ value[user][j] + wordindex ].time);
                                //push the whole midi struct.  to use later
                                midiwords[key][v3].push(midiarray[user][value[user][j] + wordindex]);
                                //we should have the user here to filter by.  words[key][v3][i].user
                                //filters are lang, word, user
                                //just get from the datatable and run though by time.  

                            }
                            //wordtimes[lang][word] = [time1, time2, time3]
                            //add this to the table.  
                        }
                        if (indexes.length > 0){
                            setTimes(key, v3, wordtimes[key][v3], user);
                        }
                    }
                }
            }
        }
    }

}


//get languages from feedback midi.  search 
//dropdown for language selection, then load meanings into table.  
//load languages.js
function getHighlightArrayA(t, dur, user=0, lang="base"){
    let value = midiarray[user][lang];
    if (value.length == 0){
        return 0;        
    }
    else{

        i = Math.round(value.length*t/dur)-1;

        if (i>0 && i<value.length-1 && value[i].time < t-vidbuffer*1000){
            while (i < value.length-1 && value[i].time < t-vidbuffer*1000){
                i++;
            }
            return i;
        }
        else {
            while (i>=0 && i < value.length && value[i].time > t-vidbuffer*1000){
                i--;
            }
            return i+1;
        }
    }
}

function getHighlightArray(t, dur, user=0, trk=0){
    
    if (midiarray[user].length == 0){
        return 0;
    }

    i = Math.round(midiarray[user].length*t/dur)-1;

    if (i>0 && i<midiarray[user].length-1 && midiarray[user][i].time < t-vidbuffer*1000){
        while (i < midiarray[user].length-1 && midiarray[user][i].time < t-vidbuffer*1000){
            i++;
        }
        return i;
    }
    else {
        while (i>=0 && i < midiarray[user].length && midiarray[user][i].time > t-vidbuffer*1000){
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

    for (const [lang, value] of Object.entries(midiarray[user])) {

        starth = getHighlightArrayA(abstime, dur, user, lang);
        


        for (i=starth; i< value.length; i++){
            //expect this in order.  
            //need better search algorithm here.  
            if (value[i].time > abstime + vidbuffer*1000){
                break;
            }
            //highlight the IDs for this time.  
            //this is undefined if these are new notes.  
            var obj = document.getElementById(lang + Math.round(value[i].time));
            if (typeof(obj) !== "undefined" && obj !== null){
                obj.style.color = "red";
            }
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

function getIntroLength(){
    if (typeof($("#intro").slider("value")) !== "undefined"){
        vidbuffer = $("#intro").slider("value");
    }
}
function seekAll(lang, word, index=0){
    //really should move this somewhere else.  
    getIntroLength();
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

function setTimes(lang, word, times, user=0){
//    table.row( 0 ).data( newData ).draw();

    dictable.rows().every(function () {
        //brute force search, not great.  
        var d = this.data();
        if (d[DIC_LANG] === lang && d[DIC_WORD] === word && d[DIC_USER] == user) {
            hyperlink = "";
            for (i=0; i<times.length; i++){
                //think this is milliseconds.  
                //think this should display ok.  
                //use id link feed + time for highlight operations.  Highlight the time on timer.  
                hyperlink += '<a id="' + lang + Math.round(times[i]) + '" href="#" onclick="seekTo(' + Math.round(times[i]/1000) + ');">' + Math.round(times[i]/1000) + '</a>, ';
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
//            this.show();
            this.invalidate(); // invalidate the data DataTables has cached for this row
        }
    
    });
    dictable.columns.adjust().draw();
}

function addDictRow(lang, word, row, user=0, add=0) {
    //if meta language then add to meta dictionary for reference.
    if (add > 0){
        if (lang == "meta"){
            metadic.row.add([
                word,
                row['midi'],
                lang,
                row['definition']
            ]).draw(false);
        }
        else{
            autodic.row.add([
                    word,
                    row['midi'],
                    lang,
                    row['definition']
                ])
                .draw(false);
        }
    }
    //very slow if we have many words.  This is problematic.  How do we make this faster?  
//    if (lang !== "meta"){
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
        
        if (word=="test"){ //initialize the table.  
//            setTimeout(function(){
                //$('.select2').val(null).trigger('change');
//                $('.select2').select2();
                dictable.columns(DIC_WORD).search("test").draw(); //have to do this to initialize the table.  Not a great solution.  
                dictable.search("").draw();
                  setTimeout(function(){
                    dictable.columns(DIC_TIMES).search((d) => d !== "").draw();
                  }, 5000);

//            }, 5000);

        }
//    }
}
