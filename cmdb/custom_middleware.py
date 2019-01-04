#_*_coding:utf-8_*_
from manager.models import LoginHistory

class TestMiddleware(object):

    def process_request(self,request):

        try:
            if request.META.has_key('HTTP_X_FORWARDED_FOR'):
                ip = request.META['HTTP_X_FORWARDED_FOR']
            else:
                ip = request.META['REMOTE_ADDR']

            username = request.user.name
            if request.path == "/skin_config/" or 'status' in request.path or 'admin' in request.path or 'favicon' in request.path \
                    or 'process' in request.path:
                pass
            else:
                get_path = request.get_full_path()
                fw = LoginHistory(name=username, ip=ip, stats="请求页面", get_full_path=get_path)
                fw.save()

        except Exception, e:
            import datetime
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print now, 'AnonymousUser', request.path

    def process_view(self,request, view_func, view_args, view_kwargs):
        print "power by limengbo,processing request view",request,view_func

    def process_response(self,request,response):
        print "power by limengbo,processing request response",request
        return response
