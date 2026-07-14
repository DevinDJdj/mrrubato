
from watchfiles import watch
import os

#recursively get all files.  
files = [ f.path for f in os.scandir('c:/devinpiano/transcripts/genbook') if f.is_file() ]
subfolders = [ f.name for f in os.scandir('c:/devinpiano/transcripts/genbook') if f.is_dir() ]

filemap = {}
for f in files:
    filemap[f] = {"modified": os.path.getmtime(f), "size": os.path.getsize(f)}

#sample just base dir and subfolders, but could be recursive if needed.
for subfolder in subfolders:
    subfiles = [ f.path for f in os.scandir('c:/devinpiano/transcripts/genbook/' + subfolder) if f.is_file() ]
    for f in subfiles:
        filemap[subfolder + '/' + os.path.basename(f)] = {"modified": os.path.getmtime(f), "size": os.path.getsize(f)}

for changes in watch('c:/devinpiano/transcripts/genbook'):
    for change_type, file_path in changes:
        if change_type.name == 'modified':
            prevsize = filemap[file_path]["size"] if file_path in filemap else 0
            currsize = os.path.getsize(file_path)

            with open(file_path, 'r') as f:
                f.seek(prevsize)
                content = f.read()
                print(f"New content from {file_path}:\n{content}")
                filemap[file_path]["size"] = currsize
                