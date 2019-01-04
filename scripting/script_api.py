#!/usr/bin/python
#_*_coding:utf-8_*_
import os
from manager.common import *

def write_script(script_dir,script_name,upload_files):

    check_and_mkdir(script_dir)
    with open("%s/%s" % (script_dir, script_name), "w") as f:
        for i in upload_files:
            f.write("%s" % i.encode("utf-8"))
    os.system("dos2unix %s/%s" % (script_dir, script_name))
    os.system("chmod +x %s/%s" % (script_dir, script_name))

    with open("%s/%s" % (script_dir, script_name), "r") as f:
        script_content = f.read()

    return script_content