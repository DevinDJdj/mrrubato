; PitchShifter.csd
; Written by Iain McCurdy, 2015.

; A pitch shifter using the traditional delay buffer write-read method.
; Two buffers are used per channel (therefore four in total).
; Each overlapping buffer is gated using a hanning window in order to prevent discontinuities
; Snap		-	when activated forces 'Semitones' to an integer.

; Three modes are provided:
; 	Feedback	-	a standard single pitchshifter unit with feedback (2 feedback modes are offered)
;	Interative	-	the user can choose the number of simultaneous pitchshifter units. 
;				Pitchshifting intervals of the various units are related additively, e.g. if semitones=12, the first unit is 12, the second 24, the third 36 etc. (similar to feedback mode)
;	Harmonic	-	Iterative units are harmonically related. E.g. normal harmonic series of intervals is generated if semitones=12. i.e. first interval of the harmonic series is 1 octave

; FB.Method	-	selects from two different feedback methods:
;			  'Indiv.' - each buffer feeds back into itself
;			  'Global' - the gated and mixed buffers from each channel are fed back into both of the buffers for that channel.
; Smooth	-	Basically portamento time governing the filtering of changes made to 'Semitones' and 'Delay'. If zero, portmento filtering is bypassed entirely.  
; Window	-	Selects the window shape used to envelope the overlapping buffers

<Cabbage>
form caption("Pitch Shifter") size(840,  90), pluginid("PShf"), scrollbars(0)

#define RSliderStyle # colour("Grey"), textcolour("white"), outlinecolour("DarkGrey"), trackercolour("Silver")#

label    bounds( 10, 15, 80, 13), fontcolour("white"), text("Interval")
combobox bounds( 10, 30, 80, 20), text("Semitone","Ratio"), channel("IntervalMode"),       value(1)

image     bounds(120, 15, 35, 58), plant("Ratio"), colour(0,0,0,0), visible(0), identchannel("RatioPlant_ident") {
numberbox bounds(  5,  0, 25, 18), channel("Numerator"),        range(1,99,3,1,1)
image     bounds(  0, 26, 35,  1), shape("sharp") 
numberbox bounds(  5, 35, 25, 18), channel("Denominator"),      range(1,99,2,1,1)
}

image    bounds(110, 10,130, 70), plant("Semitones"), colour(0,0,0,0), visible(1), identchannel("SemitonesPlant_ident") {
rslider  bounds(  0,  0, 70, 70), text("Semitones"),  channel("Semitones"),      range(-48,48,7,1,0.001), $RSliderStyle
checkbox bounds( 70, 20, 60, 15), text("Snap"),       channel("Snap"), value(1), fontcolour("white")
}

label     bounds(240, 15, 80, 13), fontcolour("white"), text("Mode")
combobox  bounds(240, 30, 80, 20), text("Feedback","Iteration","Harmonic"), channel("Mode"),       value(1)
rslider  bounds(330, 10, 70, 70), text("Feedback"),    channel("Feedback"),       range(0,1,0.9,2,0.0001), visible(1), identchannel("Feedback_ident"),  $RSliderStyle
label    bounds(400, 15, 70, 13), text("FB.Method"), fontcolour("White"), visible(1), identchannel("FBLabel_ident"),
combobox bounds(400, 30, 70, 20), text("Indiv.","Global"),       channel("FBMethod"), visible(1), identchannel("FBMethod_ident"),
rslider  bounds(400, 10, 70, 70), text("Iterations"),    channel("NIter"),       range(1,10,3,1,1), identchannel("NIter_ident"), visible(0)        $RSliderStyle

rslider  bounds(470, 10, 70, 70), text("Delay"),       channel("Delay"),          range(0.01,4.00, 0.1,0.5),      $RSliderStyle
rslider  bounds(540, 10, 70, 70), text("Smooth"),      channel("Smooth"),         range(0,99,0,0.5),              $RSliderStyle
label    bounds(610, 15, 80, 13), text("Window"), fontcolour("White")
combobox bounds(610, 30, 80, 20), text("Hanning","Triangle","Half Sine","Square","Pulse","Perc.","Rev.Perc."),  channel("Window")
rslider  bounds(690, 10, 70, 70), text("Mix"),         channel("Mix"),            range(0, 1,0.5),                $RSliderStyle
rslider  bounds(760, 10, 70, 70), text("Level"),       channel("Level"),          range(0, 1.00,1),               $RSliderStyle

</Cabbage>

<CsoundSynthesizer>
<CsOptions>
-d -n
</CsOptions>
<CsInstruments>

