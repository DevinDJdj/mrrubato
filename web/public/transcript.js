function setTranscript(transcript){
	$('#transcriptsh').html(makeTimeLinks(transcript));
	//right now this is not refreshed on page load.  
	//this ends up being the original transcript for some reason.  
	//not sure if we want this or not.  Here we dont keep history about the original transcript.  
	//is this important?  
	var tempDiv = $('#transcript');
	if (isadmin){
		tempDiv.readOnly = false;
	}
	else{
		tempDiv.readOnly = true;
		//we get the updated transcript, but cant edit further.  This removes confusion about if you can edit.  
	}
	tempDiv.val(transcript);
	createTranscriptArray();
}

function toggleTranscript(){
	if ($('#transcript').is(':visible')){
		setTranscript($('#transcript').val());
		$('#transcript').hide();
		$('#transcriptsh').show();
	}
	else{
		$('#transcript').show();
		$('#transcriptsh').hide();
	}
}


function toggleMyComments(){
	if ($('#mycomments').is(':visible')){
		createNotesArray(); //update values of the data.  
		$('#mycomments').hide();
		$('#mycommentsh').show();
	}
	else{
		$('#mycomments').show();
		$('#mycommentsh').hide();
	}
}
function loadTranscript(snapshot){
	console.log(snapshot.val().transcript);
	if (snapshot.val().transcript !==null){
		//not sure if we want this or not.  Here we dont keep history about the original transcript.  
		//is this important?  
		originaltranscript = snapshot.val().transcript;
		setTranscript(snapshot.val().transcript);
	}
}


function updateNotes(){
    var allnotes = "";
	for (i=0; i<notesarray.length; i++){
	    allnotes += notesarray[i] + "\n";
	}
    $('#mycomments').val(allnotes);
	//add clickable link inside here instead.  
	$('#mycommentsh').html(makeTimeLinks(allnotes));

  $('#mycommentsh').animate({
          scrollTop: $('#mycommentsh')[0].scrollTop+50}, "slow"
        );
  $('#mycomments').animate({
          scrollTop: $('#mycomments')[0].scrollTop+50}, "slow"
        );

	
}

function createTranscriptArray(){
//also update the new DIV with links.  
	alltranscript = $('#transcript').val();
	transcriptarray = [];
	const lines = alltranscript.split("\n");
	for (i = 0; i< lines.length; i++){
	    transcriptarray[i] = lines[i];
	}
	console.log(transcriptarray);

}

function createNotesArray(){
//also update the new DIV with links.  
	allnotes = $('#mycomments').val();
	notesarray = [];
    const lines = allnotes.split("\n");
	for (i = 0; i< lines.length; i++){
	    notesarray[i] = lines[i];
	}
	console.log(notesarray);
	//set title
    updateNotes();
}

