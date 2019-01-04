#!/usr/bin/python
#_*_coding:utf-8_*_
# code.by leoiceo


import sys,hashlib,os,urllib2

def get_passwd(data):
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

if __name__ == "__main__":
    data = sys.argv[1]
    username="xxxxxx"
    apikey="xxxxxx"
    prefix = "http://ccm.chinanetcenter.com/ccm/servlet/contReceiver"
    md5pass = get_passwd(data)
    cdndata = "username=%s&passwd=%s&url=%s" % (username, md5pass, data)

    last_result = post(prefix, cdndata)
    print last_result