sr 		= 	44100
ksmps 		= 	32
nchnls 		= 	2
0dbfs		=	1	;MAXIMUM AMPLITUDE


giHanning	ftgen	0, 0, 4097,  20, 2
giTriangle	ftgen	0, 0, 4097,  20, 3
giHalfSine	ftgen	0, 0, 4097,   9, 0.5, 1, 0
giSquare	ftgen	0, 0, 4097,   7, 0, 64, 1, 4096-128, 1, 64, 0
giPulse		ftgen	0, 0, 4097,  20, 6, 1, 0.5
giPerc		ftgen	0, 0, 4097,  16, 0, 64, -2, 1,   4096-64, -2, 0
giRevPerc	ftgen	0, 0, 4097,  16, 0, 4096-64, -2, 1, 64, -2, 0



opcode	pitchshifter, aa, aakkkkii	; individual buffer feedback
	ainL,ainR,kratio,kfeedback,kDelay,kSmooth,imaxdelay,iwfn	xin
	setksmps	1

	kPortTime	linseg	0,0.001,1
	;if kSmooth>0 then					; portamento smoothing
	 kratio		portk	kratio, kPortTime*kSmooth	
	 kDelay		portk	kDelay, kPortTime*kSmooth	
	;endif

	aDelay		interp	kDelay

	arate		=	(kratio-1)/kDelay		;SUBTRACT 1/1 SPEED

	aphase1		phasor	-arate				;MOVING PHASE 1-0
	aphase2		phasor	-arate, .5			;MOVING PHASE 1-0 - PHASE OFFSET BY 180 DEGREES (.5 RADIANS)
	
	agate1		tablei	aphase1, iwfn, 1, 0, 1		;
	agate2		tablei	aphase2, iwfn, 1, 0, 1		;
	
	abuf1		delayr	imaxdelay			;DECLARE DELAY BUFFER
	adelsig1	deltap3	aphase1 * aDelay		;VARIABLE TAP
	aGatedSig1	=	adelsig1 * agate1
			delayw	ainL + (aGatedSig1*kfeedback)	;WRITE AUDIO TO THE BEGINNING OF THE DELAY BUFFER, MIX IN FEEDBACK SIGNAL - PROPORTION DEFINED BY gkFB
	
	abuf2		delayr	imaxdelay			;DECLARE DELAY BUFFER
	adelsig2	deltap3	aphase2 * aDelay		;VARIABLE TAP
	aGatedSig2	=	adelsig2 * agate2
			delayw	ainL + (aGatedSig2*kfeedback)	;WRITE AUDIO TO THE BEGINNING OF THE DELAY BUFFER, MIX IN FEEDBACK SIGNAL - PROPORTION DEFINED BY gkFB

	abuf3		delayr	imaxdelay			;DECLARE DELAY BUFFER
	adelsig3	deltap3	aphase1 * aDelay		;VARIABLE TAP
	aGatedSig3	=	adelsig3 * agate1
			delayw	ainR + (aGatedSig3*kfeedback)	;WRITE AUDIO TO THE BEGINNING OF THE DELAY BUFFER, MIX IN FEEDBACK SIGNAL - PROPORTION DEFINED BY gkFB
	
	abuf4		delayr	imaxdelay			;DECLARE DELAY BUFFER
	adelsig4	deltap3	aphase2 * aDelay		;VARIABLE TAP
	aGatedSig4	=	adelsig4 * agate2
			delayw	ainR + (aGatedSig4*kfeedback)	;WRITE AUDIO TO THE BEGINNING OF THE DELAY BUFFER, MIX IN FEEDBACK SIGNAL - PROPORTION DEFINED BY gkFB
			
	aGatedMixL	=	(aGatedSig1 + aGatedSig2) * 0.5
	aGatedMixR	=	(aGatedSig3 + aGatedSig4) * 0.5
			xout	aGatedMixL, aGatedMixR
endop


