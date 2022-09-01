; FogFilePlayer.csd
; Written by Iain McCurdy, 2015

; File player based around the granular synthesis opcode, 'fog'.
; A second voice can be activated (basically another parallel granular synthesiser) with parameter variations of density, transposition, pointer location (Phs) and delay.
; Two modes of playback are available: manual pointer and speed
; The pointer and grain density can also be modulated by clicking and dragging on the waveform view.
;  * This will also start and stop the grain producing instrument.
;  * In click-and-drag mode mouse X position equates to pointer position and mouse Y position equates to grain density. 
; If played from the MIDI keyboard, note number translates to 'Transposition' and key velocity translates to amplitude for the grain stream for that note.

; In 'Pointer' mode pointer position is controlled by the long 'Manual' slider with an optional amount of randomisation determined ny the 'Phs.Mod' slider.  

; Selecting 'Speed' pointer mode bring up some additional controls:
; Speed		-	speed ratio
; Freeze	-	freezes the pointer at its present locations 
; Range		-	ratio of the full sound file duration that will be played back. 1=the_entire_file, 0.5=half_the_file, etc. 
; Shape		-	shape of playback function: 	'Phasor' looping in a single direction
;												'Tri' back and forth looping
;												'Sine' back and forth looping using a sinudoidal shape - i.e. slowing at the extremes of the oscillation
; The 'Manual' control functions as an pointer offset when using 'Speed' pointer mode

; Density	-	grains per second
; Oct.Div	-	thinning the density in overlapping octave steps. I.e. density is halved and then halved again etc. 
; Transpose	-	transposition as a ratio. Negative values result in grains playing in reverse.
; Transposition Mode - timing of transposition changes: 'Grain by Grain' 	- grains always maintain the transposition with which they began
;														'Continuous'		- even grains in progress can be altered by changes made to 'Transpose' 

; --Randomisation--
; Trans.Mod.	-	randomisation of transposition (in octaves)
; Ptr.Mod.	-	randomisation of pointer position
; Dens Mod.	-	randomisation of grain density
; Amp.Mod.	-	randomisation of grain amplitude. Note that this is done on a grain by grain basis, grains retain the amplitude with which they start.

; --Density LFO--
; Depth		-	depth of LFO modulation of grain density
; Rate		-	rate of LFO modulation of grain density

; --Voice 2--
; Dens.Ratio	-	ratio of grain density of voice 2 with respect to the main voice (also adjustable using the adjacent number box for precise value input)
; Ptr.Diff.	-	pointer position offset of voice 2 with respect to the main voice (also adjustable using the adjacent number box for precise value input)
; Trans.Diff.	-	transposition offset of voice 2 with respect to the main voice (also adjustable using the adjacent number box for precise value input)
; Delay		-	a delay applied to voice 2 which is defined as a ratio of the gap between grains (therefore delay time will be inversely proportional to garin density)
;			 This is a little like a phase offset for voice 2 with respect to that of the main voice.
;			 When using this control 'Dens.Ratio' should be '1' otherwise continuous temporally shifting between the grains of voice 2 and the main voice will be occurring anyway.

; --Envelope--
; Attack	-	amplitude envelope attack time for the envelope applied to complete notes
; Release	-	amplitude envelope release time for the envelope applied to complete notes

; --Control--
; MIDI Ref.	-	MIDI note that represent unison (no transposition) for when using the MIDI keyboard
; Level	-	output amplitude control


<Cabbage>
form caption("fog File Player") size(1130,445), colour(0,0,0), pluginid("FgFP"), guirefresh(16)	; guirefresh value adjusts how often the cabbage valuators are read. This can affect the usability of parameters used in realtime gesturing.

#define RSliderStyle # trackercolour(130,135,170), textcolour("white"), outlinecolour( 10, 15, 50), colour( 50, 45, 90)#

