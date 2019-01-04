#!/usr/bin/python
#_*_coding:utf-8_*_
# code.by leoiceo

from manager.common import *
from hosts.forms import ReposManagerForm
from manager.views.permission import *


@login_required
@PermissionVerify()
def repos_list(request):
    header_title, nav, tip = "发布仓库管理", "基础资源管理", "发布仓库管理"
    project = request.GET.get("project")
    af = ReposManagerForm()
    iUser = UserProfile.objects.get(email="%s" % request.user)
    if iUser.is_admin:
        pro_info = Project.objects.all()
        repos_info = ReposManager.objects.all()
    else:
        pro_info = iUser.project.all()
        pro_list = []
        for p in pro_info:
            pname = p.name
            pro_list.append(pname)

        repos_info = ReposManager.objects.filter(project__name__in=pro_list)

    if project is not None:
        repos_info = ReposManager.objects.filter(project__mini_name=project)

    if request.method == 'POST':
        action = request.POST.get("action")
    else:
        action = request.GET.get("action")

    if action == "delete":
        key_id = request.GET.get("id")
        del_key = ReposManager.objects.filter(id=key_id)
        del_key.delete()

    elif action == "add":
        if request.method == 'POST':
            af_post = ReposManagerForm(request.POST)
            name = request.POST.get('repos_name', '')
            try:
                if ReposManager.objects.filter(repos_name=name):
                    error = u'该仓库 %s 已存在!' % name
                    raise Exception(error)
            except Exception:
                pass
            else:
                if af_post.is_valid():
                    af_save = af_post.save(commit=False)
                    af_save.save()
                    af_post.save_m2m()
                else:
                    msg = "新仓库 %s 添加失败" % name

    return render_to_response('hosts/repos_list.html', locals(), context_instance=RequestContext(request))

@login_required
@PermissionVerify()
def repos_edit(request):
    header_title, nav, tip = "编辑仓库信息", "发布仓库管理", "编辑仓库信息"

    repos_id = request.GET.get("id")
    repos_info = ReposManager.objects.get(id=repos_id)
    if repos_info:
        af = ReposManagerForm(instance=repos_info)
    else:
        msg = "没有找到仓库信息ID： %s" % repos_id

    if request.method == 'POST':
        af_post = ReposManagerForm(request.POST, instance=repos_info)
        repos_name = request.POST.get('repos_name', '')
        try:
            repos_test = ReposManager.objects.get(repos_name=repos_name)
            if repos_test and repos_id != unicode(repos_test.id):
                error = u'该仓库名 %s 已存在!' % repos_name
                raise Exception(error)
        except Exception, e:
            pass
        else:

            if af_post.is_valid():
                af_save = af_post.save(commit=False)
                af_save.save()
                af_post.save_m2m()
                msg = "仓库信息 %s 修改成功" % repos_name
                af = ReposManagerForm(instance=repos_info)
            else:
                error = "仓库信息 %s 修改失败" % repos_name

    return render_to_response('hosts/repos_edit.html', locals(), context_instance=RequestContext(request))
