/*
	pianokeyboard.js
	Benjamin Pritchard / Kundalini Software
	15-March-2019

	Simple Javascript routine for drawing a piano keyboard onto a canvas element
	
	Usage:

		var canvas = document.getElementById("canvas");
		RedKeys = [39, 43, 46];
		DrawKeyboard(canvas, RedKeys);	

*/

var NUM_COLORS = 6;

function getColorFromSequence(seqno){
    adjust = Math.floor(seqno/NUM_COLORS); 
    adjust = adjust % (NUM_COLORS/2);
    r = 0;
    g = 0;
    b = 0;
    if (seqno % NUM_COLORS == 0){
        r = 255;
    }
    else if (seqno % NUM_COLORS == 1){
        r = 255;
        g = 127;
    }
    if (seqno % NUM_COLORS == 2){
        r = 255;
        g = 255;
    }
    if (seqno % NUM_COLORS == 3){
        g = 255;
    }
    if (seqno % NUM_COLORS == 4){
        b = 255;
    }
    if (seqno % NUM_COLORS == 5){
        r = 148;
        b = 211;
    }
    if (adjust > 0){
        r = Math.floor(r * (1-(adjust/NUM_COLORS)));
        g = Math.floor(g * (1-(adjust/NUM_COLORS)));
        b = Math.floor(b * (1-(adjust/NUM_COLORS)));
    }
    return "rgb("+r+","+g+","+b+")";
}