image       bounds(  0,  0,1130,445), colour( 30, 35, 70), outlinecolour("White"), shape("sharp"), line(3)	; main panel colouration    
soundfiler  bounds(  5,  5,1120,175), channel("beg","len"), identchannel("filer1"),  colour(0, 255, 255, 255), fontcolour(160, 160, 160, 255), 
label bounds(7, 5, 560, 14), text(""), align(left), colour(0,0,0,0), fontcolour(200,200,200), identchannel("stringbox")

hslider    bounds(  0,180,1120, 15), channel("phs"),   range( 0,1,0,1,0.0001), $RSliderStyle
label      bounds(  0,195,1120, 13), text("Manual"), fontcolour("white")

filebutton bounds(  5,210,  80, 25), text("Open File","Open File"), fontcolour("white") channel("filename"), shape("ellipse")
checkbox   bounds(  5,240,  95, 20), channel("PlayStop"), text("Play/Stop"), fontcolour("white")
label      bounds(  5,263, 145, 12), text("[or right-click and drag]"), fontcolour("white"), align("left")

label       bounds( 90,215, 75, 13), text("Ptr.Mode"), fontcolour("white")
combobox    bounds( 90,230, 75, 18), channel("PhsMode"), items("Manual", "Speed"), value(2),fontcolour("white")

rslider     bounds(170,215, 60, 60), channel("port"),     range( 0, 30.00, 0.01,0.5,0.01), text("Port."), identchannel("portID"), visible(0), $RSliderStyle

rslider     bounds(170,215, 60, 60), channel("spd"),     range( -2.00, 2.00, 1), text("Speed"), identchannel("spdID"), visible(0), $RSliderStyle
button      bounds(230,230, 60, 18), channel("freeze"),  colour:0(  0,  0,  0), colour:1(50,55,150), text("Freeze","Freeze"), fontcolour:0(50,50,50), fontcolour:1(200,200,255), identchannel("freezeID"), visible(0)
rslider     bounds(290,215, 60, 60), channel("range"),   range(0.01,  1,  1),              text("Range"),  identchannel("rangeID"), visible(0), $RSliderStyle
label       bounds(350,215, 60, 13), text("Shape"), fontcolour("white"), identchannel("shapelabelID")
combobox    bounds(350,230, 60, 18), channel("shape"), items("phasor","tri.","sine"), value(1),fontcolour("white"), identchannel("shapeID"), visible(0)

rslider     bounds(410,215, 60, 60), channel("dens"),    range(  1,500,   30, 0.5),  text("Density"), $RSliderStyle
rslider     bounds(470,215, 60, 60), channel("OctDiv"),  range(  0,  8,    0, 0.5),  text("Oct.Div."), $RSliderStyle
rslider     bounds(530,215, 60, 60), channel("pch"),     range(-2,2,1,1,0.001),              text("Transpose"), $RSliderStyle
label       bounds(595,210,120, 13), text("Transposition Mode"), fontcolour("white")
combobox    bounds(595,225,120, 18), channel("TransMode"), items("Grain by Grain","Continuous"), value(1),fontcolour("white")

image       bounds(730,202,260,75), colour(0,0,0,0), outlinecolour("grey"), outlinethickness(1), shape("sharp"), plant("GrainEnv"), { 
label       bounds(  0,  3,260, 8), text("G  R  A  I  N     E  N  V  E  L  O  P  E"), fontcolour("white")
rslider     bounds( 10, 13, 60, 60), channel("dur"),     range(0.01, 2,    0.1, 0.5,0.0001),                    text("Duration"),  $RSliderStyle
rslider     bounds( 70, 13, 60, 60), channel("ris"),     range(0.001,0.2,  0.01,0.5,0.0001),  text("Rise"),      $RSliderStyle
rslider     bounds(130, 13, 60, 60), channel("dec"),     range(0.001,0.2,  0.01,0.5,0.0001),                    text("Decay"),     $RSliderStyle
rslider     bounds(190, 13, 60, 60), channel("band"),    range(0,    100,  10,  0.5,0.0001),                    text("Bandwidth"), $RSliderStyle
}

