/*
importScripts('ExtPay.js')

// To test payments, replace 'sample-extension' with the ID of
// the extension you registered on ExtensionPay.com. You may
// need to uninstall and reinstall the extension.
// And don't forget to change the ID in popup.js too!
var extpay = ExtPay('my-side-panel');
extpay.startBackground(); // this line is required to use ExtPay in the rest of your extension

extpay.getUser().then(user => {
	console.log(user)
})
*/
//this not working.  
//maybe use chrome.tabs.create and use a static page with SR kit.  

async function getCurrentTab() {
    let queryOptions = { active: true, lastFocusedWindow: true };
    let [tab] = await chrome.tabs.query(queryOptions);
    return tab;
  }

async function toggleSpeechToText() {
    const activeTab = await getCurrentTab();
  
    chrome.tabs.sendMessage(activeTab.id, { command: "toggleRecognition" });
    chrome.scripting.executeScript({
      target: { tabId: activeTab.id },
      function: function() {
        const button = document.getElementById("speechToTextButton");
        if (button) {
          button.style.display = "block";
        }
      }
    });
  }
  
  chrome.action.onClicked.addListener(() => {
//    toggleSpeechToText();

	globals().then(function ($GLOBALS) { // Version 1.7.0
		//chrome.tabs.create({"url": "http://seabreezecomputers.com/rater"});
		if ($GLOBALS.tab_id == false)
			open_sr_page(); // Open speech recognition page if it is not open
		else if ($GLOBALS.sra && $GLOBALS.sra.settings && $GLOBALS.sra.settings['click_to_close']) // Version 1.2.0 // Version 1.5.7 - Added sra && sra.settings && in case chrome.storage.sync.clear() or chrome.storage.local.clear()
			chrome.tabs.remove($GLOBALS.tab_id);
		else
		{
			//var active_toggle = sra.settings['start_in_background'] ? false : true;
			chrome.tabs.update($GLOBALS.tab_id, {active: true}); // Focus on the page if it is not focused
			chrome.windows.update($GLOBALS.window_id, {focused: true}); // Version 1.2.0 - Focus on the window
		}
		//console.log("clicked");
	});
});
  
  chrome.commands.onCommand.addListener((command) => {
    if (command === "toggle_speech_to_text") {
      toggleSpeechToText();
    }
    else if (command === "mic_on"){
        //chrome.action.setIcon();
        chrome.action.setBadgeText({text: "on"}); // Version 1.1.8 - Initializing...
    }
    else if (command === "mic_off"){
//        chrome.action.setIcon();
        chrome.action.setBadgeText({text: "off"}); // Version 1.1.8 - Initializing...
    }
    else if (command === "record_start"){
        chrome.action.setBadgeBackgroundColor({"color": [255, 0, 0, 100]}); 

    }
    else if (command === "record_stop"){
        chrome.action.setBadgeBackgroundColor({"color": [255, 255, 255, 100]}); 

    }
  });


  async function globals() {
	var $GLOBALS = {};
	$GLOBALS.test_mode = ('update_url' in chrome.runtime.getManifest()) ? false : true; // If loaded from Web Store instead of local folder than getManifest has update_url property
	$GLOBALS.running_script = "background";
	$GLOBALS.tab_id = false; // Will be id of Speech Recognition tab window when it is open
	$GLOBALS.tab_url = false; // Will be url of Speech Recognition tab window
	$GLOBALS.window_id = false; // Version 1.2.0 - Will be window id of Speech Recognition tab
	$GLOBALS.last_active_tab = false;
	
	// Get sr.html tab if it exists
	//var re = new RegExp("^chrome-extension:(.*?)\/sr.html$" 'i');
	//var re = new RegExp("^chrome-extension:\/\/"+chrome.runtime.id+"\/sr.html$" 'i');
	var re = RegExp(chrome.runtime.getURL("sidepanel.html"), "i");
	var tabs = await chrome.tabs.query({}); // https://stackoverflow.com/a/68787047/4307527
	tabs.forEach(function (tab) {
		// if (tab.url.match(/^chrome-extension:(.*?)\/sr.html$/i)) {
		if (tab.url.match(re)) {
			$GLOBALS.tab_id = tab.id;
			$GLOBALS.tab_url = tab.url;
			$GLOBALS.window_id = tab.windowId; // Version 1.7.0
		}
	});
	
	
	// Get all chrome.storage.local
	$GLOBALS.sra = await getAllStorageSyncData(null);
	//$GLOBALS = me($GLOBALS);
	return $GLOBALS; // return global variables object
}


function getAllStorageSyncData(top_key) {
    // Immediately return a promise and start asynchronous work
    return new Promise((resolve, reject) => {
      // Asynchronously fetch all data from storage.sync.
      chrome.storage.local.get(top_key, (items) => {
        // Pass any observed errors down the promise chain.
        if (chrome.runtime.lastError) {
          return reject(chrome.runtime.lastError);
        }
        // Pass the data retrieved from storage down the promise chain.
        resolve(items);
      });
    });
  }
  

  function open_sr_page() {
	globals().then(function ($GLOBALS) { // Version 1.7.0
		var active_toggle = ($GLOBALS.sra && $GLOBALS.sra.settings && $GLOBALS.sra.settings['start_in_background']) ? false : true; // Version 1.5.7 - Added sra && sra.settings && 
		var pin_tab = ($GLOBALS.sra && $GLOBALS.sra.settings && $GLOBALS.sra.settings['pin_tab']) ? true : false; // Version 1.7.15f - Added
		// Found out I don't really need chrome.extension.getURL. It understands relative paths
		//chrome.tabs.create({"url":chrome.extension.getURL("sr.html"),"selected":true}, function(tab){
		chrome.tabs.create({"url":"sidepanel.html","active":active_toggle,"pinned":pin_tab}, function(tab){ // Version 1.7.2 - From selected to active because selected deprecated
			if ($GLOBALS.test_mode) // Version 1.7.0
				console.log(tab); // Version 1.3.2 test
			$GLOBALS.tab_id = tab.id;
			$GLOBALS.tab_url = tab.pendingUrl || tab.url; // Version 1.3.2 - Chrome 79 added PendingUrl on 12/17/2019 - https://developer.chrome.com/extensions/tabs
			$GLOBALS.window_id = tab.windowId; // Version 1.2.0
			//updateBadge(); // Version 1.1.8 - Removed
			chrome.action.setBadgeText({text: "..."}); // Version 1.1.8 - Initializing...
//			chrome.action.setBadgeBackgroundColor({"color": [255, 0, 0, 100]}); 
			chrome.tabs.update(tab.id, {autoDiscardable: false}); // Version 1.7.15 - Added
		});

        
	});
  }



  
function doStuffWithDom(domContent) {
    console.log('I received the following DOM content:\n' + domContent);
}
