; RandomNumberGenerators.csd
; Written by Iain McCurdy 2015
; 
; It will be noticed that rspline can output values beyond the maximum allowed amplitude limits (-1 and 1)

<Cabbage>
form caption("Random Number Generators"), size(920, 280), pluginid("RaFu"), guirefresh(32)

image     bounds(  5,  0,910,200), colour(0,0,0,0), plant("Table") {
gentable  bounds(  0,  0,910,150), identchannel("table1"), tablenumber(1), tablecolour:1(100,0,0), alpha(1), amprange(-1,1,1), zoom(-1), tablebackgroundcolour(50,50,50), tablegridcolour(100,100,100)
image     bounds(  0,  0,  1,150), identchannel("wiper")
nslider bounds(  0,155,90,30), text("Rate of Updates"), channel("ROU"), range(1,256,64,1,1)
nslider bounds( 95,155,90,30), text("Maximum so far"), channel("Max"), range(-10,10,0,1,0.001)
nslider bounds(190,155,90,30), text("Minimum so far"), channel("Min"), range(-10,10,0,1,0.001)
button    bounds(285,170,60,17), text("RESET","RESET"), channel("Reset"), latched(0)

checkbox  bounds(355,170,60,15), text("Sound"), channel("SoundOnOff"), colour("yellow")
rslider   bounds(415,165,25,25), channel("SoundAmp"), range(0,1,0.3,0.5,0.001)

image     bounds(450,154,130,39), colour(0,0,0,0), outlinethickness(1), outlinecolour(200,200,200), shape("sharp")
label     bounds(455,158,80,12), text("FILTER")
combobox  bounds(455,170,80,20), text("none","port","lineto"), channel("Filter")
label     bounds(545,156,25,11), text("Time"), align("centre")
rslider   bounds(545,165,25,25), channel("Time"), range(0,1,0.1,0.5,0.001)

}

label     bounds( 10,208,80,12), text("OPCODE")
combobox  bounds( 10,220,80,20), text("randomi","randomh","rspline","jspline","jitter","jitter2","vibr","vibrato","gaussi"), channel("Type")