image      bounds(995,202,130,75), colour(0,0,0,0), outlinecolour("grey"), outlinethickness(1), shape("sharp"), plant("envelope"), { 
label      bounds(  0,  3,130, 8), text("E   N   V   E   L   O   P   E"), fontcolour("white")
rslider    bounds(  5, 13, 60, 60), channel("AttTim"),    range(0, 5, 0, 0.5, 0.001),       text("Attack"), $RSliderStyle
rslider    bounds( 65, 13, 60, 60), channel("RelTim"),    range(0.01, 5, 0.05, 0.5, 0.001), text("Release"), $RSliderStyle
}

image       bounds(  5,282,250,75), colour(0,0,0,0), outlinecolour("grey"), outlinethickness(1), shape("sharp"), plant("randomise"), { 
label       bounds(  0,  3,250, 8), text("R  A  N  D  O  M  I  S  E"), fontcolour("white")
rslider     bounds(  5, 13, 60, 60), channel("fmd"),     range(    0, 1,    0), text("Trans.Mod."), $RSliderStyle
rslider     bounds( 65, 13, 60, 60), channel("pmd"),     range(    0, 1,    0.0055,0.25,0.00001),  text("Ptr.Mod."), $RSliderStyle
rslider     bounds(125, 13, 60, 60), channel("DensRnd"), range(    0, 2,    0), text("Dens.Mod."), $RSliderStyle
rslider     bounds(185, 13, 60, 60), channel("AmpRnd"), range(    0, 1,    0), text("Amp.Mod."), $RSliderStyle
}

image      bounds(260,282,190,75), colour(0,0,0,0), outlinecolour("grey"), outlinethickness(1), shape("sharp"), plant("LFO"), { 
label      bounds(  0,  3,190, 8), text("L  F  O"), fontcolour("white")
rslider    bounds(  5, 13, 60, 60), channel("DensLFODep"), range(-2, 2, 0, 1, 0.001),       text("Density"), $RSliderStyle
rslider    bounds( 65, 13, 60, 60), channel("AmpLFODep"),  range(-1, 1, 0, 1, 0.001),  text("Amplitude"),  $RSliderStyle
rslider    bounds(125, 13, 60, 60), channel("LFORte"),     range(0.01, 8, 0.1, 0.5, 0.001),  text("Rate"),  $RSliderStyle
}
                              
image      bounds(455,282,485,75), colour(0,0,0,0), outlinecolour("grey"), outlinethickness(1), shape("sharp"), plant("dual"), { 
label      bounds(  0,  3,485, 8), text("V  O  I  C  E     2"), fontcolour("white")
checkbox   bounds( 10, 10, 70, 15), channel("DualOnOff"), text("On/Off"), fontcolour("white")
rslider    bounds( 60, 13, 60, 60), channel("DensRatio"),   range(0.5,2,1,0.64,0.00001), text("Dens.Ratio"), $RSliderStyle
numberbox  bounds(120, 25, 60, 20), channel("DensRatio"),   range(0.5,2,1,0.64,0.00001),  textcolour("white"), trackercolour(190,170,130), outlinecolour(100,100,100)
rslider    bounds(180, 13, 60, 60), channel("PtrDiff"),   range(-1,1,0,1,0.00001), text("Ptr.Diff."), $RSliderStyle
numberbox  bounds(240, 25, 60, 20), channel("PtrDiff"),   range(-1,1,0,1,0.00001), textcolour("white"), trackercolour(190,170,130), outlinecolour(100,100,100)
rslider    bounds(300, 13, 60, 60), channel("TransDiff"),   range(-2,2,0,1,0.00001), text("Trans.Diff."), $RSliderStyle
numberbox  bounds(360, 25, 60, 20), channel("TransDiff"),   range(-2,2,0,1,0.00001), textcolour("white"), trackercolour(190,170,130), outlinecolour(100,100,100)
rslider    bounds(420, 13, 60, 60), channel("Delay"),       range(0,1,0,1,0.00001), text("Delay"), $RSliderStyle
}

