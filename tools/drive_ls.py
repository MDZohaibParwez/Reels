#!/usr/bin/env python3
"""List a public Google Drive folder tree without downloading (gdown --folder times out on big libraries).
python3 tools/drive_ls.py <folder_id>   -> id | name | mimetype, 3 levels deep. Then: gdown <id> -O name.mp4"""
import re, sys, subprocess, codecs
def ls(fid):
    t = subprocess.run(["curl","-sL",f"https://drive.google.com/drive/folders/{fid}"],capture_output=True,text=True).stdout
    i = t.find("window['_DRIVE_ivd'] = '")
    if i < 0: return []
    s = t[i+24: t.find("';", i+24)]
    s = codecs.decode(s.replace('\\/', '/'), 'unicode_escape')
    return re.findall(r'\["([A-Za-z0-9_-]{25,45})",\["'+re.escape(fid)+r'"\],"([^"]+)","([^"]+)"', s)
def walk(fid, pre="", depth=0):
    for i, n, m in ls(fid):
        print(f"{'  '*depth}{i} | {n} | {m}", flush=True)
        if m.endswith("folder") and depth < 2: walk(i, pre+n+"/", depth+1)
walk(sys.argv[1])