image     bounds( 95,210,300, 60), colour(0,0,0,0), plant("randomi"), identchannel("randomiPlant") {
nslider bounds(  0,  0,90,30), text("Amp.1"),         channel("randomiAmp1"),    range(-1,1,-1,1,0.001)
nslider bounds( 90,  0,90,30), text("Amp.2"),         channel("randomiAmp2"),    range(-1,1,1,1,0.001)
nslider bounds(180,  0,90,30), text("Freq"),          channel("randomiFreq"),    range(0.001,16,1,1,0.001)
}
image     bounds( 95,210,600, 60), colour(0,0,0,0), plant("randomh"), identchannel("randomhPlant") {
nslider bounds(  0,  0,90,30), text("Amp.1"),         channel("randomhAmp1"),    range(-1,1,-1,1,0.001)
nslider bounds( 90,  0,90,30), text("Amp.2"),         channel("randomhAmp2"),    range(-1,1,1,1,0.001)
nslider bounds(180,  0,90,30), text("Freq"),          channel("randomhFreq"),    range(0.001,16,1,1,0.001)
}
image     bounds( 95,210,600, 60), colour(0,0,0,0), plant("rspline"), identchannel("rsplinePlant") {
nslider bounds(  0,  0,90,30), text("Amp.1"),           channel("rsplineAmp1"),     range(-1,1,-1,1,0.001)
nslider bounds( 90,  0,90,30), text("Amp.2"),           channel("rsplineAmp2"),     range(-1,1,1,1,0.001)
nslider bounds(180,  0,90,30), text("Freq.1"),          channel("rsplineFreq1"),    range(0.001,16,1,1,0.001)
nslider bounds(270,  0,90,30), text("Freq.2"),          channel("rsplineFreq2"),    range(0.001,16,1,1,0.001)
}
image     bounds( 95,210,600, 60), colour(0,0,0,0), plant("jspline"), identchannel("jsplinePlant") {
nslider bounds(  0,  0,90,30), text("Amp"),             channel("jsplineAmp"),     range(-1,1,1,1,0.001)
nslider bounds( 90,  0,90,30), text("Freq.1"),          channel("jsplineFreq1"),    range(0.001,16,1,1,0.001)
nslider bounds(180,  0,90,30), text("Freq.2"),          channel("jsplineFreq2"),    range(0.001,16,1,1,0.001)
}
image     bounds( 95,210,600, 60), colour(0,0,0,0), plant("jitter"), identchannel("jitterPlant") {
nslider bounds(  0,  0,90,30), text("Amp"),             channel("jitterAmp"),      range(-1,1,1,1,0.001)
nslider bounds( 90,  0,90,30), text("Freq.1"),          channel("jitterFreq1"),    range(0.001,16,1,1,0.001)
nslider bounds(180,  0,90,30), text("Freq.2"),          channel("jitterFreq2"),    range(0.001,16,1,1,0.001)
}
image     bounds( 95,210,700, 60), colour(0,0,0,0), plant("jitter2"), identchannel("jitter2Plant") {
nslider bounds(  0,  0,90,30), text("Total Amp."),      channel("jitter2TotAmp"),  range(-1,1,1,1,0.001)
nslider bounds( 90,  0,90,30), text("Amp.1"),           channel("jitter2Amp1"),    range(-1,1,1,1,0.001)
nslider bounds(180,  0,90,30), text("Freq.1"),          channel("jitter2Freq1"),   range(0.001,16,1,1,0.001)
nslider bounds(270,  0,90,30), text("Amp.2"),           channel("jitter2Amp2"),    range(-1,1,1,1,0.001)
nslider bounds(360,  0,90,30), text("Freq.2"),          channel("jitter2Freq2"),   range(0.001,16,1,1,0.001)
nslider bounds(450,  0,90,30), text("Amp.3"),           channel("jitter2Amp3"),    range(-1,1,1,1,0.001)
nslider bounds(540,  0,90,30), text("Freq.3"),          channel("jitter2Freq3"),   range(0.001,16,1,1,0.001)
}
image     bounds( 95,210,700, 60), colour(0,0,0,0), plant("vibr"), identchannel("vibrPlant") {
nslider bounds(  0,  0,90,30), text("Av.Amp"),        channel("vibrAvAmp"),        range(-1,1,.3,1,0.001)
nslider bounds( 90,  0,90,30), text("Av.Freq"),       channel("vibrAvFreq"),       range(0.1,16,1,1,0.001)
combobox  bounds(180, 14,70,17), text("sine","triangle","square","exp","gauss.1","gauss.2","Bi-gauss"), channel("WaveShape")
}
image     bounds( 95,210,800, 60), colour(0,0,0,0), plant("vibrato"), identchannel("vibratoPlant") {
nslider bounds(  0,  0,90,30), text("Av.Amp"),        channel("vibratoAvAmp"),          range(-1,1,.3,1,0.001)
nslider bounds( 90,  0,90,30), text("Av.Freq"),       channel("vibratoAvFreq"),         range(0.1,16,1,1,0.001)
nslider bounds(180,  0,90,30), text("Rand.Dev.Amp."), channel("vibratoRandAmountAmp"),  range(0,1,1,1,0.001)
nslider bounds(270,  0,90,30), text("Rand.Dev.Frq."), channel("vibratoRandAmountFreq"), range(0.001,16,1,1,0.001)
nslider bounds(360,  0,90,30), text("Amp.Min.Rate"),  channel("vibratoAmpMinRate"),     range(0.001,16,1,1,0.001)
nslider bounds(450,  0,90,30), text("Amp.Max.Rate"),  channel("vibratoAmpMaxRate"),     range(0.001,16,1,1,0.001)
nslider bounds(540,  0,90,30), text("Frq.Min.Rate"),  channel("vibratoCpsMinRate"),     range(0.001,16,1,1,0.001)
nslider bounds(630,  0,90,30), text("Frq.Max.Rate"),  channel("vibratoCpsMaxRate"),     range(0.001,16,1,1,0.001)
combobox  bounds(720, 14,70,17), text("sine","triangle","square","exp","gauss.1","gauss.2","Bi-gauss"), channel("WaveShape")
}
image     bounds( 95,210,800, 60), colour(0,0,0,0), plant("gaussi"), identchannel("gaussiPlant") {
nslider bounds(  0,  0,90,30), text("Amp."),        	channel("gaussiRange"),          range(0,1,.3,1,0.001)
nslider bounds( 90,  0,90,30), text("Range"),       	channel("gaussiAmp"),         range(0,1,1,1,0.001)
nslider bounds(180,  0,90,30), text("Freq."), 		channel("gaussiCps"),  range(0,100,5,1,0.001)
}
</Cabbage>
                    
<CsoundSynthesizer>

<CsOptions>   
-dm0 -n -+rtmidi=NULL -M0
</CsOptions>

<CsInstruments>

sr 		= 	44100	; SAMPLE RATE
ksmps 		= 	32	; NUMBER OF AUDIO SAMPLES IN EACH CONTROL CYCLE
nchnls 		= 	2	; NUMBER OF CHANNELS (1=MONO)
0dbfs		=	1	; MAXIMUM AMPLITUDE