image      bounds(945,282,130,75), colour(0,0,0,0), outlinecolour("grey"), outlinethickness(1), shape("sharp"), plant("control"), { 
label      bounds(  0,  3,130, 8), text("C   O   N   T   R   O   L"), fontcolour("white")
rslider    bounds(  5, 13, 60, 60), channel("MidiRef"),   range(0,127,60, 1, 1),   text("MIDI Ref."), $RSliderStyle
rslider    bounds( 65, 13, 60, 60), channel("level"),     range(  0,  3.00, 0.7, 0.5, 0.001), text("Level"), $RSliderStyle
}

keyboard bounds(5,365,1120, 75)
}
</Cabbage>

<CsoundSynthesizer>

<CsOptions>
-n -+rtmidi=NULL -M0 -dm0
</CsOptions>
                         
<CsInstruments>

sr = 44100
ksmps = 64
nchnls = 2
0dbfs=1

massign	0,3
gichans		init	0
giReady		init	0
gSfilepath	init	""

giTriangle	ftgen	0, 0, 4097,  20, 3

; CURVE USED TO FORM ATTACK AND DECAY PORTIONS OF EACH GRAIN
;              NUM | INIT_TIME | SIZE | GEN_ROUTINE |  PARTIAL_NUMBER_1 | STRENGTH_1 | PHASE_1 | DC_OFFSET_1
giattdec ftgen  0,        0,     524288,     19,             0.5,             0.5,        270,         0.5	; I.E. A RISING SIGMOID

opcode	NextPowerOf2i,i,i
 iInVal	xin
 icount	=	1
 LOOP:
 if 2^icount>iInVal then
  goto DONE
 else
  icount	=	icount + 1
  goto LOOP
 endif
 DONE:
 	xout	2^icount
endop

opcode FileNameFromPath,S,S		; Extract a file name (as a string) from a full path (also as a string)
 Ssrc	xin				; Read in the file path string
 icnt	strlen	Ssrc			; Get the length of the file path string
 LOOP:					; Loop back to here when checking for a backslash
 iasc	strchar Ssrc, icnt		; Read ascii value of current letter for checking
 if iasc==92 igoto ESCAPE		; If it is a backslash, escape from loop
 loop_gt	icnt,1,0,LOOP		; Loop back and decrement counter which is also used as an index into the string
 ESCAPE:				; Escape point once the backslash has been found
 Sname	strsub Ssrc, icnt+1, -1		; Create a new string of just the file name
	xout	Sname			; Send it back to the caller instrument
endop

