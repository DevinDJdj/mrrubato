import os
import re

st = []
et = []

def getSecsFromTime(time):
    minsec = time.split(":")
    if (minsec == time):
        return 0
    print(int(minsec[0])*60 + int(minsec[1]))
    return int(minsec[0])*60 + int(minsec[1])


def getIterations(desc):
    st.clear()
    et.clear()
    s = 0

    try: 
        for i in range(1, 20):
            s = -1
            e = -1
            fnd = "TRIAL#" + str(i)
            ts = desc.index(fnd)
            te = desc.index(")", ts)
            if ts > -1:
                s = getSecsFromTime(desc[ts+(len(fnd))+2:te])
                
            fnd = "END#" + str(i)
            ts = desc.index(fnd)
            te = desc.index(")", ts)
            if ts > -1:
                e = getSecsFromTime(desc[ts+(len(fnd))+2:te])
            if s > 0 and e > 0 and e > s:
                st.append(s)
                et.append(e)
    except:
        s = -1


def getTranscriptFile(desc):
    url = ""
    tposition = desc.find("TRANSCRIPT:")
    if tposition > -1:
        eposition = desc.find('\n', tposition)
        if eposition > -1:
            url = desc[tposition+11:eposition]
        else:
            url = desc[tposition+11:]
    return url

def getMediaFile(desc):
    url = ""
    tposition = desc.find("MEDIAFILE:")
    if tposition > -1:
        eposition = desc.find('\n', tposition)
        if eposition > -1:
            url = desc[tposition+10:eposition]
        else:
            url = desc[tposition+10:]
    return url

def makeTimeLinks(desc, vid):
    desc = desc.replace("\n", "<br>")
    # desc = desc.replace(")", ")<br>")

    regex1 = r"\(([^)]+)\)"
    regex2 = r"\d+:\d\d?"

    matches = re.findall(regex2, desc)

    for match in matches:
        secs = getSecsFromTime(match)
        if secs > 0:
            #this will be mixed up if comments at the same time for two different videos.  Do we care?
            repl = "youtu.be/watch?v=" + vid + "&t=" + str(secs) + "s"
            desc = re.sub(match, repl, desc)

    return desc

def getVidFromMetadata(metadata):
    vid = os.path.splitext(os.path.basename(metadata))[0]
    return vid
