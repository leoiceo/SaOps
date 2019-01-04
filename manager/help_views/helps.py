#_*_coding:utf-8_*_
from django.shortcuts import render,HttpResponseRedirect,render_to_response,HttpResponse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from manager.models import *
from manager.common import *
from manager.forms import *
from django.db.models import Q
import json

@login_required
def index(request):
    header_title, nav, tip = "文档列表", "帮助", "帮助文档"

    category = request.GET.get("category")
    tag_id = request.GET.get("tag")
    search = request.GET.get("search")

    if request.POST:
        article_list = request.POST.get("ids")

        for article_id in eval(article_list):

            article = Article.objects.filter(id=article_id)
            article.delete()
        info = {"status": True, "msg": "删除成功"}

        return HttpResponse(json.dumps(info), content_type='application/json')

    Article_count = Article.objects.all().count()

    if category is not None and tag_id is not None:
        zone = category
        article_info = Article.objects.filter(category__name=category,tag__id=tag_id)
    elif category is not None:
        article_info = Article.objects.filter(category__name=category)
        zone = category
    elif tag_id is not None:
        article_info = Article.objects.filter(tag__id=tag_id)
    elif search is not None:
        article_info = Article.objects.filter(Q(name__icontains=search)|Q(content__icontains=search))
    else:
        article_info = Article.objects.all()

    return render_to_response('manager/help_index.html', locals(), context_instance=RequestContext(request))


@login_required
def new_article(request):
    header_title, nav, tip = "新建文档", "帮助", "新建文档"
    if request.POST:
        name = request.POST.get("name")
        category = request.POST.get("category")
        tag = request.POST.get("tag")
        content = request.POST.get("content")
        operator = UserProfile.objects.get(email="%s" % request.user).name

        if len(name) != 0 or len(content) != 0:
            category_id = CateGory.objects.get(id=category)
            tag_id = Tag.objects.get(id=tag)
            user_id = UserProfile.objects.get(name=operator)
            w = Article(name=name,category=category_id,tag=tag_id,create_user=user_id,content=content)
            w.save()

            return HttpResponseRedirect(reverse('help_index'))

    category_info = CateGory.objects.all()
    tag_info = Tag.objects.all()
    return render_to_response('manager/new_article.html', locals(), context_instance=RequestContext(request))

@login_required
def edit(request):
    header_title, nav, tip = "编辑文档", "帮助", "编辑文档"
    if request.GET:
        article = request.GET.get("id")
        action = request.GET.get("action")
    else:
        action = request.POST.get("action")

    if action == "del":
        a_del = Article.objects.filter(id=article)
        a_del.delete()
        return HttpResponseRedirect(reverse('help_index'))
    elif action == "edit":
        current_id = Article.objects.get(id=article)
        category_info = CateGory.objects.all()
        tag_info = Tag.objects.all()
    elif action == "save":
        name = request.POST.get("name")
        category = request.POST.get("category")
        tag = request.POST.get("tag")
        content = request.POST.get("content")
        operator = UserProfile.objects.get(email="%s" % request.user).name

        if len(name) != 0 or len(content) != 0:
            category_id = CateGory.objects.get(id=category)
            tag_id = Tag.objects.get(id=tag)
            user_id = UserProfile.objects.get(name=operator)
            update_article = Article.objects.filter(id=article)
            update_article.update(name=name,category=category_id,tag=tag_id,create_user=user_id,content=content)
            return HttpResponseRedirect(reverse('help_index'))

    return render_to_response('manager/help_edit.html', locals(), context_instance=RequestContext(request))


@login_required
def detail(request):
    header_title, nav, tip = "查看文档", "帮助", "查看文档"
    id = request.GET.get("id")
    article_info = Article.objects.get(id=id)

    return render_to_response('manager/help_detail.html', locals(), context_instance=RequestContext(request))