instr	1
 kRampUp	linseg	0,0.001,1
 gkport		chnget	"port"
 gkloop		chnget	"loop"
 gkPlayStop	chnget	"PlayStop"
 gkPhsMode	chnget	"PhsMode"
 gkPhsMode	init	1
 gklevel	chnget	"level"
 gklevel	port	gklevel,0.05
 gkpch		chnget	"pch" 
 gkspd		chnget	"spd"
 gkfreeze	chnget	"freeze"
 gkrange	chnget	"range"
 gkshape	chnget	"shape"
 gkTransMode	chnget	"TransMode"
 gkTransMode	init	1
 gkOctDiv	chnget	"OctDiv"
 gkband		chnget	"band"
 gkris		chnget	"ris"
 gkdec		chnget	"dec"
 gkdur		chnget	"dur"   
 gkfmd		chnget	"fmd"
 gkpmd		chnget	"pmd"
 gkDensRnd	chnget	"DensRnd"
 gkAmpRnd	chnget	"AmpRnd"
 gkDensLFODep	chnget	"DensLFODep"
 gkAmpLFODep	chnget	"AmpLFODep"
 gkLFORte	chnget	"LFORte"
 gkDualOnOff	chnget	"DualOnOff"
 gkDensRatio	chnget	"DensRatio"
 gkPtrDiff	chnget	"PtrDiff"
 gkPtrDiff	port	gkPtrDiff,0.1
 gkTransDiff	chnget	"TransDiff"
 gkDelay	chnget	"Delay"
 gkDelay	port	gkDelay,0.1
      
 if changed(gkPhsMode)==1 then
  if gkPhsMode==1 then
   	chnset	"visible(0)", "spdID"
   	chnset	"visible(0)", "freezeID"
   	chnset	"visible(0)", "rangeID"
   	chnset	"visible(0)", "shapeID"
   	chnset	"visible(0)", "shapelabelID"
   	chnset	"visible(1)", "portID"
  elseif gkPhsMode==2 then
   	chnset	"visible(1)", "spdID"
   	chnset	"visible(1)", "freezeID"
   	chnset	"visible(1)", "rangeID"
   	chnset	"visible(1)", "shapeID"
   	chnset	"visible(1)", "shapelabelID"
   	chnset	"visible(0)", "portID"
  endif
 endif
          
 gSfilepath	chnget	"filename"
 kNewFileTrg	changed	gSfilepath	; if a new file is loaded generate a trigger
 if kNewFileTrg==1 then				; if a new file has been loaded...
  event	"i",99,0,0					; call instrument to update sample storage function table 
 endif  

 /* START/STOP SOUNDING INSTRUMENT */
 ktrig	trigger	gkPlayStop,0.5,0
 schedkwhen	ktrig,0,0,2,0,-1

 /* MOUSE SCRUBBING */
 gkMOUSE_DOWN_RIGHT	chnget	"MOUSE_DOWN_RIGHT"	; Read in mouse left click status
 kStartScrub		trigger	gkMOUSE_DOWN_RIGHT,0.5,0
 if gkMOUSE_DOWN_RIGHT==1 then
  if kStartScrub==1 then 
   reinit RAMP_FUNC
  endif
  RAMP_FUNC:
  krampup	linseg	0,0.001,1
  rireturn
  kMOUSE_X	chnget	"MOUSE_X"
  kMOUSE_X	portk	kMOUSE_X,gkport*kRampUp
  kMOUSE_Y	chnget	"MOUSE_Y"
  kMOUSE_X	=	(kMOUSE_X - 5) / 1120
  kMOUSE_Y	portk	1 - ((kMOUSE_Y - 5) / 175), krampup*0.05		; SOME SMOOTHING OF DENSITY CHANGES VIA THE MOUSE ENHANCES PERFORMANCE RESULTS. MAKE ANY ADJUSTMENTS WITH ADDITIONAL CONSIDERATION OF guirefresh VALUE 
  gkphs		limit	kMOUSE_X,0,1
  gkdens	limit	((kMOUSE_Y^3) * 502) - 2, 0, 500
  schedkwhen	kStartScrub,0,0,2,0,-1
 else
  gkphs		chnget	"phs"
  gkphs		portk	gkphs,gkport*kRampUp
  gkdens	chnget	"dens"
 endif
 
endin

instr	99	; load sound file
 gichans	filenchnls	gSfilepath			; derive the number of channels (mono=1,stereo=2) in the sound file
 iFtlen		NextPowerOf2i	filelen:i(gSfilepath)*sr
 gitableL	ftgen	1,0,iFtlen,1,gSfilepath,0,0,1
 if gichans==2 then
  gitableR	ftgen	2,0,iFtlen,1,gSfilepath,0,0,2
 endif
 giReady 	=	1					; if no string has yet been loaded giReady will be zero
 Smessage sprintfk "file(%s)", gSfilepath			; print sound file to viewer
 chnset Smessage, "filer1"

 /* WRITE FILE NAME TO GUI */
 Sname FileNameFromPath	gSfilepath				; Call UDO to extract file name from the full path
 Smessage sprintfk "text(%s)",Sname
 chnset Smessage, "stringbox"

endin