opcode	pitchshifter2, aa, aakkkkii	; global feedback signal
	ainL,ainR,kratio,kfeedback,kDelay,kSmooth,imaxdelay,iwfn	xin
	setksmps	1

	kPortTime	linseg	0,0.001,1
	;if kSmooth>0 then					; portamento smoothing
	 kratio		portk	kratio, kPortTime*kSmooth	
	 kDelay		portk	kDelay, kPortTime*kSmooth	
	;endif

	aDelay		interp	kDelay

	arate		=	(kratio-1)/kDelay		;SUBTRACT 1/1 SPEED
	aphase1		phasor	-arate				;MOVING PHASE 1-0
	aphase2		phasor	-arate, .5			;MOVING PHASE 1-0 - PHASE OFFSET BY 180 DEGREES (.5 RADIANS)
	
	agate1		tablei	aphase1, iwfn, 1, 0, 1		;
	agate2		tablei	aphase2, iwfn, 1, 0, 1		;

	aGatedMixL,aGatedMixR	init	0
	
	abuf1		delayr	imaxdelay			;DECLARE DELAY BUFFER
	adelsig1	deltap3	aphase1 * aDelay		;VARIABLE TAP
	aGatedSig1	=	adelsig1 * agate1
			delayw	ainL + (aGatedMixL*kfeedback)	;WRITE AUDIO TO THE BEGINNING OF THE DELAY BUFFER, MIX IN FEEDBACK SIGNAL - PROPORTION DEFINED BY gkFB
	
	abuf2		delayr	imaxdelay			;DECLARE DELAY BUFFER
	adelsig2	deltap3	aphase2 * aDelay		;VARIABLE TAP
	aGatedSig2	=	adelsig2 * agate2
			delayw	ainL + (aGatedMixL*kfeedback)	;WRITE AUDIO TO THE BEGINNING OF THE DELAY BUFFER, MIX IN FEEDBACK SIGNAL - PROPORTION DEFINED BY gkFB

	abuf3		delayr	imaxdelay			;DECLARE DELAY BUFFER
	adelsig3	deltap3	aphase1 * aDelay		;VARIABLE TAP
	aGatedSig3	=	adelsig3 * agate1
			delayw	ainR + (aGatedMixR*kfeedback)		;WRITE AUDIO TO THE BEGINNING OF THE DELAY BUFFER, MIX IN FEEDBACK SIGNAL - PROPORTION DEFINED BY gkFB
	
	abuf4		delayr	imaxdelay			;DECLARE DELAY BUFFER
	adelsig4	deltap3	aphase2 * aDelay		;VARIABLE TAP
	aGatedSig4	=	adelsig4 * agate2
			delayw	ainR + (aGatedMixR*kfeedback)		;WRITE AUDIO TO THE BEGINNING OF THE DELAY BUFFER, MIX IN FEEDBACK SIGNAL - PROPORTION DEFINED BY gkFB
			
	aGatedMixL	=	(aGatedSig1 + aGatedSig2) * 0.5
	aGatedMixR	=	(aGatedSig3 + aGatedSig4) * 0.5
	
			xout	aGatedMixL, aGatedMixR
endop


; ITERATIVE PITCHSHIFTER
opcode	pitchshifter3, aa, aakikkiip	; global feedback signal
	ainL,ainR,kratio,iNIter,kDelay,kSmooth,imaxdelay,iwfn,iCount	xin
	setksmps	1

	kPortTime	linseg	0,0.001,1
	;if kSmooth>0 then					; portamento smoothing
	 kratioL	portk	kratio^iCount, kPortTime*kSmooth	
	 kDelay		portk	kDelay, kPortTime*kSmooth	
	;endif

	aDelay		interp	kDelay

	arate		=	(kratioL-1)/kDelay		;SUBTRACT 1/1 SPEED
	aphase1		phasor	-arate				;MOVING PHASE 1-0
	aphase2		phasor	-arate, .5			;MOVING PHASE 1-0 - PHASE OFFSET BY 180 DEGREES (.5 RADIANS)
	
	agate1		tablei	aphase1, iwfn, 1, 0, 1		;
	agate2		tablei	aphase2, iwfn, 1, 0, 1		;

	aGatedMixL,aGatedMixR	init	0
	
	abuf1		delayr	imaxdelay			;DECLARE DELAY BUFFER
	adelsig1	deltap3	aphase1 * aDelay		;VARIABLE TAP
	aGatedSig1	=	adelsig1 * agate1
			delayw	ainL				;WRITE AUDIO TO THE BEGINNING OF THE DELAY BUFFER, MIX IN FEEDBACK SIGNAL - PROPORTION DEFINED BY gkFB
	
	abuf2		delayr	imaxdelay			;DECLARE DELAY BUFFER
	adelsig2	deltap3	aphase2 * aDelay		;VARIABLE TAP
	aGatedSig2	=	adelsig2 * agate2
			delayw	ainL				;WRITE AUDIO TO THE BEGINNING OF THE DELAY BUFFER, MIX IN FEEDBACK SIGNAL - PROPORTION DEFINED BY gkFB

	abuf3		delayr	imaxdelay			;DECLARE DELAY BUFFER
	adelsig3	deltap3	aphase1 * aDelay		;VARIABLE TAP
	aGatedSig3	=	adelsig3 * agate1
			delayw	ainR				;WRITE AUDIO TO THE BEGINNING OF THE DELAY BUFFER, MIX IN FEEDBACK SIGNAL - PROPORTION DEFINED BY gkFB
	
	abuf4		delayr	imaxdelay			;DECLARE DELAY BUFFER
	adelsig4	deltap3	aphase2 * aDelay		;VARIABLE TAP
	aGatedSig4	=	adelsig4 * agate2
			delayw	ainR				;WRITE AUDIO TO THE BEGINNING OF THE DELAY BUFFER, MIX IN FEEDBACK SIGNAL - PROPORTION DEFINED BY gkFB
			
	aGatedMixL	=	(aGatedSig1 + aGatedSig2) * 0.5
	aGatedMixR	=	(aGatedSig3 + aGatedSig4) * 0.5
	
	aMixL,aMixR	init	0
	if iCount<iNIter then
	 aMixL,aMixR	pitchshifter3	ainL,ainR,kratio,iNIter,kDelay,kSmooth,imaxdelay,iwfn,iCount+1
	endif
	
			xout	aGatedMixL + aMixL, aGatedMixR + aMixR
