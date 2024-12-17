#!C:\Python\Python311\python.exe

import cgi
import cgitb
import os
import subprocess
import datetime
import config
import json
import base64
import urllib.request

#need to change cgi to multipart
#https://www.agiliq.com/blog/2019/09/python-multipart/

cgitb.enable()
form = cgi.FieldStorage()
ret = {"retcode": "error"}
print("Content-type: text/html\n")
if "file" in form:
    file_item = form["file"]
    mycomments = form["mycomments"].value
    version = form["version"].value
    title = form["title"].value
    pat = form["pat"].value
    ocrtranscript = form["ocrtranscript"].value
    cat = form["cat"].value
    images = json.loads(form["images"].value)
    if file_item.filename:
        file_name = file_item.filename
        file_path = 'uploads/videos/' + file_name
        with open(file_path, 'wb') as file:
            file.write(file_item.file.read())
        tranfile = 'uploads/transcripts/' + title + '_' + version + '.txt'
        with open(tranfile, 'w') as file:
            file.write(mycomments)
        ocrtranfile = 'uploads/ocr/' + title + '_' + version + '_ocr.txt'
        with open(ocrtranfile, 'w') as file:
            file.write(ocrtranscript)

        if (len(images) > 0):
            for image in images:
                file_patha = 'uploads/images/'
                response = urllib.request.urlopen(image['img'])
                with open(file_patha + title + '_' + version + "_" + str(image['id']) + '.png', 'wb') as file:
                    file.write(response.file.read())
        #this should wait for completion.  
        cmd = "python ./confluenceupload.py --pat=\"" + pat + "\" --category=\"" + cat + "\" --file=\"" + file_path + "\" --transcript=\"" + tranfile + "\" --ocrtranscript=\"" + ocrtranfile + "\" --title=\"" + title + "\" --version=\"" + version + "\""
        retcode = subprocess.call("python ./confluenceupload.py --pat=\"" + pat + "\" --category=\"" + cat + "\" --file=\"" + file_path + "\" --transcript=\"" + tranfile + "\" --ocrtranscript=\"" + ocrtranfile + "\" --title=\"" + title + "\" --version=\"" + version + "\"", shell=True)
        upload_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ret = {"cmd": cmd, "fname": file_name, "version": version, "retcode": retcode, "uploadtime": upload_datetime}
        local_path = os.path.abspath(file_path)

#        print(f"<div class='file-info'> {images}</div>")

    else:
        ret = {"retcode": -1}
        
else:
	ret = {"retcode": -1}

print(json.dumps(ret))