instr	2	; triggered by 'play/stop' button
 if gkPlayStop==0&&gkMOUSE_DOWN_RIGHT==0 then
  turnoff
 endif
 if giReady = 1 then						; i.e. if a file has been loaded
  
  /* ENVELOPE */
  iAttTim	chnget	"AttTim"				; read in widgets
  iRelTim	chnget	"RelTim"
  if iAttTim>0 then						; is amplitude envelope attack time is greater than zero...
   kenv	linsegr	0,iAttTim,1,iRelTim,0				; create an amplitude envelope with an attack, a sustain and a release segment (senses realtime release)
  else            
   kenv	linsegr	1,iRelTim,0					; create an amplitude envelope with a sustain and a release segment (senses realtime release)
  endif
  kenv	expcurve	kenv,8					; remap amplitude value with a more natural curve
  aenv	interp		kenv					; interpolate and create a-rate envelope

  kporttime	linseg	0,0.001,0.05				; portamento time function. (Rises quickly from zero to a held value.)

  kSwitch		changed	gkTransMode
  if	kSwitch==1	then		;IF I-RATE VARIABLE CHANGE TRIGGER IS '1'...
  	reinit	START			;BEGIN A REINITIALISATION PASS FROM LABEL 'START'
  endif
  START:

  kPmdRnd	unirand	gkpmd
  
  if gkPhsMode==1||gkMOUSE_DOWN_RIGHT==1 then
   kptr		portk	gkphs+kPmdRnd, kporttime	; PORTAMENTO IS APPLIED TO SMOOTH VALUE CHANGES VIA THE FLTK SLIDERS
   kptr		mirror	kptr,0,1
   kptr		=	kptr * (nsamp(1)/ftlen(1))
   aptr		interp	kptr				; A NEW A-RATE VARIABLE (aptr) IS CREATED BASE ON kptr
  else
   if gkshape==1 then
    kptr		phasor	(gkspd * sr * (1-gkfreeze))/(nsamp(1) * gkrange)
   elseif gkshape==2 then
    kptr		oscili	1,(gkspd * sr * (1-gkfreeze))/(nsamp(1) * gkrange),giTriangle
   elseif gkshape==3 then
    kptr		oscili	0.5,(gkspd * sr * (1-gkfreeze))/(nsamp(1) * gkrange)
    kptr		+=		0.5
   endif
   kptr	=	kptr * (nsamp(1)/ftlen(1)) * gkrange
   kptr	+=	(gkphs+kPmdRnd) * (nsamp(1)/ftlen(1))
   kptr	mirror	kptr,0,nsamp(1)/ftlen(1)
  endif
  aptr		interp	kptr
  
  iNumOverLaps	=	2000
  itotdur		=	3600
  
  kPchRnd	bexprnd	gkfmd					; random pitch
  kpch		=	gkpch * octave(kPchRnd)

  kRndTrig	init	1
  ;kdens		init	30					; set to initial widget value
  kDensRnd	bexprnd	gkDensRnd	;randomh	-gkDensRnd, gkDensRnd, kdens
  kdens	=	gkdens * octave(kDensRnd)
  kRndTrig	metro	kdens

  /* amplitude random modulation */
  kAmpRnd	random	0,gkAmpRnd
  klevel	=		gklevel-sqrt(kAmpRnd)

  /* LFO */
  kDensLFO	poscil	gkDensLFODep,gkLFORte
  kdens	=		kdens * octave(kDensLFO)
  kAmpLFO	poscil	gkAmpLFODep*0.5,gkLFORte
  klevel	*=		1-((kAmpLFO+(abs(gkAmpLFODep)*0.5))^2)

  if gichans==1 then						; if mono...
  a1	fog	klevel, kdens, kpch, aptr, gkOctDiv, gkband, gkris, gkdur, gkdec, iNumOverLaps, 1, giattdec, itotdur, 0, i(gkTransMode)-1, 1
   if gkDualOnOff==1 then
    a1b	fog	klevel, kdens*gkDensRatio, kpch*octave(gkTransDiff), aptr+(gkPtrDiff*nsamp(1)/ftlen(1)), gkOctDiv, gkband, gkris, gkdur, gkdec, iNumOverLaps, 1, giattdec, itotdur, 0, i(gkTransMode)-1, 1
    if gkDelay>0 then
     a1b	vdelay	a1b,(gkDelay*1000)/gkdens,1000
    endif
    a1	+=	a1b
   endif
 	outs	a1*aenv,a1*aenv				; send mono audio to both outputs 
  elseif gichans==2 then						; otherwise, if stereo...
   a1	fog	klevel, kdens, kpch, aptr, gkOctDiv, gkband, gkris, gkdur, gkdec, iNumOverLaps, 1, giattdec, itotdur, 0, i(gkTransMode)-1, 1
   a2	fog	klevel, kdens, kpch, aptr, gkOctDiv, gkband, gkris, gkdur, gkdec, iNumOverLaps, 2, giattdec, itotdur, 0, i(gkTransMode)-1, 1
   if gkDualOnOff==1 then
    a1b	fog	klevel, kdens*gkDensRatio, kpch*octave(gkTransDiff), aptr+(gkPtrDiff*nsamp(1)/ftlen(1)), gkOctDiv, gkband, gkris, gkdur, gkdec, iNumOverLaps, 1, giattdec, itotdur, 0, i(gkTransMode)-1, 1
    a2b	fog	klevel, kdens*gkDensRatio, kpch*octave(gkTransDiff), aptr+(gkPtrDiff*nsamp(1)/ftlen(1)), gkOctDiv, gkband, gkris, gkdur, gkdec, iNumOverLaps, 2, giattdec, itotdur, 0, i(gkTransMode)-1, 1
    if gkDelay>0 then
     a1b	vdelay	a1b,(gkDelay*1000)/gkdens,1000
     a2b	vdelay	a2b,(gkDelay*1000)/gkdens,1000
    endif
    a1	+=	a1b
    a2	+=	a2b
   endif
 	outs	a1*aenv,a2*aenv				; send stereo signal to outputs
  endif
  rireturn

 endif