endop


; HARMONIC ITERATIVE
opcode	pitchshifter4, aa, aakikkiip	; global feedback signal
	ainL,ainR,kratio,iNIter,kDelay,kSmooth,imaxdelay,iwfn,iCount	xin
	setksmps	1

	kratio	=	kratio * (iCount+1)/iCount
	iratio	=	i(kratio) * (iCount+1)/iCount

	kPortTime	linseg	0,0.001,1
	if kSmooth>0 then					; portamento smoothing
	 kratio		portk	kratio, kPortTime*kSmooth	
	 kDelay		portk	kDelay, kPortTime*kSmooth	
	endif

	aDelay		interp	kDelay
	;koctfract	=	kSemitones/12			;TRANSPOSITION AS FRACTION OF AN OCTAVE
	;kratio		=	cpsoct(8+koctfract)/cpsoct(8)	;RATIO OF NEW FREQ TO A DECLARED BASE FREQUENCY (MIDDLE C)

	arate		=	(kratio-1)/kDelay		;SUBTRACT 1/1 SPEED
	aphase1		phasor	-arate				;MOVING PHASE 1-0
	aphase2		phasor	-arate, .5			;MOVING PHASE 1-0 - PHASE OFFSET BY 180 DEGREES (.5 RADIANS)
	
	agate1		tablei	aphase1, iwfn, 1, 0, 1		;
	agate2		tablei	aphase2, iwfn, 1, 0, 1		;

	aGatedMixL,aGatedMixR	init	0
	
	abuf1		delayr	imaxdelay			;DECLARE DELAY BUFFER
	adelsig1	deltap3	aphase1 * aDelay		;VARIABLE TAP
	aGatedSig1	=	adelsig1 * agate1
			delayw	ainL				;WRITE AUDIO TO THE BEGINNING OF THE DELAY BUFFER, MIX IN FEEDBACK SIGNAL - PROPORTION DEFINED BY gkFB
	
	abuf2		delayr	imaxdelay			;DECLARE DELAY BUFFER
	adelsig2	deltap3	aphase2 * aDelay		;VARIABLE TAP
	aGatedSig2	=	adelsig2 * agate2
			delayw	ainL				;WRITE AUDIO TO THE BEGINNING OF THE DELAY BUFFER, MIX IN FEEDBACK SIGNAL - PROPORTION DEFINED BY gkFB

	abuf3		delayr	imaxdelay			;DECLARE DELAY BUFFER
	adelsig3	deltap3	aphase1 * aDelay		;VARIABLE TAP
	aGatedSig3	=	adelsig3 * agate1
			delayw	ainR				;WRITE AUDIO TO THE BEGINNING OF THE DELAY BUFFER, MIX IN FEEDBACK SIGNAL - PROPORTION DEFINED BY gkFB
	
	abuf4		delayr	imaxdelay			;DECLARE DELAY BUFFER
	adelsig4	deltap3	aphase2 * aDelay		;VARIABLE TAP
	aGatedSig4	=	adelsig4 * agate2
			delayw	ainR				;WRITE AUDIO TO THE BEGINNING OF THE DELAY BUFFER, MIX IN FEEDBACK SIGNAL - PROPORTION DEFINED BY gkFB
			
	aGatedMixL	=	(aGatedSig1 + aGatedSig2) * 0.5
	aGatedMixR	=	(aGatedSig3 + aGatedSig4) * 0.5
	
	aMixL,aMixR	init	0
	if iCount<iNIter then
	 aMixL,aMixR	pitchshifter4	ainL,ainR,kratio,iNIter,kDelay,kSmooth,imaxdelay,iwfn,iCount+1
	endif
	
			xout	aGatedMixL + aMixL, aGatedMixR + aMixR
