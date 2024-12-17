from atlassian import Confluence
import json
import requests
import subprocess
import config
from oauth2client.tools import argparser, run_flow
import os
import glob
from pathlib import Path   

#pip install sumy
from sumy.parsers.plaintext import PlaintextParser
#from sumy.nlp.tokenizers import Tokenizer
#from sumy.summarizers.lsa import LsaSummarizer

#pip install atlassian-python-api
#search of all mp4 on staging wiki.  
#https://wikistage.company.com/dosearchsite.action?cql=siteSearch%20~%20%22mp4%22%20AND%20type%20in%20(%22attachment%22)&includeArchivedSpaces=false

#this works so perhaps we can just use this 
#curl -u dj:xxxxx https://wikistage.company.com//confluence/rest/api/content?limit=2




#download all mp4


def getConfluenceContent(title):
  contentoverall="""
<ac:structured-macro ac:name=\"section\">
 <ac:rich-text-body>
 <ac:structured-macro ac:name=\"column\">
 <ac:parameter ac:name=\"width\">60%</ac:parameter>
 <ac:rich-text-body>
  <ac:structured-macro ac:name=\"recently-updated\">
  <ac:parameter ac:name=\"theme\">concise</ac:parameter>
  <ac:parameter ac:name=\"labels\">"""
  contentoverall += title
  contentoverall += """	
  </ac:parameter>
  </ac:structured-macro>
 </ac:rich-text-body>
 </ac:structured-macro>
 <ac:structured-macro ac:name=\"column\">
 <ac:parameter ac:name=\"width\">2%</ac:parameter>
</ac:structured-macro>
 <ac:structured-macro ac:name=\"column\">
 <ac:parameter ac:name=\"width\">38%</ac:parameter>
 <ac:rich-text-body>
  <ac:structured-macro ac:name=\"pagetreesearch\">
  </ac:structured-macro>
  <ac:structured-macro ac:name=\"pagetree\">
   <ac:parameter ac:name=\"root\">
    <ac:link>
     <ri:page ri:content-title=\"@self\"/>
    </ac:link>
   </ac:parameter>
   <ac:parameter ac:name=\"startDepth\">2</ac:parameter>
  </ac:structured-macro>
 </ac:rich-text-body>
 </ac:structured-macro>
 </ac:rich-text-body>
</ac:structured-macro>

<ac:structured-macro ac:name=\"include\">
 <ac:parameter ac:name=\"\">
  <ac:link>
   <ri:page ri:content-title=\"TCSKB FAQ\" ri:space-key=\"AYUD\"/>
  </ac:link>
 </ac:parameter>
</ac:structured-macro>
    """
  return contentoverall


def getTranscript(args, uploadlinks, summary):
  transcript = ""
  with open(args.transcript, "r+") as file1:
    transcript = file1.read()
  for idx, l in enumerate(uploadlinks):
    transcript = transcript.replace("-OCR" + str(idx) + "-", "<ac:image ac:height=\"250\">    <ri:attachment ri:filename=\"" + l + "\"></ri:attachment>  </ac:image>")
  transcript = transcript.replace("\n", "<br/>")
  transcript = transcript.replace("<br/><br/>", "<br/>")
  transcript = transcript.replace("<br/><br/>", "<br/>")
  link = 'https://localhost/rec.html?cat=' + args.category + '&amp;id=' + args.title + '&amp;ver=' + args.version
  print(link)
  link = '<a href=\"' + link + '\">FULL VIDEO</a>'
  return summary + '<br/>' + link + '<br/>' + transcript + '<br/>' + summary + '<br/>' + link
  return transcript + '<br/>' + link
#  return transcript

def getSummary(args):
  transcript = ""
  with open(args.transcript, "r+") as file1:
    transcript = file1.read()
  parser = PlaintextParser.from_string(transcript, Tokenizer("english"))
  # Create an LSA summarizer
  summarizer = LsaSummarizer()
  # Generate the summary
  ret = ""
  summary = summarizer(parser.document, sentences_count=3)  # You can adjust the number of sentences in the summary
  for sentence in summary:
    ret += str(sentence) + '<br/>'
  return ret