endin

instr	3
 icps	cpsmidi							; read in midi note data as cycles per second
 iamp	ampmidi	1						; read in midi velocity (as a value within the range 0 - 1)
 iAttTim	chnget	"AttTim"				; read in widgets
 iRelTim	chnget	"RelTim"
 iMidiRef	chnget	"MidiRef"
 iFrqRatio		=	icps/cpsmidinn(iMidiRef)	; derive playback speed from note played in relation to a reference note (MIDI note 60 / middle C)

 if giReady = 1 then						; i.e. if a file has been loaded
  iAttTim	chnget	"AttTim"				; read in widgets
  iRelTim	chnget	"RelTim"
  if iAttTim>0 then						; is amplitude envelope attack time is greater than zero...
   kenv	linsegr	0,iAttTim,1,iRelTim,0				; create an amplitude envelope with an attack, a sustain and a release segment (senses realtime release)
  else            
   kenv	linsegr	1,iRelTim,0					; create an amplitude envelope with a sustain and a release segment (senses realtime release)
  endif
  kenv	expcurve	kenv,8					; remap amplitude value with a more natural curve
  aenv	interp		kenv					; interpolate and create a-rate envelope

  kporttime	linseg	0,0.001,0.05				; portamento time function. (Rises quickly from zero to a held value.)

  kSwitch		changed	gkTransMode
  if	kSwitch==1	then		;IF I-RATE VARIABLE CHANGE TRIGGER IS '1'...
  	reinit	START			;BEGIN A REINITIALISATION PASS FROM LABEL 'START'
  endif
  START:

  kPmdRnd	unirand	gkpmd
  
  if gkPhsMode==1 then
   kptr		portk	gkphs+kPmdRnd, kporttime	; PORTAMENTO IS APPLIED TO SMOOTH VALUE CHANGES VIA THE FLTK SLIDERS
   kptr		mirror	kptr,0,1
   kptr		=	kptr * (nsamp(1)/ftlen(1))
   aptr		interp	kptr				; A NEW A-RATE VARIABLE (aptr) IS CREATED BASE ON kptr
  else
   if gkshape==1 then
    kptr		phasor	(gkspd * sr * (1-gkfreeze))/(nsamp(1) * gkrange)
   elseif gkshape==2 then
    kptr		oscili	1,(gkspd * sr * (1-gkfreeze))/(nsamp(1) * gkrange),giTriangle
   elseif gkshape==3 then
    kptr		oscili	0.5,(gkspd * sr * (1-gkfreeze))/(nsamp(1) * gkrange)
    kptr		+=		0.5
   endif
   kptr	=	kptr * (nsamp(1)/ftlen(1)) * gkrange
   kptr	+=	(gkphs+kPmdRnd) * (nsamp(1)/ftlen(1))
   kptr	mirror	kptr,0,nsamp(1)/ftlen(1)
  endif
  aptr		interp	kptr
  
  iNumOverLaps	=	2000
  itotdur		=	3600
  
  kPchRnd	bexprnd	gkfmd					; random pitch
  kpch		=	iFrqRatio * octave(kPchRnd)
  gklevel	*=	iamp
  
  kRndTrig	init	1
  kDensRnd	bexprnd	gkDensRnd
  kdens	=	gkdens * octave(kDensRnd)
  kRndTrig	metro	kdens

  /* amplitude random modulation */
  kAmpRnd	random	0,gkAmpRnd
  klevel	=		gklevel-sqrt(kAmpRnd)

  /* LFO */
  kDensLFO	poscil	gkDensLFODep,gkLFORte
  kdens	=		gkdens * octave(kDensLFO)
  kAmpLFO	poscil	gkAmpLFODep*0.5,gkLFORte
  klevel	*=		1-((kAmpLFO+(abs(gkAmpLFODep)*0.5))^2)
    
  if gichans==1 then						; if mono...
  a1	fog	klevel, kdens, kpch, aptr, gkOctDiv, gkband, gkris, gkdur, gkdec, iNumOverLaps, 1, giattdec, itotdur, 0, i(gkTransMode)-1, 1
   if gkDualOnOff==1 then
    a1b	fog	klevel, kdens*gkDensRatio, kpch*octave(gkTransDiff), aptr+(gkPtrDiff*nsamp(1)/ftlen(1)), gkOctDiv, gkband, gkris, gkdur, gkdec, iNumOverLaps, 1, giattdec, itotdur, 0, i(gkTransMode)-1, 1
    if gkDelay>0 then
     a1b	vdelay	a1b,(gkDelay*1000)/gkdens,1000
    endif
    a1	+=	a1b
   endif
 	outs	a1*aenv,a1*aenv				; send mono audio to both outputs 
  elseif gichans==2 then						; otherwise, if stereo...
   a1	fog	klevel, kdens, kpch, aptr, gkOctDiv, gkband, gkris, gkdur, gkdec, iNumOverLaps, 1, giattdec, itotdur, 0, i(gkTransMode)-1, 1
   a2	fog	klevel, kdens, kpch, aptr, gkOctDiv, gkband, gkris, gkdur, gkdec, iNumOverLaps, 2, giattdec, itotdur, 0, i(gkTransMode)-1, 1
   if gkDualOnOff==1 then
    a1b	fog	klevel, kdens*gkDensRatio, kpch*octave(gkTransDiff), aptr+(gkPtrDiff*nsamp(1)/ftlen(1)), gkOctDiv, gkband, gkris, gkdur, gkdec, iNumOverLaps, 1, giattdec, itotdur, 0, i(gkTransMode)-1, 1
    a2b	fog	klevel, kdens*gkDensRatio, kpch*octave(gkTransDiff), aptr+(gkPtrDiff*nsamp(1)/ftlen(1)), gkOctDiv, gkband, gkris, gkdur, gkdec, iNumOverLaps, 2, giattdec, itotdur, 0, i(gkTransMode)-1, 1
    if gkDelay>0 then
     a1b	vdelay	a1b,(gkDelay*1000)/gkdens,1000
     a2b	vdelay	a2b,(gkDelay*1000)/gkdens,1000
    endif
    a1	+=	a1b
    a2	+=	a2b
   endif
 	outs	a1*aenv,a2*aenv				; send stereo signal to outputs
  endif
  rireturn


 endif

endin

</CsInstruments>  

<CsScore>
i 1 0 [60*60*24*7]
</CsScore>

</CsoundSynthesizer>
