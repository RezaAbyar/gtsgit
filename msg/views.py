import datetime
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from base.models import UserPermission, DefaultPermission
from base.views import checkxss
from util import HOME_PAGE
from .forms import SearchForm
from .models import *
from base.serializers import RoleSerializer
from api.samplekey import encrypt as Encrypt, decrypt as Decrypt

def inbox(request, id):
    owner_p = UserPermission.objects.filter(owner_id=request.user.owner.id)
    if owner_p.count() == 0:
        owner_p = DefaultPermission.objects.filter(role_id=request.user.owner.role_id)
    formpermmision = {}
    for i in owner_p:
        formpermmision[i.permission.name] = i.accessrole.ename
    # --------------------------------------------------------------------------------------
    if request.user.owner.role.role in ['mgr', 'setad']:
        owners = Owner.objects.filter(active=True, role__role='gs')
    else:
        owners = Owner.objects.filter(active=True, role__role='gs', zone_id=request.user.owner.zone_id)
    msgs = None
    if id == 'inbox':
        msgs = ListMsg.objects.filter(user_id=request.user.owner.id, isremove=False).order_by('isread', '-id')
    if id == 'send':
        msgs = CreateMsg.objects.filter(owner_id=request.user.owner.id).order_by('-id')
    if id == 'star':
        msgs = ListMsg.objects.filter(user_id=request.user.owner.id, isremove=False, star=True).order_by('-id')
    if id == 'remove':
        msgs = ListMsg.objects.filter(user_id=request.user.owner.id, isremove=True).order_by('-id')
    s_inbox = ListMsg.objects.filter(user_id=request.user.owner.id, isremove=False, isread=False).count()
    s_star = ListMsg.objects.filter(user_id=request.user.owner.id, isremove=False, star=True).count()
    s_remove = ListMsg.objects.filter(user_id=request.user.owner.id, isremove=True).count()
    if 'search' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            cd = form.cleaned_data['search']
            msgs = msgs.filter(Q(msg__info__icontains=cd) | Q(msg__titel__icontains=cd))
    if id == 'send':
        paginator = Paginator(msgs, 500)
    else:
        paginator = Paginator(msgs, 5)
    page_num = request.GET.get('page')
    data = request.GET.copy()

    if 'page' in data:
        del data['page']
    query_string = request.META.get("QUERY_STRING", "")

    if query_string.startswith("page"):
        query_string = query_string.split("&", 1)
        query_string = query_string[1]
    page_object = paginator.get_page(page_num)
    page_obj = paginator.num_pages
    if request.method == 'POST':
        url = request.META.get('HTTP_REFERER')
        titel = request.POST.get('titel')
        isreplay = request.POST.get('isreplay')
        if isreplay == 'on':
            isreplay = True
        else:
            isreplay = False
        info = request.POST.get('info')
        items = request.POST.getlist('owner')
        payam = CreateMsg.objects.create(titel=checkxss(titel), info=checkxss(info), owner_id=request.user.owner.id,
                                         isreply=isreplay)
        payam.orginal = payam.id
        payam.save()
        for item in items:
            if item == 'g1':
                if request.user.owner.role.role == 'zone':
                    for send in Owner.objects.filter(role__role='gs', zone_id=request.user.owner.zone_id, active=True):
                        ListMsg.objects.create(msg_id=payam.id, user_id=send.id, orginal=payam.id)
                if request.user.owner.role.role == 'area':
                    for send in Owner.objects.filter(role__role='gs', area_id=request.user.owner.area_id, active=True):
                        ListMsg.objects.create(msg_id=payam.id, user_id=send.id, orginal=payam.id)
                if request.user.owner.role.role in ['setad', 'mgr', 'test']:
                    for send in Owner.objects.filter(role__role='gs', active=True):
                        ListMsg.objects.create(msg_id=payam.id, user_id=send.id, orginal=payam.id)
            elif item == 'g2':
                if request.user.owner.role.role == 'zone':
                    for send in Owner.objects.filter(role__role='tek', zone_id=request.user.owner.zone_id, active=True):
                        ListMsg.objects.create(msg_id=payam.id, user_id=send.id, orginal=payam.id)
                if request.user.owner.role.role in ['setad', 'mgr', 'test']:
                    for send in Owner.objects.filter(role__role='tek', active=True):
                        ListMsg.objects.create(msg_id=payam.id, user_id=send.id, orginal=payam.id)
            elif item == 'g3':
                for send in Owner.objects.filter(refrence_id=1, active=True):
                    ListMsg.objects.create(msg_id=payam.id, user_id=send.id, orginal=payam.id)

            elif item == 'g4':
                if request.user.owner.role.role == 'zone':
                    for send in Owner.objects.filter(role__role='area', zone_id=request.user.owner.zone_id,
                                                     active=True):
                        ListMsg.objects.create(msg_id=payam.id, user_id=send.id, orginal=payam.id)
                if request.user.owner.role.role in ['setad', 'mgr', 'test']:
                    for send in Owner.objects.filter(role__role='area', active=True):
                        ListMsg.objects.create(msg_id=payam.id, user_id=send.id, orginal=payam.id)
            elif item == 'g5':
                if request.user.owner.role.role in ['setad', 'mgr']:
                    for send in Owner.objects.filter(role__role='setad', active=True):
                        ListMsg.objects.create(msg_id=payam.id, user_id=send.id, orginal=payam.id)
            elif item == 'g6':
                if request.user.owner.role.role in ['setad', 'mgr', 'zone']:
                    for send in Owner.objects.filter(role__role='zone', refrence_id=6, active=True):
                        ListMsg.objects.create(msg_id=payam.id, user_id=send.id, orginal=payam.id)
                    for send in Owner.objects.filter(role_id=101, active=True):
                        ListMsg.objects.create(msg_id=payam.id, user_id=send.id, orginal=payam.id)
            elif item == 'g7':
                for send in Owner.objects.filter(refrence_id=2, active=True):
                    ListMsg.objects.create(msg_id=payam.id, user_id=send.id, orginal=payam.id)

            else:
                ListMsg.objects.create(msg_id=payam.id, user_id=item, orginal=payam.id)
        messages.success(request, 'پیام شما با موفقیت ارسال شد.')
        return redirect(url, id)
    return render(request, 'inbox.html',
                  {'msgs': page_object, 'query_string': query_string, 'owners': owners, 'id': id, 's_inbox': s_inbox,
                   's_star': s_star, 'formpermmision': formpermmision, 'page_obj': page_obj,
                   's_remove': s_remove})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def getRole(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        list = []
        if id == 'group':
            listd = {
                'id': 'g1',
                'name': 'همه جایگاهداران',
                'lname': '',
            }
            list.append(listd)
            listd = {
                'id': 'g2',
                'name': 'همه پشتیبانان',
                'lname': '',
            }
            list.append(listd)
            listd = {
                'id': 'g3',
                'name': 'همه روسای سامانه',
                'lname': '',
            }
            list.append(listd)
            listd = {
                'id': 'g4',
                'name': 'همه کاربران نواحی',
                'lname': '',
            }
            list.append(listd)
            listd = {
                'id': 'g5',
                'name': 'همه کاربران ستاد',
                'lname': '',
            }
            list.append(listd)
            listd = {
                'id': 'g6',
                'name': 'همه کارشناسان سامانه مناطق',
                'lname': '',
            }
            list.append(listd)
            listd = {
                'id': 'g7',
                'name': 'همه مدیران مناطق',
                'lname': '',
            }
            list.append(listd)
        else:
            if id == 'gs':
                owners = Owner.objects.filter(active=True, role__role=id, zone_id=request.user.owner.zone_id)
            else:
                owners = Owner.objects.filter(active=True, role__role=id)
            srz_data = RoleSerializer(instance=owners, many=True)
            list = srz_data.data
        return JsonResponse({"message": "success", 'mylist': list})


def delmsg(request, id):
    if len(str(id)) < 6:
        messages.warning(request, 'دسترسی غیر مجاز')
        return redirect(HOME_PAGE)
    id = Decrypt(id)
    url = request.META.get('HTTP_REFERER')
    msg = ListMsg.objects.get(id=id,user_id=request.user.owner.id)
    msg.isremove = True
    msg.save()
    return redirect(url)


def setStar(request, id):
    if len(str(id)) < 6:
        messages.warning(request, 'دسترسی غیر مجاز')
        return redirect(HOME_PAGE)
    id = Decrypt(id)
    url = request.META.get('HTTP_REFERER')
    msg = ListMsg.objects.get(id=id,user_id=request.user.owner.id)
    msg.star = True
    msg.save()
    return redirect(url)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def isRead(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        msg = ListMsg.objects.get(id=id)
        if msg.isread:
            i = 0
        else:
            msg.isread = True
            msg.tarikh = datetime.datetime.now()
            msg.save()
    return JsonResponse({'message': 'success'})


def replyMsg(request):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        id = request.POST.get('msgidnew')
        reply = request.POST.get('reply')
    msg = ListMsg.objects.get(id=id)
    payam = CreateMsg.objects.create(info=reply, titel='پاسخ: ' + str(msg.msg.titel), owner_id=request.user.owner.id,
                                     orginal=msg.orginal)
    ListMsg.objects.create(msg_id=payam.id, user_id=msg.msg.owner.id, replyid=msg.msg.id, orginal=msg.orginal)
    return redirect(url)


def msgevent(request):
    mylist = []
    if request.method == 'POST':
        val = request.POST.get('val')

        list = ListMsg.objects.filter(msg_id=val).order_by('-isread')
        for item in list:
            if item.isread:
                read = 'خوانده شد'
                dread = str(item.pdate()) + ' ' + str(item.ptime())
            else:
                read = 'خوانده نشده'
                dread = '-'
            if item.user.role.name in ['zone', 'area', 'engin']:
                zonename = item.user.zone.name
            else:
                zonename = ""
            mydict = {
                'name': str(item.user.name) + ' ' + str(item.user.lname) + " (" + str(item.user.role.name) + ' ' + str(
                    zonename) + ")",
                'status': str(read) + ' ' + str(dread),
                'isreply': item.msg.isreply
            }
            mylist.append(mydict)

    return JsonResponse({"mylist": mylist, 'message': 'success'})


def chat(request):
    owner_p = UserPermission.objects.filter(owner_id=request.user.owner.id)
    if owner_p.count() == 0:
        owner_p = DefaultPermission.objects.filter(role_id=request.user.owner.role_id)
    formpermmision = {}
    for i in owner_p:
        formpermmision[i.permission.name] = i.accessrole.ename
    # --------------------------------------------------------------------------------------
    if request.method == 'POST':
        _id = request.POST.get('orginalid')

        msg = ListMsg.objects.filter(orginal=_id,user_id=request.user.owner.id).order_by('-id')
        mymsg = CreateMsg.objects.filter(orginal=_id,owner_id=request.user.owner.id).first().owner_id
        context = {'msg': msg, 'mymsg': mymsg, 'formpermmision': formpermmision}
        return render(request, 'chat.html', context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def msgmodal(request):
    if request.method == 'POST':

        titel = request.POST.get('subject_msg')
        isreplay = True
        info = request.POST.get('info_msg')
        items = request.POST.get('idcodemeli')
        payam = CreateMsg.objects.create(titel=checkxss(titel), info=checkxss(info), owner_id=request.user.owner.id,
                                         isreply=isreplay)
        payam.orginal = payam.id
        payam.save()
        send=Owner.objects.get(codemeli=items)
        ListMsg.objects.create(msg_id=payam.id, user_id=send.id, orginal=payam.id)
        return JsonResponse({'message': 'success'})