endop


instr	1
	aInL,aInR	ins
	;aInL		vco2	0.2,100,4,0.5
	;aInR		=	aInL
	
	kFeedback	chnget	"Feedback"
	kNIter		chnget	"NIter"
	kNIter		init	1
	kDelay		chnget	"Delay"
	kSmooth		chnget	"Smooth"
	kMode		chnget	"Mode"
	kIntervalMode	chnget	"IntervalMode"
	
	if changed(kIntervalMode)==1 then				; semitones mode
	 if kIntervalMode==1 then
	 	chnset	"visible(0)","RatioPlant_ident"
	 	chnset	"visible(1)","SemitonesPlant_ident"
	 else								; ratio mode
	 	chnset	"visible(1)","RatioPlant_ident"
	 	chnset	"visible(0)","SemitonesPlant_ident"
	 endif
	endif
	
	if kIntervalMode==1 then
		kSemitones	chnget	"Semitones"
		kSnap		chnget	"Snap"
		if kSnap==1 then
		 if frac(kSemitones)!=0 then
		  kSemitones	=	round(kSemitones)
		  		chnset	kSemitones,"Semitones"
		 endif
		endif
	 	kRatio	=	semitone(kSemitones)	
	else
		kNumerator	chnget	"Numerator"
		kDenominator	chnget	"Denominator"
		kRatio		=	kNumerator/kDenominator
		kSemitones	=	log2(kRatio)*12	
	endif
	
	if changed(kMode)==1 then
	 if kMode==1 then
	  chnset	"visible(1)","Feedback_ident"
	  chnset	"visible(1)","FBLabel_ident"
	  chnset	"visible(1)","FBMethod_ident"
	  chnset	"visible(0)","NIter_ident"
	 elseif kMode==2 then
	  chnset	"visible(0)","Feedback_ident"
	  chnset	"visible(0)","FBLabel_ident"
	  chnset	"visible(0)","FBMethod_ident"
	  chnset	"visible(1)","NIter_ident"
	 else
	  chnset	"visible(0)","Feedback_ident"
	  chnset	"visible(0)","FBLabel_ident"
	  chnset	"visible(0)","FBMethod_ident"
	  chnset	"visible(1)","NIter_ident"
	 endif
	endif
	
	
	iMaxDelay	=	4
	kWindow		chnget	"Window"
	kWindow		init	1
	if changed(kWindow)==1 then
	 reinit UPDATE
	endif
	UPDATE:
	iWfn	=	giHanning + i(kWindow) - 1

	if kMode==1 then
	 kFBMethod	chnget	"FBMethod"
	 kFBMethod	init	1
	 if kFBMethod==1 then
	  aPS_L,aPS_R	pitchshifter	aInL,aInR,kRatio,kFeedback,kDelay,kSmooth,iMaxDelay,iWfn
	 elseif kFBMethod==2 then
	  aPS_L,aPS_R	pitchshifter2	aInL,aInR,kRatio,kFeedback,kDelay,kSmooth,iMaxDelay,iWfn	
	 endif
	elseif kMode==2 then
	 if changed(kNIter)==1 then
	  reinit UPDATE3
	 endif
	 UPDATE3:
	 aPS_L,aPS_R	pitchshifter3	aInL,aInR,kRatio,i(kNIter),kDelay,kSmooth,iMaxDelay,iWfn	
	elseif kMode==3 then		; HARMONIC ITERATIVE
	 if changed(kNIter)==1 then
	  reinit UPDATE4
	 endif
	 ;aFBL,aFBR	init	0
	 UPDATE4:
	 ;aPS_L,aPS_R	pitchshifter4	aInL+aFBL,aInR+aFBL,semitone(kSemitones-12),i(kNIter),kDelay,kSmooth,iMaxDelay,iWfn	
	 aPS_L,aPS_R	pitchshifter4	aInL,aInR,semitone(kSemitones-12),i(kNIter),kDelay,kSmooth,iMaxDelay,iWfn	
	 ;aFBL	=	aPS_L*kFeedback
	 ;aFBR	=	aPS_R*kFeedback
	endif

	rireturn
	kMix		chnget	"Mix"
	aMixL		ntrpol	aInL,aPS_L,kMix
	aMixR		ntrpol	aInR,aPS_R,kMix
	kLevel		chnget	"Level"
			outs	aMixL*kLevel, aMixR*kLevel
endin

</CsInstruments>

<CsScore>
i 1 0 [60*60*24*7]
</CsScore>

</CsoundSynthesizer>