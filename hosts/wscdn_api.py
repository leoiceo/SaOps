#!/usr/bin/python
#_*_coding:utf-8_*_
# code.by leoiceo


import sys,hashlib,os,urllib2

def get_passwd(username,apikey,data):
    try:
        m = hashlib.md5()
        m.update("%s%s%s"%(username,apikey,data))
        m.digest()
        md5pass = m.hexdigest()
        return md5pass
    except Exception,e:
        print "Error,getpass fail,%s" %e
        sys.exit()


def post(url, data):
    req = urllib2.Request(url)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    response = opener.open(req, data)
    result_info = response.read().strip()

    return result_info



def cdn_update_api(data,project):
    if project ==  "xxxxxx":
        username = "xxxxxxxxxxx"
        apikey = "xxxxxxxxxxxxx"
    else:
        return False

    prefix = "http://ccm.chinanetcenter.com/ccm/servlet/contReceiver"
    #print data
    md5pass = get_passwd(username,apikey,data)
    cdndata = "username=%s&passwd=%s&url=%s" % (username, md5pass, data)
    #print cdndata
    result = post(prefix, cdndata)
    #print result
    return result

if __name__ == "__main__":
    pass