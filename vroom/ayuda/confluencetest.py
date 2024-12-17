from atlassian import Confluence
import json
import requests
import subprocess
#search of all mp4 on staging wiki.  
#https://wikistage.company.com/dosearchsite.action?cql=siteSearch%20~%20%22mp4%22%20AND%20type%20in%20(%22attachment%22)&includeArchivedSpaces=false
#see if we can get this search to work with the api.  
# Get results from cql search result with all related fields
#confluence.cql(cql, start=0, limit=None, expand=None, include_archived_spaces=None, excerpt=None)

#this works so perhaps we can just use this 
#curl -u dj:xxxxx https://wikistage.company.com//confluence/rest/api/content?limit=2

#ok we have a start.  Now lets see if we can generate something from a video.  
#search for video content in the wiki.  
#edit the page based on 

# Get all page by label
#confluence.get_all_pages_by_label(label, start=0, limit=50)

# Get all pages from Space
# content_type can be 'page' or 'blogpost'. Defaults to 'page'
# expand is a comma separated list of properties to expand on the content.
# max limit is 100. For more you have to loop over start values.
#confluence.get_all_pages_from_space(space, start=0, limit=100, status=None, expand=None, content_type='page')
# Update page if already exist
#confluence.update_page(page_id, title, body, parent_id=None, type='page', representation='storage', minor_edit=False, full_width=False)

# The list of labels on a piece of Content
#confluence.get_page_labels(page_id, prefix=None, start=None, limit=None)
# Set a label on the page
#confluence.set_page_label(page_id, label)

# Delete Confluence page label
#confluence.remove_page_label(page_id, label)

# Update page or create page if it is not exists
#confluence.update_or_create(parent_id, title, body, representation='storage', full_width=False)

# Append body to page if already exist
#confluence.append_page(page_id, title, append_body, parent_id=None, type='page', representation='storage', minor_edit=False)
# Attach (upload) a file to a page, if it exists it will update the
# automatically version the new file and keep the old one
#confluence.attach_file(filename, name=None, content_type=None, page_id=None, title=None, space=None, comment=None)
# Get attachment for content
#confluence.get_attachments_from_content(page_id, start=0, limit=50, expand=None, filename=None, media_type=None)


mypass = input("Type password: ")
confluence = Confluence(
    url='https://wikistage.company.com',
    username='dj',
    password=mypass)

#ok we can use this.  
status = confluence.create_page(
    space='VROOM',
    title='This is the title',
    body='<ac:link><ri:user ri:username="dj"/></ac:link>This is the body. You can use <strong>HTML tags</strong>!')
    #body = '<ac:image><ri:attachment ri:filename="tb.png" /></ac:image>'


print(status)



#download all mp4


def downloadmp4(allmp4):
#    allmp4 = "siteSearch+~+\"mp4\""
    

    result = confluence.cql(allmp4, start=0, limit=None, expand=None, include_archived_spaces=None, excerpt=None)
    print(result)
    file = open('test_output.txt', 'w')
    file.write(json.dumps(result))
    file.close()

    for r in result["results"]:
        print(r["content"]["_links"]["webui"])
        pos = r["content"]["_links"]["webui"].find("pageId=")
        if pos > 0:
            parent = r["content"]["_links"]["webui"]
            parent = parent[pos+7:pos+16]
            print(parent)
            #perhaps copy from here to another test location?  
            apage = confluence.get_page_by_id(parent, expand=None, status=None, version=None)
            print(apage)

            attachments_container = confluence.get_attachments_from_content(page_id=parent, start=0, limit=500)
            print(json.dumps(attachments_container))
            attachments = attachments_container['results']
            for attachment in attachments:
                fname = attachment['title']
                print(fname)
                if (fname == r["content"]["title"]) and (fname.find("_s.mp4") == -1):
                    download_link = confluence.url + attachment['_links']['download']
                    r = requests.get(download_link, auth=(confluence.username, confluence.password))
                    if r.status_code == 200:
                        with open("output/" + fname, "wb") as f:
                            for bits in r.iter_content():
                                f.write(bits)    
                    #this should wait for completion.  
                    subprocess.call("python ./test.py --file=\"C:/projects/vroom/output/" + fname + "\" --function compress", shell=True)
                    #after completion, we should upload back to the same page.  
                    #and attach the text transcript.  Is this enough?  If we look at the time 
                    #cant delete at the moment, so probably lets leave this for now.  
                    #or limit search path.  
                    #https://wikistage.company.com/pages/viewpageattachments.action?pageId=128548922
                    #sorry.  
                    fn = fname.split('.')
                    #skip this part for now.  
#                    print("Uploading to confluence" + fn[0])
#                    confluence.attach_file("output/" + fn[0] + "_s.mp4", name=fn[0] + "_s.mp4", content_type=None, page_id=parent, title=fn[0] + "_s.mp4", space=None, comment=None)
#                    confluence.attach_file("output/" + fn[0] + ".txt", name=fn[0] + "_transcript.txt", content_type=None, page_id=parent, title=fn[0] + "_transcript.txt", space=None, comment=None)
#                    print("Uploaded to confluence" + fn[0])
                    #launch python ./test.py --file="C:/projects/vroom/IBM_AD_Demo_2017_05_03.mp4" --function compress
            break;


##It can have any extension supported by ffmpeg: .ogv, .mp4, .mpeg, .avi, .mov, .m4v
allmp4 = "siteSearch+~+\"file.extension:mp4\"+and+type+=+\"attachment\""
#downloadmp4(allmp4)
allmp4 = "siteSearch+~+\"file.extension:avi\"+and+type+=+\"attachment\""
#downloadmp4(allmp4)
allmp4 = "siteSearch+~+\"file.extension:mov\"+and+type+=+\"attachment\""
#downloadmp4(allmp4)