def getMyContent(args, parent, sections):
  fn = os.path.basename(args.file)
  fntranscript = os.path.basename(args.transcript)
  fnocrtranscript = os.path.basename(args.ocrtranscript)
  #skip this part for now.  
  print("Uploading to confluence" + fn)
  print(parent['id'])

  #here attach video and or other.  Need to store in another repository, confluence too slow.  
#  confluence.attach_file(args.file, name=fn, content_type=None, page_id=parent['id'], title=fn, space=None, comment=None)
  #this is timing out because of Confluence setting I believe.  
  #disable this? https://httpd.apache.org/docs/2.4/mod/mod_reqtimeout.html
  print("Uploaded to confluence" + fn)

  imagefolder = config.cfg["imagefolder"]
  search = title + '_' + version + '_*'
  files=glob.glob(imagefolder + search)
  uploadlinks = []
  for f in files:
#    status = confluence.attach_file(f, name=Path(f).name, content_type=None, page_id=parent['id'], title=fn, space=None, comment=None)  
#    print(status)
    uploadlinks.append(Path(f).name)
  print(uploadlinks)
  sum = ""
#  sum = getSummary(args)
  t = getTranscript(args, uploadlinks, sum)
  print(t)
  me = confluence.update_or_create(parent["id"], version + '_' + title, t, representation='storage', full_width=False)
  confluence.set_page_label(me["id"], "OCR")
  confluence.set_page_label(me["id"], "SUM")
  for s in sections:
    confluence.set_page_label(me["id"], s)
  
  for f in files:
    status = confluence.attach_file(f, name=Path(f).name, content_type=None, page_id=me['id'], title=f, space=None, comment=None)  

  confluence.attach_file(args.transcript, name=fntranscript, content_type=None, page_id=me['id'], title=fntranscript, space=None, comment=None)
  print("uploaded transcript" + fntranscript)
  confluence.attach_file(args.ocrtranscript, name=fnocrtranscript, content_type=None, page_id=me['id'], title=fnocrtranscript, space=None, comment=None)
  print("uploaded OCR transcript" + fnocrtranscript)





#  print(status)
  

if __name__ == '__main__':
  #if not set, utilize latest file in Home/Videos/
  argparser.add_argument("--file", required=True, help="Video file to upload")
  argparser.add_argument("--transcript", required=True, help="Transcript file")
  argparser.add_argument("--ocrtranscript", required=True, help="OCR Transcript file")
  argparser.add_argument("--pat", required=True, help="Personal Access Token")
  argparser.add_argument("--category", required=True, help="Category for Confl page")
  argparser.add_argument("--title", required=False, help="Video file to upload", default="Test")
  argparser.add_argument("--version", required=False, help="Video file to upload", default="00000000000000")


  args = argparser.parse_args()

  if not os.path.exists(args.file):
    exit("Please specify a valid file using the --file= parameter.")
  
#  myuser = config.cfg["confluence"]["uid"]
#  mypass = config.cfg["confluence"]["pwd"]
#  confluence = Confluence(
#      url='https://wikistage.company.com',
#      username=myuser,
#      password=mypass)

  pat = config.cfg["confluence"]["pat"]
  pat = args.pat
  confluence = Confluence(url=config.cfg["confluence"]["url"], 
                          token=pat)

  space = config.cfg["confluence"]["space"]
  args.category += "_" + args.title
  title = args.title
  version = args.version
  cat = args.category
  sections = cat.split('_')
  parent = None

  toppage = confluence.get_page_by_title(space, config.cfg["confluence"]["toppage"], start=None, limit=None)
  parent = toppage
  for s in sections:
    mypage = confluence.get_page_by_title(space, s, start=None, limit=None)
    #if this page exists, then just add attachment.  

    if mypage and 'id' in mypage:
      parent = mypage
    else:  
    #ok we can use this.  
      status = confluence.create_page(
        space=space,
        title=s,
        body=getConfluenceContent(s),
        parent_id=parent["id"])
#        body='<ac:link><ri:user ri:username="dj"/></ac:link>This is the body. You can use <strong>HTML tags</strong>!')
      parent = status
    #no error checking for existing page names etc.  
    #so if we fail in naming, we have issues.  
      
      
  getMyContent(args, parent, sections)
