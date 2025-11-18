from django.shortcuts import redirect
from django.template.response import TemplateResponse
from accounts.logger import add_to_log
from base.permission_decoder import cache_permission
from .models import Videos, Tags
from django.contrib import messages


@cache_permission('0')
def blog(request):
    add_to_log(request, 'مشاهده فرم آموزش ', 0)
    videos = Videos.objects.filter(role__role=request.user.owner.role.role).order_by('-id')
    return TemplateResponse(request, 'blog_home.html', {'videos': videos, 'active': 1})


@cache_permission('0')
def videoplay(request, _id):
    try:
        video = Videos.objects.get(id=_id, role__role=request.user.owner.role.role)
        video.views += 1
        video.save()
        add_to_log(request, 'مشاهده  آموزش ' + str(video.title), 0)
    except Videos.DoesNotExist:
        messages.error(request, 'ویدیو مورد نظر یافت نشد')
        return redirect('blog:blog')
    return TemplateResponse(request, 'videoplay.html', {'video': video})


@cache_permission('0')
def videotags(request, _en):
    en = Tags.objects.get(en=_en).name
    add_to_log(request, 'مشاهده  آموزش  tag ' + str(en), 0)
    videos = Videos.objects.filter(tags__en=_en, role__role=request.user.owner.role.role).order_by('sort')
    return TemplateResponse(request, 'blog_home.html',
                            {'videos': videos, 'en': en, 'active': 2})
