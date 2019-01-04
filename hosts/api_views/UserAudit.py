from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import StreamingHttpResponse
from django.shortcuts import render,HttpResponseRedirect,render_to_response,HttpResponse
import json
from cmdb import settings
from hosts.models import *

def ssh_audit(request):

    if request.META.has_key('HTTP_X_FORWARDED_FOR'):
        ip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        ip = request.META['REMOTE_ADDR']

    if request.method == 'POST':
        received_json_data = json.loads(request.body)

    try:
        check_ip = host.objects.get(p_ip=ip)
        project_id = Project.objects.get(name=check_ip.project)
        new_log = SshAuditLog(project=project_id,p_ip=ip,username=received_json_data["username"],
                              login_ip=received_json_data["login_ip"],
                              log_time=received_json_data["log_time"],
                              cmd_log=received_json_data["cmd_log"])
        new_log.save()
        log = {"log":"ok"}
        return HttpResponse(json.dumps(log),content_type='text/html')

    except Exception,e:
        log = {"error":"This ipaddr not in myops","log":"%s"%e}

        return HttpResponse(json.dumps(log),content_type='text/html')

def get_ssl(request):
    #Ssl key download
    '''def readFile(fn, buf_size=262144):
        f = open(fn, "rb")
        while True:
            c = f.read(buf_size)
            if c:
                yield c
            else:
                break
        f.close()

    file_name = "%s/static/ops/ssl/client.p12" % settings.BASE_DIR
    response = HttpResponse(readFile(file_name))
    '''
    def file_iterator(file_name, chunk_size=512):
        with open(file_name) as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break

    the_file_name = "%s/static/ops/ssl/client.p12" % settings.BASE_DIR
    filename="client.p12"
    response = StreamingHttpResponse(file_iterator(the_file_name))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(filename)

    return response
