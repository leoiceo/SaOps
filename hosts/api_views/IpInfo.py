from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render,HttpResponseRedirect,render_to_response,HttpResponse
import json

def public_ipv4(request):
    if request.META.has_key('HTTP_X_FORWARDED_FOR'):
        ip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        ip = request.META['REMOTE_ADDR']
    #info = {"ip": ip}
    #return HttpResponse(json.dumps(info),content_type='application/json')
    return HttpResponse(ip,content_type='text/html')