// canvas 		- HTML5 canvas element
// RedKeyArray  - array of keys to color red (0 = low a, 87 = high c, proceeding chromatically)
function DrawKeyboard(canvas, RedKeyArray=[], numKeys=88, whiteKeys=52) {
	
	// general characteristics of a piano

	var TOTAL_KEYS = numKeys;
	var NUM_WHITE_KEYS = whiteKeys;
//    TOTAL_KEYS = 25;
//    NUM_WHITE_KEYS = 15;
	var NUM_BLACK_KEYS = TOTAL_KEYS - NUM_WHITE_KEYS;
    var KeyLookupTable;
	var ctx = canvas.getContext("2d");

	var X_BORDER = 0;
	var Y_BORDER = 0;

	var width = canvas.width - (X_BORDER * 2);
	var height = canvas.height - (Y_BORDER * 2); 
	
	var WHITE_KEY_WIDTH = (width / NUM_WHITE_KEYS);
	var WHITE_KEY_HEIGHT = height;

	var BLACK_KEY_WIDTH = WHITE_KEY_WIDTH * .75
	var BLACK_KEY_HEIGHT = height * .66



    function DrawRectNoBorder(X, Y, Width, Height, Color1) {
		ctx.fillStyle = Color1;
		ctx.fillRect(X, Y, Width, Height);    
    }

	function DrawRectWithBorder(X, Y, Width, Height, Color1, Color2) {

		//draw border
		ctx.fillStyle = Color1;
		ctx.fillRect(X, Y, Width, Height);

		//draw inside
		ctx.fillStyle = Color2;
		ctx.fillRect(X+1,Y+1, Width-2, Height-2);

	}

	// draws a back key, based on whiteKeyIndex, where 0 <= WhiteKeyIndex < 52 
	function drawBlackKey(whiteKeyIndex, shouldBeRed = false, seqno=0) { 

        ctx.globalAlpha = 1.0;
	  if (!shouldBeRed) {

		C1 = "rgb(0,0,0)";			// black
		C2 = "rgb(20,20,20)";		// ??
		
		DrawRectWithBorder(X_BORDER + ((whiteKeyIndex+1) * WHITE_KEY_WIDTH) - (BLACK_KEY_WIDTH / 2), Y_BORDER, BLACK_KEY_WIDTH, BLACK_KEY_HEIGHT, C1, C2);

	  }
	  else {

        //use colors to indicate sequence.
        C1 = getColorFromSequence(seqno);
        seqoffset = Math.floor(seqno*2/NUM_COLORS);
        opacity = 1.0;
        if (seqoffset > 0){
            opacity = 1 - (seqoffset/6);                
        }
        DrawRectNoBorder(X_BORDER + ((whiteKeyIndex+1) * WHITE_KEY_WIDTH) - (BLACK_KEY_WIDTH / 2), seqoffset+((seqno)%NUM_COLORS)*3, BLACK_KEY_WIDTH, 4, C1);
        /*
        if (seqno > 0){
            ctx.font = "8px Arial";
            ctx.fillStyle = "rgb(255,255,255)";
            ctx.fillText(seqno, X_BORDER + ((whiteKeyIndex+1) * WHITE_KEY_WIDTH) - (BLACK_KEY_WIDTH / 2), height*0.66 -seqno*2);
        }
        */

	  }
	  
	 }

	function DrawWhiteKey(WhiteKeyIndex, shouldBeRed = false, seqno=0) {

        ctx.globalAlpha = 1.0;
	  if (!shouldBeRed) {

			C1 = "rgb(0,0,0)";			// lback
			C2 = "rgb(255,255,255)";	// white

			DrawRectWithBorder(X_BORDER + (WhiteKeyIndex * WHITE_KEY_WIDTH), Y_BORDER, WHITE_KEY_WIDTH, height, C1, C2);

	   } else {

            //use colors to indicate sequence.
            C1 = getColorFromSequence(seqno);
            seqoffset = Math.floor(seqno*2/NUM_COLORS);
            opacity = 1.0;
            if (seqoffset > 0){
                opacity = 1 - (seqoffset/6);                
            }
            ctx.globalAlpha = opacity;
            
            DrawRectNoBorder(X_BORDER + (WhiteKeyIndex * WHITE_KEY_WIDTH)+1, seqoffset+((seqno)%NUM_COLORS)*3, WHITE_KEY_WIDTH-2, 5, C1);
            /*
            if (seqno > 0){
                ctx.font = "8px Arial";
                ctx.fillStyle = "rgb(255,255,255)";
                ctx.fillText(seqno, X_BORDER + (WhiteKeyIndex * WHITE_KEY_WIDTH), height-seqno*2);
            }
            */
			
	   }
	}

	function keyType (isBlack,  White_Index, played=false) {
		this.isBlack 		= isBlack;
		this.White_Index 	= White_Index;
        this.played 		= played;
	}  

    function buildKeyLookupTable() {
		KeyLookupTable = new Array(TOTAL_KEYS);
        base = 0;
        if (TOTAL_KEYS == 88){
            KeyLookupTable[0]  = new keyType(false, 0);			// a
            KeyLookupTable[1]  = new keyType(true,  0);			// a#
            KeyLookupTable[2]  = new keyType(false, 1);			// b
            base = 3;
        }	
		NumOctaves = Math.floor(TOTAL_KEYS/12);
		for (counter=0; counter<NumOctaves; counter++) {
			octave_offset = 7 * counter;
			if (TOTAL_KEYS ==88){
                //C based X octaves.  
                octave_offset +=2;
            }
			KeyLookupTable[base+0]  = new keyType(false, octave_offset); // c
			KeyLookupTable[base+1]  = new keyType(true,  octave_offset); // c#
			KeyLookupTable[base+2]  = new keyType(false, octave_offset+1); // d
			KeyLookupTable[base+3]  = new keyType(true,  octave_offset+1); // d#
			KeyLookupTable[base+4]  = new keyType(false, octave_offset+2); // e
			KeyLookupTable[base+5]  = new keyType(false, octave_offset+3); // f
			KeyLookupTable[base+6]  = new keyType(true,  octave_offset+3); // f#
			KeyLookupTable[base+7] =  new keyType(false, octave_offset+4); // g
			KeyLookupTable[base+8] =  new keyType(true,  octave_offset+4); // g#
			KeyLookupTable[base+9] =  new keyType(false, octave_offset+5); // a
			KeyLookupTable[base+10] = new keyType(true,  octave_offset+5)  // a#
			KeyLookupTable[base+11] = new keyType(false, octave_offset+6); // b
			
			base += 12;
		}
        if (TOTAL_KEYS != 88){
            //end with C
			octave_offset = 7 * counter;
			KeyLookupTable[base+0]  = new keyType(false, octave_offset); // c
            
        }

    }

	function AbsoluteToKeyInfo(AbsoluteNoteNum) {
		
		
		return KeyLookupTable[AbsoluteNoteNum];
	}


    //only need to do this once.  
    buildKeyLookupTable();

	// just draw in all the white keys to begin with... 
	for (i = 0; i < NUM_WHITE_KEYS; i++) {
		DrawWhiteKey(i, false);
	}  

    
	// now draw all the rest of the black keys...
	// loop through all 7 octaves	
	numOctaves = Math.floor(TOTAL_KEYS/12);
	curWhiteNoteIndex = 0;
    if (TOTAL_KEYS == 88){
        curWhiteNoteIndex = 2;
    }
	
	for (octave=0; octave<numOctaves; octave++) {
		// and draw 5 black notes per octave...
		for (i=0; i<5; i++) {
			drawBlackKey(curWhiteNoteIndex, false);
			if (i == 1 || i == 4)
				curWhiteNoteIndex +=2;
			else
				curWhiteNoteIndex += 1;
		}
	} 
 
	// now draw specially white keys that need to be red...
	// just loop through all the RedKeyArray
    for (index = 0; index < RedKeyArray.length; index++){
        KeyLookup = AbsoluteToKeyInfo(RedKeyArray[index]);
        if (!KeyLookup.isBlack){
            DrawWhiteKey(KeyLookup.White_Index, true, index);
            KeyLookup.played = true;
        }
        else{
            drawBlackKey(KeyLookup.White_Index, true, index);
            KeyLookup.played = true;
        }
    }

   	
	// draw in lowest a# manually (making sure to draw it red if it should be)
//	LowestShouldBeRed = RedKeyArray.includes(1);
//	drawBlackKey(0, LowestShouldBeRed);					

	
	
	
}