giTableWidth	=	910				; width of the table (in pixels)
giTableOffset	=	5				; table offset (in pixels)
giFunc		ftgen	1,0,2048,-10,0				; storage for the streams of random data
giSine		ftgen	2,0,2048,10,1				; sine wave
giTri		ftgen	3,0,2048,7,0,512,1,1024,-1,512,0	; triangular wave
giSqu		ftgen	4,0,2048,7,1,1024,1,0,-1,1024,-1	; square wave
giExp		ftgen	5,0,2048,19,0.5,0.5,270,0.5		; exponential curve
giGauss1	ftgen	6,0,2048,20,6,1,1			; gaussian window shape
giGauss2	ftgen	7,0,2048,20,6,1,0.25			; gaussian window shape (sharper)
giBiGauss	ftgen	8,0,2048,10,1
iCount		=		0
while iCount<ftlen(giBiGauss) do
 iVal		table	iCount, giBiGauss
 			tablew	iVal^16 * (iVal<0?-1:1), iCount, giBiGauss
 iCount		+=		1
od

instr	1
 kROU			chnget	"ROU"			; rate of updates
 kType			chnget	"Type"			; random opcode choice
 kReset			chnget	"Reset"
 krandomiAmp1		chnget	"randomiAmp1"		; randomi
 krandomiAmp2		chnget	"randomiAmp2"
 krandomiFreq		chnget	"randomiFreq"
 krandomhAmp1		chnget	"randomhAmp1"		; randomh
 krandomhAmp2		chnget	"randomhAmp2"
 krandomhFreq		chnget	"randomhFreq"
 krsplineAmp1		chnget	"rsplineAmp1"		; rspline
 krsplineAmp2		chnget	"rsplineAmp2"
 krsplineFreq1		chnget	"rsplineFreq1"
 krsplineFreq2		chnget	"rsplineFreq2"
 kjsplineAmp		chnget	"jsplineAmp"		; jspline
 kjsplineFreq1		chnget	"jsplineFreq1"
 kjsplineFreq2		chnget	"jsplineFreq2"
 kjitterAmp		chnget	"jitterAmp"		; jitter
 kjitterFreq1		chnget	"jitterFreq1"
 kjitterFreq2		chnget	"jitterFreq2"
 kjitter2TotAmp		chnget	"jitter2TotAmp"		; jitter2
 kjitter2Amp1		chnget	"jitter2Amp1"
 kjitter2Freq1		chnget	"jitter2Freq1"
 kjitter2Amp2		chnget	"jitter2Amp2"
 kjitter2Freq2		chnget	"jitter2Freq2"
 kjitter2Amp3		chnget	"jitter2Amp3"
 kjitter2Freq3		chnget	"jitter2Freq3"
 kvibrAvAmp		chnget	"vibrAvAmp"		; vibr
 kvibrAvFreq		chnget	"vibrAvFreq"
 kWaveShape		chnget	"WaveShape"
 kvibratoAvAmp		chnget	"vibratoAvAmp"		; vibrato
 kvibratoAvFreq		chnget	"vibratoAvFreq"
 kvibratoRandAmountAmp	chnget	"vibratoRandAmountAmp"
 kvibratoRandAmountFreq	chnget	"vibratoRandAmountFreq"
 kvibratoAmpMinRate	chnget	"vibratoAmpMinRate"
 kvibratoAmpMaxRate	chnget	"vibratoAmpMaxRate"
 kvibratoCpsMinRate	chnget	"vibratoCpsMinRate"
 kvibratoCpsMaxRate	chnget	"vibratoCpsMaxRate"
 kgaussiRange		chnget	"gaussiRange"
 kgaussiAmp			chnget	"gaussiAmp"
 kgaussiCps			chnget	"gaussiCps"
    
 kFilter		chnget	"Filter"
 kFilterTime		chnget	"Time"
 
 kMax	init	0			; maximum so far
 kMin	init	0			; minimum so far
 
 if changed(kReset)==1 then
  kMax	=	0
  kMin	=	0
  chnset	kMax,"Max"
  chnset	kMin,"Min"
 endif
  
 if changed(kType)==1 then			; if opcode type is changed reset maximum and minimum to zero
  kMax	=	0
  kMin	=	0
  chnset	kMax,"Max"			; send zeros to widgets
  chnset	kMin,"Min"
  chnset	"visible(0)","randomiPlant"	; first hide all opcode parameter widgets...
  chnset	"visible(0)","randomhPlant"
  chnset	"visible(0)","rsplinePlant"
  chnset	"visible(0)","jsplinePlant"
  chnset	"visible(0)","jitterPlant"
  chnset	"visible(0)","jitter2Plant"
  chnset	"visible(0)","vibrPlant"
  chnset	"visible(0)","vibratoPlant"
  chnset	"visible(0)","gaussiPlant"
  if(kType==1) then				; .. then reveal the appropriate plant
   chnset	"visible(1)","randomiPlant"
  elseif(kType==2) then
   chnset	"visible(1)","randomhPlant"
  elseif(kType==3) then
   chnset	"visible(1)","rsplinePlant"
  elseif(kType==4) then
   chnset	"visible(1)","jsplinePlant"
  elseif(kType==5) then
   chnset	"visible(1)","jitterPlant"
  elseif(kType==6) then
   chnset	"visible(1)","jitter2Plant"
  elseif(kType==7) then
   chnset	"visible(1)","vibrPlant"
  elseif(kType==8) then
   chnset	"visible(1)","vibratoPlant"
  elseif(kType==9) then
   chnset	"visible(1)","gaussiPlant"
  endif
 endif

 iLen	=	ftlen(giFunc)			; length of function table
 kNdx	init	0				; table write index initilialised to the start of the table

 if changed(kWaveShape)==1 then			; reinit if waveshape combobox has been changed
  reinit UPDATE
 endif
 UPDATE:

 if kType==1 then			; randomi
  kRnd	randomi	krandomiAmp1, krandomiAmp2, krandomiFreq, 2
 elseif kType==2 then			; randomh
  kRnd	randomh	krandomhAmp1, krandomhAmp2, krandomhFreq, 2
 elseif kType==3 then			; rspline
  kRnd	rspline	krsplineAmp1, krsplineAmp2, krsplineFreq1, krsplineFreq2
 elseif kType==4 then			; rspline
  kRnd	jspline	kjsplineAmp, kjsplineFreq1, kjsplineFreq2
 elseif kType==5 then			; jitter 
  kRnd	jitter	kjitterAmp, kjitterFreq1, kjitterFreq2
 elseif kType==6 then			; jitter2 
  kRnd	jitter2	kjitter2TotAmp, kjitter2Amp1, kjitter2Freq1, kjitter2Amp2, kjitter2Freq2, kjitter2Amp3, kjitter2Freq3
 elseif kType==7 then			; vibr
  kRnd	vibr	kvibrAvAmp, kvibrAvFreq, i(kWaveShape) + giSine - 1
 elseif kType==8 then			; vibrato
  kRnd	vibrato	kvibratoAvAmp, kvibratoAvFreq, kvibratoRandAmountAmp, kvibratoRandAmountFreq, kvibratoAmpMinRate, kvibratoAmpMaxRate, kvibratoCpsMinRate, kvibratoCpsMaxRate, i(kWaveShape) + giSine - 1
 elseif kType==9 then			; gaussi
  kRnd	gaussi	kgaussiRange, kgaussiAmp, kgaussiCps
 endif
 rireturn
 
 if kFilter==2 then
  kRnd	portk	kRnd, kFilterTime
 elseif kFilter==3 then
  kRnd	lineto	kRnd, kFilterTime
 endif  
 
 
 if metro(kROU)==1 then							; limit updates (both to the table and to the GUI) using a metronome
  	tablew	kRnd,kNdx,giFunc					; write random value to table
  kNdx	wrap	kNdx+1,0,iLen						; increment index and wrap ot zero if it exceeds table length
  chnset	"tablenumber(1)","table1"				; update GUI gentable
  Smsg	sprintfk	"pos(%d,5)", ((kNdx/iLen) * giTableWidth)	; construct string message to update position of wiper
  	chnset		Smsg,"wiper"					; send message to 'wiper' widget
 endif

 kMax	=	kRnd>kMax?kRnd:kMax					; update 'Maximum So Far' value if required
 kMin	=	kRnd<kMin?kRnd:kMin					; update 'Minimum So Far' value if required
 if changed(kMax)==1 then						; if 'Maximum So Far' has been changed...
  chnset	kMax,"Max"						; ...write to GUI nslider
 elseif changed(kMin)==1 then						; if 'Minimum So Far' has been changed...
  chnset	kMin,"Min"						; ...write to GUI nslider
 endif

 ; sonify
 kSoundOnOff	chnget	"SoundOnOff"					; Sound On/Off checkbox
 kSoundAmp	chnget	"SoundAmp"					; Sound Amplitude
 kSoundOnOff	lineto	kSoundOnOff*kSoundAmp,0.03			; smooth on/off button change. (Will be used to prevent clicks.)
 aSoundOnOff	interp	kSoundOnOff
 if kSoundOnOff>0 then							; if Sound On/Off button is on...
  asig	poscil	0.1*aSoundOnOff,cpsoct(8+kRnd)				; audio oscillator. Frequency modulated by random function.
  	outs	asig,asig						; send to audio outputs
 endif

endin

</CsInstruments>

<CsScore>
i 1 0 [3600*24*7]
</CsScore>

</CsoundSynthesizer>
