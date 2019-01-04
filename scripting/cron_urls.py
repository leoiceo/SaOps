from django.conf.urls import include, url, patterns

urlpatterns = patterns('scripting.views',
    url(r'task_plan/$','crontabs.task_plan',name='task_plan' ),
    url(r'task_plan_eye/$','crontabs.task_plan_eye',name='task_plan_eye' ),
    url(r'task_plan_manage/$','crontabs.task_plan_manage',name='task_plan_manage' ),
    url(r'task_plan_hosts/$','crontabs.task_plan_hosts',name='task_plan_hosts' ),
    url(r'check_task_hosts/$','crontabs.check_task_hosts',name='check_task_hosts' ),
)