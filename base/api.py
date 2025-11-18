import jdatetime
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import redirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth.models import User
from accounts.logger import add_to_log
from base.code import generateotp
from base.serializers import ZoneSerializer
from base.views import SendOTP2
from pay.models import StoreList, StoreHistory
from pay.views import pumpcheck
from permission import ShowFailurePermission, CloseTicketOwnerPermission, OwnerCreatePermission
from sell.models import SellModel, IpcLog
from utils.exception_helper import zoneorarea, checknumber, checkxss, distance
from base.models import FailureSub, Pump, Ticket, Workflow, UserPermission, DefaultPermission, Owner, GsList, Parametrs, \
    WorkflowLog, Zone, GsModel, Reply, FailureCategory, Organization, NegativeScore, Storage, OwnerZone, Refrence, Role, \
    Peykarbandylog
from datetime import datetime
import datetime
from django.db import IntegrityError, transaction
import random
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def subfailure(request, *args, **kwargs):
    thislist = []
    ok = 0
    if request.method == 'POST':
        tid = request.POST.get('Tid')

        result = FailureSub.objects.get(id=tid)
        if result.isnazel == True:
            ok = 1

        else:
            ok = 0

    return JsonResponse({"mylist": thislist, 'ok': ok})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def loadnazel(request, *args, **kwargs):
    thislist = []
    ticketlist = []
    _lat = 0
    _lon = 0
    if request.method == 'POST':
        gid = request.POST.get('gId')
        try:
            gsmodel = GsModel.objects.get(id=gid)
            _location = gsmodel.location.split(',')
            _lat = _location[0]
            _lon = _location[1]
        except:
            pass
        pro = []
        pro.append(948)
        if gsmodel.area.zone.ticket_benzin:
            pro.append(2)
        if gsmodel.area.zone.ticket_super:
            pro.append(3)
        if gsmodel.area.zone.ticket_gaz:
            pro.append(4)
        nazels = Pump.objects.filter(gs_id=gid, status__status=True, product_id__in=pro).order_by('number')
        tickets = Ticket.objects.filter(gs_id=gid, status__status='open')
        for item in tickets:
            workcount = Workflow.objects.filter(ticket_id=item.id).count()

            isdel = 1 if workcount == 1 and item.owner_id == request.user.id else 0

            if item.Pump_id:
                pump = item.Pump.number
            else:
                pump = 0,
            thisdict = {
                "id": item.id,
                "pump": pump,
                "organization": item.organization.name,
                "oid": item.organization.id,
                "failure": item.failure.info,
                "status": item.status_id,
                "isdel": isdel,
            }

            ticketlist.append(thisdict)

        for item in nazels:
            thisdict = {
                "id": item.id,
                "number": item.number,
                "product": item.product.name,
            }

            thislist.append(thisdict)

    return JsonResponse({"mylist": thislist, 'ticketlist': ticketlist, 'lat': _lat, 'lon': _lon})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def getworkflow(request):
    thislist = []
    myticket = []
    access = '1'
    end_vahed = 0
    owner_p = UserPermission.objects.filter(owner_id=request.user.owner.id)
    if owner_p.count() == 0:
        owner_p = DefaultPermission.objects.filter(role_id=request.user.owner.role_id,
                                                   semat_id=request.user.owner.refrence_id)
    ua = owner_p.get(permission__name='t_open')
    if ua.accessrole.ename != 'view':
        formpermmision = 1
    else:
        formpermmision = 0
    # --------------------------------------------------------------------------------------
    _role = request.user.owner.role.role
    _roleid = zoneorarea(request)
    serialmaster = ""
    serialpinpad = ""
    nextsell = 0
    msg = ""
    tek = ""
    tektell = ""
    a = "-"
    _item = 1
    _newtime = False
    if request.method == 'POST':
        obj = request.POST.get('obj')
        _rnd = request.POST.get('rnd')

        if Owner.objects.filter(id=request.user.owner.id, daghimande=True).count() > 0:
            return JsonResponse({"message": "no", 'msg': msg, 'formpermmision': formpermmision})
        else:

            try:
                _ticket = Ticket.objects.get(id=obj, rnd=_rnd)
                if _ticket.usererja and _ticket.usererja == request.user.owner.id:
                    ticket = _ticket
                else:
                    ticket = Ticket.object_role.c_gs(request, 1).get(id=obj, rnd=_rnd)
            except ObjectDoesNotExist as e:
                msg = 'این محتوا وجود ندارد'
                return JsonResponse({'msg': msg + "|" + str(e)})
            if ticket.Pump_id:
                nextsell = SellModel.objects.filter(tolombeinfo_id=ticket.Pump_id, tarikh__gt=ticket.shamsi_date,
                                                    sellkol__gt=10).count()
            closebyqrcode = ticket.failure.closebyqrcode
            if closebyqrcode:
                owner = Owner.objects.get(id=request.user.owner.id)
                owner.qrcode2 = ""
                owner.qrcode = ""
                owner.save()
            if ticket.failure.isclosetek == False:
                if ticket.failure.organizationclose == 'fani,test':
                    end_vahed = ' خدمات فنی یا تست راه اندازی '
                if ticket.failure.organizationclose == 'fani':
                    end_vahed = ' خدمات فنی '
                if ticket.failure.organizationclose == 'test':
                    end_vahed = ' تست و راه اندازی '
                if ticket.failure.organizationclose == 'engin':
                    end_vahed = ' مهندسی '
                if ticket.failure.organizationclose == 'shef':
                    end_vahed = ' رئیس سامانه هوشمند '
                if ticket.failure.organizationclose == 'hoze':
                    end_vahed = ' رئیس حوزه '
                if ticket.failure.organizationclose == 'area':
                    end_vahed = ' رئیس ناحیه '

                ending = 0
            else:
                ending = 1
            if ticket.failure.organizationclose:
                if request.user.owner.role.role in ticket.failure.organizationclose:
                    ending = 1
            if request.user.owner.role.role == 'area':
                if ticket.organization_id != 7:
                    access = '0'
            if request.user.owner.role.role == 'tek':
                if ticket.organization_id != 1:
                    access = '0'
            if ticket.Pump_id:
                nazel = ticket.Pump.number
                nazel_id = ticket.Pump.id
                if ticket.Pump.master:
                    serialmaster = f'  سریال کارتخوان: {ticket.Pump.master}'
                if ticket.Pump.master:
                    serialpinpad = f' سریال صفحه کلید: {ticket.Pump.pinpad}'
            else:
                nazel = "-"
                nazel_id = "-"
                serialmaster = "-"
                serialpinpad = "-"
            _tek = GsList.objects.filter(owner__role__role='tek', gs_id=ticket.gs_id, owner__active=True).last()
            if _tek:
                tek = _tek.owner
                tektell = _tek.owner.mobail
            if len(ticket.gs.address) > 1:
                address = ticket.gs.address
            else:
                address = 'آدرس ثبت نشده'
            thisdict = {
                "id": ticket.id,
                "info": ticket.failure.info,
                "gsid": ticket.gs.gsid,
                "gs_id": ticket.gs.id,
                "gsname": ticket.gs.name,
                "nazel": nazel,
                "tek": str(tek),
                "tektell": str(tektell),
                "nazel_id": nazel_id,
                'serialmaster': serialmaster,
                'serialpinpad': serialpinpad,
                'fid': ticket.failure.id,
                'address': address,
                'isclose': ticket.status_id,

            }

            myticket.append(thisdict)
            result = Workflow.objects.filter(ticket_id=obj).order_by('id')
            i = 0

            if result:
                ok = 1
                for item in result:
                    i += 1
                    if request.user.owner.role.role in ['test', 'fani', 'setad', 'mgr']:
                        tell = item.user.owner.mobail
                    elif request.user.owner.refrence_id == 1 and item.user.owner.zone_id == request.user.owner.zone_id:
                        tell = item.user.owner.mobail
                    else:
                        tell = '-'
                    if item.user.owner.refrence_id:
                        iname = item.user.owner.refrence.name
                    else:
                        iname = ""
                    lat = 0
                    if item.lat:
                        lat = item.lat
                    lng = 0
                    if item.lang:
                        lng = item.lang
                    try:
                        loc = ticket.gs.location.split(',')
                        _lat = loc[0]
                        _lang = loc[1]
                        a = distance(float(lat), float(_lat), float(lng), float(_lang))
                        a = int(a)
                        a2 = int(a)

                        if a < 600:
                            a = "عملیات در جایگاه انجام شد"
                        elif a > 999:
                            a = a / 1000
                            a = int(a)
                            a = f'فاصله تکنسین تا جایگاه {a} کیلومتر میباشد'
                            newtime = (datetime.datetime.now() - item.createtime).seconds

                            _newtime = True if newtime < 900 else False
                        else:
                            a = f'فاصله تکنسین تا جایگاه {a} متر میباشد'
                            newtime = (datetime.datetime.now() - item.createtime).seconds

                            _newtime = True if newtime < 900 else False
                        if ticket.gs.gpssignal == False:
                            a = a + ' - سیگنال GPS  در این جایگاه دقیق نمیباشد '
                        if request.user.owner.role.role != 'tek':
                            _newtime = False
                        if item.user.owner.id != request.user.owner.id:
                            _newtime = False
                        if a2 < 100:
                            _newtime = False

                    except TypeError as e:
                        msg = 'آدرس جغرافیایی جایگاه در فرم مشخصات جایگاه بطور صحیح وارد نشده'
                        return JsonResponse({'msg': msg + "|" + str(e)})
                    except IndexError as e:
                        msg = 'آدرس جغرافیایی جایگاه در فرم مشخصات جایگاه بطور صحیح وارد نشده'
                        return JsonResponse({'msg': msg + "|" + str(e)})
                    except AttributeError as e:
                        msg = 'آدرس جغرافیایی جایگاه در فرم مشخصات جایگاه بطور صحیح وارد نشده'
                        return JsonResponse({'msg': msg + "|" + str(e)})
                    except ObjectDoesNotExist as e:
                        msg = 'این محتوا وجود ندارد'
                        return JsonResponse({'msg': msg + "|" + str(e)})
                    loclat = loc[0]
                    loclong = loc[1]
                    s_master = item.serialmaster if item.serialmaster else ''
                    s_master_daghi = item.serialmasterdaghi if item.serialmasterdaghi else ''
                    s_pinpad = item.serialpinpad if item.serialpinpad else ''
                    s_pinpad_daghi = item.serialpinpaddaghi if item.serialpinpaddaghi else ''

                    parametr = Parametrs.objects.all().first()
                    isgps = parametr.isgps
                    thisdict = {
                        "id": item.id,
                        "name": item.user.owner.name + ' ' + item.user.last_name,
                        "info": item.description,
                        "date": item.pdate(),
                        "time": item.ptime(),
                        "org": item.organization.name,
                        "count": i,
                        "gs": item.ticket.gs_id,
                        "phone": tell,
                        "oid": item.organization.id,
                        'failure': item.failure.info,
                        'status': item.ticket.status_id,
                        'macaddress': item.macaddress,
                        'counter': result.count() - 1,
                        'role': iname + ' - ' + item.user.owner.role.name,
                        'lat': lng,
                        'long': lat,
                        'latto': loclat,
                        'longto': loclong,
                        's_master': s_master,
                        's_master_daghi': s_master_daghi,
                        's_pinpad': s_pinpad,
                        's_pinpad_daghi': s_pinpad_daghi,
                        'metr': a,
                        'newtime': _newtime,

                    }
                    _item = item.id
                    thislist.append(thisdict)
            else:
                ok = 0
        if request.user.owner.refrence_id == '1':
            access = '1'
        if request.user.owner.role.role == 'gs':
            if ticket.organization.organiztion == 'gs':
                access = '1'
            else:
                access = '0'

        if request.user.owner.refrence.ename == 'tek' and ticket.organization.organiztion == 'tek':
            access = '1'
        isboarder = request.user.owner.isboarder
        WorkflowLog.objects.create(owner_id=request.user.owner.id, workflow_id=_item)
        return JsonResponse(
            {"mylist": thislist, 'end_vahed': end_vahed, 'ending': ending, 'myticket': myticket, 'ok': ok,
             'isgps': isgps,
             'nextsell': nextsell, 'closebyqrcode': closebyqrcode, 'isboarder': isboarder,
             'formpermmision': formpermmision, 'msg': msg,
             'access': access})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def showmalek(request, *args, **kwargs):
    thislist = []
    if request.method == 'POST':
        gsid = request.POST.get('id')
        query = GsList.objects.filter(gs_id=gsid, owner__role__role__in=['gs', 'tek'])
        if query.count() > 0:
            ok = 1
        else:
            ok = 2
        for q in query:
            if q.owner.role.role == 'tek':
                role = 'تکنسین'
            elif q.owner.role.role == 'gs':
                role = 'مالک'
            thisdict = {
                "id": q.id,
                "name": q.owner.name,
                "codemeli": q.owner.user.username,
                "gs": q.gs.name,
                "lname": q.owner.lname + ' ( ' + str(role) + ' )',
                "mobail": q.owner.mobail,
            }
            thislist.append(thisdict)
        return JsonResponse({"mylist": thislist, 'ok': ok, 'message': 'success'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getrole(request, id, *args, **kwargs):
    thislist = []
    query = None
    role = request.POST.get('master')
    if role == 1:
        query = Zone.objects_limit.all()
    for q in query:
        thisdict = dict(id=q.id, name=q.name)
        thislist.append(thisdict)
    return JsonResponse({"mylist": thislist})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def saveusr(request, *args, **kwargs):
    if request.method == 'POST':

        idgs = request.POST.get('IdGs')
        codmeli = request.POST.get('CodMeli')
        codmeli = checkxss(codmeli)
        codmeli = checknumber(codmeli)
        passid = request.POST.get('PassId')
        firstnameid = request.POST.get('firstNameId')
        firstNameId = checkxss(firstnameid)
        lastnameid = request.POST.get('lastNameId')
        lastNameId = checkxss(lastnameid)
        mobailid = request.POST.get('mobailId')
        mobailId = checkxss(mobailid)
        mobailId = checknumber(mobailId)

        try:
            user = User.objects.create_user(codmeli, 'aa@tt.com')
            user.set_password(passid)
            user.last_name = lastnameid
            user.first_name = firstnameid
            user.save()
            add_to_log(request, ' ایجاد کاربر ' + str(codmeli), 0)

            owner = Owner.objects.create(user_id=user.id, name=str(firstnameid), lname=str(lastnameid), mobail=mobailid,
                                         codemeli=codmeli, role_id=2)
            GsList.objects.create(owner_id=owner.id, gs_id=idgs)
        except IntegrityError:
            user = User.objects.get(username=codmeli)
            owner = Owner.objects.get(codemeli=codmeli)
            GsList.objects.create(owner_id=owner.id, gs_id=idgs)
    return JsonResponse({"mylist": 1})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def saveeditusr(request, *args, **kwargs):
    if request.method == 'POST':
        oldcodmeli = request.POST.get('oldCodeMeli')
        codmeli = request.POST.get('CodMeli')
        firstnameid = request.POST.get('firstNameId')
        lastnameid = request.POST.get('lastNameId')
        mobailid = request.POST.get('mobailId')

        edituser = User.objects.get(username=oldcodmeli)
        edituser.username = checkxss(codmeli)
        edituser.first_name = checkxss(firstnameid)
        edituser.last_name = checkxss(lastnameid)
        edituser.save()
        owner = Owner.objects.get(user_id=edituser.id)
        owner.codemeli = checkxss(codmeli)
        owner.lname = checkxss(lastnameid)
        owner.name = checkxss(firstnameid)
        owner.mobail = checkxss(mobailid)

        owner.save()
        add_to_log(request, 'ویرایش کاربر ' + str(codmeli), 0)
    return JsonResponse({"mylist": 1})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def saveaddgs(request, *args, **kwargs):
    thislist = []
    _role = request.user.owner.role.role
    _roleid = zoneorarea(request)

    if request.method == 'POST':
        gsidgs = request.POST.get('gsidGs')
        namegs = request.POST.get('nameGs')
        addressgs = request.POST.get('addressGs')
        tellgs = request.POST.get('tellGs')
        id_area = request.POST.get('id_area')

        _rnd = random.randint(10000000, 99999999)

        gs = GsModel.object_role.c_gsmodel(request).create(gsid=gsidgs, name=checkxss(namegs),
                                                           address=checkxss(addressgs), rnd=_rnd,
                                                           phone=checkxss(tellgs), area_id=id_area, status_id=3,
                                                           user_id=request.user.id)
        add_to_log(request, 'ایجاد جایگاه ' + str(gsidgs), gsidgs)
        thisdict = {
            "gsid": gsidgs,
            "name": namegs,
            "address": addressgs,
            "tell": tellgs,
            "area": gs.area.name,
            "zone": gs.area.zone.name,
            "id": gs.id,
        }
        thislist.append(thisdict)
    return JsonResponse({"mylist": thislist})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def getnazel(request, *args, **kwargs):
    thislist = []
    if request.method == 'POST':
        gsid = request.POST.get('id')
        query = Pump.objects.filter(active=True, gs_id=gsid).order_by('number')
        if query.count() > 0:
            ok = 1
        else:
            ok = 2
        for q in query:
            thisdict = {
                "id": q.id,
                "number": q.number,
                "product": q.product.name,
                "master": q.master,
                "pinpad": q.pinpad,
                "pumpbrand": q.pumpbrand.name,
                "actived": q.actived,

            }
            thislist.append(thisdict)
        return JsonResponse({"mylist": thislist, 'ok': ok, 'message': 'success'})


class SaveNazel(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        thislist = []
        if request.method == 'POST':

            nazelnuid = int(request.POST.get('nazelnuid'))
            gs = request.POST.get('id')
            productid = request.POST.get('productid')
            masterid = request.POST.get('masterid')
            pinpadid = request.POST.get('pinpadid')
            nazelmodelid = request.POST.get('nazelmodelid')
            activeid = request.POST.get('activeid')

            if activeid == 'on':

                activeid = True
            else:
                activeid = False

            try:

                p = Pump.objects.create(gs_id=gs, number=nazelnuid, product_id=productid, master=masterid,
                                        user_id=request.user.id,
                                        pinpad=pinpadid, pumpbrand_id=nazelmodelid, actived=activeid,
                                        uniq=str(nazelnuid) + '-' +
                                             str(gs))
                add_to_log(request, 'ایجاد نازل ' + str(p.gs.name) + ' شماره نازل ' + str(nazelnuid), int(gs))
                thisdict = {
                    "number": p.number,
                    "product": p.product.name,
                    "master": p.master,
                    "pinpad": p.pinpad,
                    "pumpbrand": p.pumpbrand.name,
                    "active": p.active,
                }
                ok = 1

                thislist.append(thisdict)

            except IntegrityError:

                ok = 0

            return JsonResponse({"mylist": thislist, "ok": ok})


class CatFailure(APIView):
    permission_classes = [IsAuthenticated, ShowFailurePermission]

    def post(self, request):
        thislist = []
        if request.method == 'POST':
            sid = request.POST.get('Sid')
            if request.user.owner.role.role == 'gs':
                result = FailureSub.objects.filter(failurecategory_id=sid, level__in=[1, 4], active=True)
            elif request.user.owner.role.role == 'tek':
                result = FailureSub.objects.filter(failurecategory_id=sid, level__in=[2, 4], active=True)
            else:
                result = FailureSub.objects.filter(failurecategory_id=sid, active=True)
            for item in result:
                thisdict = {
                    "id": item.id,
                    "info": item.info,
                    "isnazel": item.isnazel,

                }
                thislist.append(thisdict)

        return JsonResponse({"mylist": thislist})


class CatFailureEdit(APIView):
    permission_classes = [IsAuthenticated, ShowFailurePermission]

    def post(self, request):
        thislist = []
        if request.method == 'POST':
            sid = request.POST.get('Sid')
            tid = request.POST.get('tid')
            ticket = Ticket.objects.get(id=tid)

            if request.user.owner.role.role == 'gs':
                result = FailureSub.objects.filter(failurecategory_id=sid, level=1, active=True)
            else:
                result = FailureSub.objects.filter(failurecategory_id=sid, active=True)
            for item in result:
                thisdict = {
                    "id": item.id,
                    "info": item.info,
                    "isnazel": item.isnazel,

                }
                thislist.append(thisdict)
            myrpid = []
            _rpid = Reply.objects.filter(organization__organiztion=ticket.organization.organiztion,
                                         failurecat__in=[sid, 0],
                                         forwarditem=False, active=True).order_by('sort_id')
            for item in _rpid:
                dict = {
                    "id": item.id,
                    "info": item.info
                }
                myrpid.append(dict)
        return JsonResponse({"mylist": thislist, 'myrpid': myrpid})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def closeticket(request):
    _role = request.user.owner.role.role
    _roleid = zoneorarea(request)
    failursub = []
    replydic = []
    myfailur = None
    mycat = None
    if request.method == 'POST':
        obj = request.POST.get('obj')

        _ticket = Ticket.objects.get(id=obj)
        if _ticket.usererja and _ticket.usererja == request.user.owner.id:
            ticket = _ticket
        else:
            ticket = Ticket.object_role.c_gs(request, 1).get(id=obj)
        if ticket.failure.closebyqrcode:
            return False
        if ticket.status_id == 2:
            return False
        s_master = 1 if ticket.failure_id == 1163 else 0

        reply = Reply.objects.filter(organization__organiztion=ticket.organization.organiztion,
                                     failurecat__in=[ticket.failure.failurecategory_id, 0],
                                     forwarditem=False, active=True).order_by('sort_id')
        for rep in reply:
            thisdict = {
                "id": rep.id,
                "info": rep.info,
            }
            replydic.append(thisdict)
        myfailur = ticket.failure.id
        editable = ticket.failure.editable
        mycat = ticket.failure.failurecategory_id
        failur = FailureSub.objects.filter(failurecategory_id=ticket.failure.failurecategory.id)
        for fail in failur:
            thisdict = {
                "id": fail.id,
                "info": fail.info,
            }
            failursub.append(thisdict)
        _failurcat = []
        failurecat = FailureCategory.objects.all()
        for fail in failurecat:
            thisdict = {
                "id": fail.id,
                "info": fail.info,
            }
            _failurcat.append(thisdict)

    return JsonResponse(
        {"failursub": failursub, 'myfailur': myfailur, 'mycat': mycat, 'replydic': replydic, 's_master': s_master,
         'failurcat': _failurcat, 'editable': editable})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def getforward(request):
    _role = request.user.owner.role.role
    _roleid = zoneorarea(request)
    thislist = []
    replydic = []
    _sarfasllist = []
    _onvanlist = []

    if request.method == 'POST':

        sarfasllist = FailureCategory.objects.all()
        for fail in sarfasllist:
            thisdict = {
                "id": fail.id,
                "info": fail.info,
            }
            _sarfasllist.append(thisdict)
        onvanlist = FailureSub.objects.filter(active=True)
        for fail in onvanlist:
            thisdict = {
                "id": fail.id,
                "info": fail.info,
            }
            _onvanlist.append(thisdict)
        obj = request.POST.get('tid')
        _ticket = Ticket.objects.get(id=obj)
        if _ticket.usererja and _ticket.usererja == request.user.owner.id:
            ticket = _ticket
        else:
            ticket = Ticket.object_role.c_gs(request, 0).get(id=obj)
        editable = ticket.failure.editable
        work = Workflow.objects.filter(ticket_id=obj).order_by('-id')[:2]
        for w in work:
            _oid = w.organization_id
        if request.user.owner.role.role == 'engin':
            _list = Organization.objects.filter(
                organiztion__in=['engin', 'shef', 'area', 'gs', 'karshenasengin', 'tekengin'])
        elif request.user.owner.role.role == 'tek':
            _list = Organization.objects.filter(organiztion__in=['shef', 'fani', 'test', 'gs'])
        elif request.user.owner.role.role == 'area':
            _list = Organization.objects.filter(organiztion__in=['shef', 'engin', 'tek', 'gs'])
        elif request.user.owner.role.role == 'gs':
            _list = Organization.objects.filter(id=_oid)
            editable = False
        else:
            _list = Organization.objects.all()

        for fail in _list:
            thisdict = {
                "id": fail.id,
                "info": fail.name,
            }
            thislist.append(thisdict)
        reply = Reply.objects.filter(organization__organiztion=ticket.organization.organiztion,
                                     forwarditem=True).order_by(
            'sort_id')

        for rep in reply:
            thisdict = {
                "id": rep.id,
                "info": rep.info,

            }
            replydic.append(thisdict)
    return JsonResponse(
        {"thislist": thislist, 'sarfasllist': _sarfasllist, 'onvanlist': _onvanlist, 'replydic': replydic,
         'editable': editable,
         'refid': request.user.owner.refrence_id})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def getreplyischange(request):
    masters = []
    pinpads = []
    if request.method == 'POST':
        _role = request.user.owner.role.role
        _roleid = zoneorarea(request)
        obj = request.POST.get('obj')
        _gsid = request.POST.get('gsid')
        ticketid = request.POST.get('ticketid')
        print(ticketid)
        if request.POST.get('nazel'):
            _nazel = int(request.POST.get('nazel'))
            if _nazel < 10:
                _nazel = str("0") + str(_nazel)
        else:
            _nazel = 0

        if obj == "0":
            return JsonResponse({"message": "error"})
        _list = Reply.objects.get(id=obj)

        if _list.ispeykarbandi:
            otp_peykarbandi = generateotp(_gsid, _nazel)
            _gs = GsModel.objects.get(gsid=_gsid)
            Peykarbandylog.objects.create(gs_id=_gs.id, owner_id=request.user.owner.id, code=otp_peykarbandi,
                                          nazel=_nazel)
        else:

            otp_peykarbandi = "1"

        if _list.changemaster:
            master = 1
            result = StoreList.objects.filter(status_id=4, statusstore_id=1, getuser_id=request.user.owner.id,
                                              assignticket=ticketid)
            if len(result) == 0:
                result = StoreList.objects.filter(status_id=4, statusstore_id=1, getuser_id=request.user.owner.id,
                                                  assignticket__isnull=True)
            for item in result:
                _dict = {
                    'id': item.id,
                    'serial': item.serial,
                }
                masters.append(_dict)
        else:
            master = 0
            masters = []
        if _list.changepinpad:
            pinpad = 1
            result = StoreList.objects.filter(status_id=4, statusstore_id=2, getuser_id=request.user.owner.id,
                                              assignticket=ticketid)
            if len(result) == 0:
                result = StoreList.objects.filter(status_id=4, statusstore_id=2, getuser_id=request.user.owner.id,
                                                  assignticket__isnull=True)
            for item in result:
                _dict = {
                    'id': item.id,
                    'serial': item.serial,
                }
                pinpads.append(_dict)
        else:
            pinpad = 0
            pinpads = []
        if _list.isdaghimaster and master == 0:
            master = 2
        if _list.isdaghipinpad and pinpad == 0:
            pinpad = 2
        if _list.isdaghipinpad and _list.isdaghimaster and pinpad == 0 and master == 0:
            master = 2
            pinpad = 2
    if request.user.owner.refrence.ename == 'tek':
        _role = 'tek'

    return JsonResponse(
        {"master": master, 'pinpad': pinpad, 'masters': masters, 'pinpads': pinpads, 'otp_peykarbandi': otp_peykarbandi,
         'role': _role})


class GetCloseTicket(APIView):
    permission_classes = [IsAuthenticated, CloseTicketOwnerPermission]

    @transaction.atomic
    def post(self, request):
        _role = request.user.owner.role.role
        _roleid = zoneorarea(request)
        if request.method == 'POST':
            dgi = 5
            obj = request.POST.get('obj')
            infooidclose = request.POST.get('InfooIdClose')
            failurid = int(request.POST.get('failurId'))
            rpid = request.POST.get('rpId')
            cmasterid = request.POST.get('cmasterId')
            cpinpadid = request.POST.get('cpinpadId')
            _owner = Owner.objects.get(id=request.user.owner.id)
            if _owner.role.role == 'tek' and _owner.daghimande:
                return JsonResponse({"message": 'error'})

            if rpid == "0":
                return JsonResponse({"message": 'error'})

            lat = request.POST.get('lat')
            lang = request.POST.get('lang')
            autodaghi = int(request.POST.get('autodaghi'))

            if cpinpadid != '0':
                store_pinpad = StoreList.objects.get(id=cpinpadid)
                if store_pinpad.status_id != 4:
                    return JsonResponse({"message": 'error'})
                else:
                    store_pinpad = store_pinpad.serial
            else:
                store_pinpad = ''

            if cmasterid != '0':
                store_master = StoreList.objects.get(id=cmasterid)
                if store_master.status_id != 4:
                    return JsonResponse({"message": 'error'})
                else:
                    store_master = store_master.serial

            else:
                store_master = ''
            ticket = Ticket.objects.get(id=obj)
            if ticket.usererja and ticket.usererja == request.user.owner.id:
                _ticket = ticket
            else:
                _ticket = Ticket.object_role.c_gs(request, 1).get(id=obj)
            _ipclog = IpcLog.objects.filter(gs_id=_ticket.gs_id).last()
            _isdaghimaster = False
            _isdaghipinpad = False
            _nocloseafteraccept = False
            _closebysmart = False
            if rpid != '0':
                reply = Reply.objects.get(id=int(rpid))
                _isdaghimaster = reply.isdaghimaster
                _isdaghipinpad = reply.isdaghipinpad
                _nocloseafteraccept = reply.nocloseafteraccept
                _closebysmart = reply.closebysmart
                if reply.isdaghimaster or reply.isdaghipinpad:
                    dgi = 0

            if _ipclog and int(rpid) in [2, 4, 57, 58, 59, 60] and _ipclog.dashboard_version == '1.02.101701':
                work = Workflow.objects.create(ticket_id=obj, organization_id=3, description='ارجاع جهت پیکربندی',
                                               user_id=request.user.id, lat=lat, lang=lang, serialmaster=store_master,
                                               failure_id='1045')

            else:
                if rpid != '0':
                    desc = reply.info + str(infooidclose)
                else:
                    desc = checkxss(infooidclose)
                work = Workflow.objects.create(ticket_id=obj, organization_id=1, description=desc,
                                               user_id=request.user.id,
                                               lat=lat, lang=lang, failure_id=failurid, serialmaster=store_master,
                                               serialpinpad=store_pinpad)
            if _closebysmart:
                work = Workflow.objects.create(ticket_id=obj, organization_id=5,
                                               description='برای این تیکت داغی ثبت نشده و باید رئیس سامانه تایید کند',
                                               user_id=request.user.id,
                                               lat=lat, lang=lang, failure_id=failurid, serialmaster=store_master,
                                               serialpinpad=store_pinpad)
            if rpid == '0':
                rpid = 1

            _ticket = Ticket.objects.get(id=obj)
            if _ticket.usererja and _ticket.usererja == request.user.owner.id:
                ticket = _ticket
            else:
                ticket = Ticket.object_role.c_gs(request, 0).get(id=obj)

            ticket.failure_id = failurid
            ticket.reply_id = rpid

            if cpinpadid != '0':
                store = StoreList.objects.get(id=cpinpadid)
                store.status_id = 5
                store.pump_id = ticket.Pump_id
                store.save()
                pumpno = Pump.objects.get(id=ticket.Pump_id)
                daghi = pumpno.pinpad

                pumpcheck(store.serial, 2)
                pumpno.pinpad = store.serial
                ticket.serialpinpad = store.serial
                pumpno.active = True
                pumpno.actived = True
                pumpno.status_id = 1
                pumpno.save()
                StoreHistory.objects.create(store_id=store.id, owner_id=request.user.owner.id,
                                            information="ارسال قطعه از پشتیبان  " + str(store.getuser),
                                            status_id=5,
                                            description=f' تخصیص به جایگاه  {store.pump.gs.name} (تیکت {ticket.id})')

                if autodaghi == 1 and StoreList.objects.filter(serial=daghi).count() == 0:
                    autodaghi = 0
                if autodaghi == 1 and daghi:

                    dgi = 2
                    store = StoreList.objects.get(serial=daghi)
                    store.getuser_id = request.user.owner.id
                    if store.status_id == 5:
                        store.status_id = 6
                        store.save()
                        StoreHistory.objects.create(store_id=store.id, owner_id=request.user.owner.id,
                                                    information="ارسال قطعه داغی صفحه کلید ",
                                                    status_id=6,
                                                    description=f' به پشتیبان  {store.getuser} (تیکت {ticket.id})')
                        work.serialpinpaddaghi = store.serial
                        work.save()

                    else:
                        owner = Owner.objects.get(id=request.user.owner.id)
                        if _isdaghimaster or _isdaghipinpad:
                            ticket.isdaghi = True
                            owner.daghimande = True
                            owner.save()
                else:
                    owner = Owner.objects.get(id=request.user.owner.id)
                    if _isdaghimaster or _isdaghipinpad:
                        ticket.isdaghi = True
                        owner.daghimande = True
                        owner.save()

            if _isdaghipinpad and cpinpadid == '0':
                pumpno = Pump.objects.get(id=ticket.Pump_id)
                daghi = pumpno.pinpad
                pumpno.pinpad = ""
                pumpno.save()
                if autodaghi == 1 and StoreList.objects.filter(serial=daghi).count() == 0:
                    autodaghi = 0
                if autodaghi == 1 and daghi:

                    dgi = 2
                    store = StoreList.objects.get(serial=daghi)
                    store.getuser_id = request.user.owner.id
                    if store.status_id == 5:
                        store.status_id = 6
                        store.save()
                        StoreHistory.objects.create(store_id=store.id, owner_id=request.user.owner.id,
                                                    information="ارسال قطعه داغی صفحه کلید ",
                                                    status_id=6,
                                                    description=f' به پشتیبان  {store.getuser} (تیکت {ticket.id})')
                        work.serialpinpaddaghi = store.serial
                        work.save()

                    else:
                        owner = Owner.objects.get(id=request.user.owner.id)
                        if _isdaghimaster or _isdaghipinpad:
                            ticket.isdaghi = True
                            owner.daghimande = True
                            owner.save()
                else:
                    owner = Owner.objects.get(id=request.user.owner.id)
                    if _isdaghimaster or _isdaghipinpad:
                        ticket.isdaghi = True
                        owner.daghimande = True
                        owner.save()
            if cmasterid != '0':
                store = StoreList.objects.get(id=cmasterid)
                store.status_id = 5
                store.pump_id = ticket.Pump_id
                store.save()
                pumpno = Pump.objects.get(id=ticket.Pump_id)
                daghi = pumpno.master
                pumpcheck(store.serial, 1)
                pumpno.master = store.serial
                ticket.serialmaster = store.serial
                pumpno.active = True
                pumpno.actived = True
                pumpno.status_id = 1
                pumpno.save()
                StoreHistory.objects.create(store_id=store.id, owner_id=request.user.owner.id,
                                            information="ارسال قطعه از پشتیبان  " + str(store.getuser),
                                            status_id=5,
                                            description=f' تخصیص به جایگاه  {store.pump.gs.name} (تیکت {ticket.id})')

                if autodaghi == 1 and daghi:
                    dgi = 1
                    store = StoreList.objects.get(serial=daghi)
                    if store.status_id == 5:
                        store.status_id = 6
                        store.getuser_id = request.user.owner.id
                        store.save()
                        StoreHistory.objects.create(store_id=store.id, owner_id=request.user.owner.id,
                                                    information="ارسال قطعه داغی کارتخوان ",
                                                    status_id=6,
                                                    description=f' به پشتیبان  {store.getuser} (تیکت {ticket.id})')
                        work.serialmasterdaghi = store.serial
                        work.save()
                    else:
                        owner = Owner.objects.get(id=request.user.owner.id)
                        if _isdaghimaster or _isdaghipinpad:
                            ticket.isdaghi = True
                            owner.daghimande = True
                            owner.save()
                else:
                    owner = Owner.objects.get(id=request.user.owner.id)
                    if _isdaghimaster or _isdaghipinpad:
                        ticket.isdaghi = True
                        owner.daghimande = True
                        owner.save()

            if _isdaghimaster and cmasterid == '0':
                pumpno = Pump.objects.get(id=ticket.Pump_id)
                daghi = pumpno.master
                pumpno.master = ""
                pumpno.save()

                if autodaghi == 1 and daghi:
                    dgi = 1
                    store = StoreList.objects.get(serial=daghi)
                    if store.status_id == 5:
                        store.status_id = 6
                        store.getuser_id = request.user.owner.id
                        store.save()
                        StoreHistory.objects.create(store_id=store.id, owner_id=request.user.owner.id,
                                                    information="ارسال قطعه داغی کارتخوان ",
                                                    status_id=6,
                                                    description=f' به پشتیبان  {store.getuser} (تیکت {ticket.id})')
                        work.serialmasterdaghi = store.serial
                        work.save()
                    else:
                        owner = Owner.objects.get(id=request.user.owner.id)
                        if _isdaghimaster or _isdaghipinpad:
                            ticket.isdaghi = True
                            owner.daghimande = True
                            owner.save()
                else:
                    owner = Owner.objects.get(id=request.user.owner.id)
                    if _isdaghimaster or _isdaghipinpad:
                        ticket.isdaghi = True
                        owner.daghimande = True
                        owner.save()
            if _nocloseafteraccept:
                ticket.descriptionactioner = desc
                ticket.organization_id = 1
            elif _closebysmart:
                ticket.descriptionactioner = 'برای این تیکت داغی ثبت نشده و باید رئیس سامانه تایید کند'
                ticket.organization_id = 5
            elif _ipclog and int(rpid) in [2, 4, 57, 58, 59, 60] and _ipclog.dashboard_version == '1.02.101701':
                ticket.descriptionactioner = "ارسال به تست و راه اندازی جهت پیکربندی"
                ticket.organization_id = 3
                ticket.failure_id = '1045'
            else:

                ticket.descriptionactioner = 'تیکت بسته شد' + str(desc)
                ticket.status_id = 2
            ticket.actioner_id = request.user.owner.id
            ticket.close_shamsi_year = jdatetime.datetime.now().year
            if len(str(jdatetime.datetime.now().month)) == 1:
                month = '0' + str(jdatetime.datetime.now().month)
            else:
                month = jdatetime.datetime.now().month
            ticket.close_shamsi_month = month
            if len(str(jdatetime.datetime.now().day)) == 1:
                day = '0' + str(jdatetime.datetime.now().day)
            else:
                day = jdatetime.datetime.now().day
            ticket.close_shamsi_day = day
            ticket.closedate = datetime.datetime.now()
            ticket.close_shamsi_date = str(jdatetime.datetime.now().year) + "-" + str(month) + "-" + str(day)

            if ticket.closedate:
                try:
                    ticket.timeaction = (ticket.closedate - ticket.create).days
                    ticket.save()
                    if ticket.failure_id in [1049, 1046, 1053]:
                        a = Ticket.objects.create(owner_id=request.user.owner.id, status_id=1, organization_id=2,
                                                  gs_id=ticket.gs_id,
                                                  failure_id=1078, is_system=True)
                        Workflow.objects.create(ticket_id=a.id, user_id=request.user.owner.id,
                                                description='این تیکت  بصورت سیستمی ایجاد شده است ',
                                                organization_id=2, failure_id=1078)
                        if ticket.gs.iscoding:
                            a = Ticket.objects.create(owner_id=request.user.owner.id, status_id=1, organization_id=2,
                                                      gs_id=ticket.gs_id,
                                                      failure_id=1079, is_system=True)
                            Workflow.objects.create(ticket_id=a.id, user_id=request.user.owner.id,
                                                    description='این تیکت  بصورت سیستمی ایجاد شده است ',
                                                    organization_id=2, failure_id=1079)
                except:
                    return JsonResponse({"message": 'success', 'dgi': dgi})

            return JsonResponse({"message": 'success', 'dgi': dgi})


class getforwardticket(APIView):
    permission_classes = [IsAuthenticated, CloseTicketOwnerPermission]

    def post(self, request):
        _role = request.user.owner.role.role
        _roleid = zoneorarea(request)
        if request.method == 'POST':
            isdel = 0
            obj = request.POST.get('obj')
            erjaunitid = request.POST.get('erjaunitId')
            erjainfoid = request.POST.get('erjainfoId')
            failureid = request.POST.get('failureid')
            foryat = request.POST.get('foryat')
            sms = request.POST.get('sms')

            lat = request.POST.get('lat')
            lang = request.POST.get('lang')
            rpid2 = request.POST.get('rpId2')
            _ticket = Ticket.objects.get(id=obj)
            if _ticket.failure_id != int(failureid):
                _failure = FailureSub.objects.get(id=int(failureid))
                if _failure.ischange:
                    return JsonResponse(
                        {"message": 'امکات تغییر شرح خرابی انتخابی نیست ، برای این شرح باید تیکت جدید ثبت کنید'})

            if _ticket.usererja and _ticket.usererja == request.user.owner.id:
                ticket = _ticket
            else:
                ticket = Ticket.object_role.c_gs(request, 0).get(id=obj)
            erjainfoid = checkxss(erjainfoid)
            if request.user.owner.role_id == 2:
                workcount = Workflow.objects.filter(ticket_id=obj, user_id=request.user.id,
                                                    user__owner__role_id=2).count()
                if workcount == 5 or workcount == 10 or workcount == 15:
                    NegativeScore.create_score(score=1, owner=request.user.owner.id, status=str(obj))
                if workcount == 9 or workcount == 14 or workcount == 19:
                    Workflow.objects.create(ticket_id=obj, organization_id=5,
                                            description=' بعلت ارجاع متعدد  ، نیاز به بررسی توسط رئیس سامانه میباشد (' + str(
                                                erjainfoid) + ")",
                                            failure_id=failureid, lat=lat, lang=lang,
                                            user_id=request.user.id)
                    ticket.organization_id = 5

                    ticket.save()
                    messages.warning(request,
                                     'با توجه به اینکه بعد از ارجاعات متعدد تیکت به نتیجه نرسیده به رئیس سامانه ارجاع شد')
                    return redirect('base:CrudeTickets')

            self.check_object_permissions(request, ticket)
            ticket.organization_id = erjaunitid

            if request.user.owner.refrence_id == 1:
                ticket.foryat = int(foryat)

                if int(foryat) == 3 and erjaunitid == '1':
                    gsmobail = GsList.objects.filter(gs_id=ticket.gs.id, owner__role__role='tek')[:1]
                    for item in gsmobail:
                        mobail = item.owner.mobail
                    message = '''
                     سلام ،  یک تیکت با اولویت  آنی به شما ارجاع شده لطفا فورا بررسی بفرمایید. 
                    شرکت ملی پخش فرآورده های نفتی ایران
                                    '''.format(param1=123)
                    try:
                        SendOTP2(mobail, message, 0, 0, 0)
                    except:
                        print('ok')
            if not ticket.is_system:
                ticket.failure_id = failureid
            if rpid2 != '0':
                info = Reply.objects.get(id=int(rpid2))
                desc = info.info + str(erjainfoid)
            else:
                desc = checkxss(erjainfoid)
            ticket.islock = False
            ticket.save()
            Workflow.objects.create(ticket_id=obj, organization_id=erjaunitid, description=desc,
                                    failure_id=failureid, lat=lat, lang=lang,
                                    user_id=request.user.id)

            a = ticket.organization.name
            if sms == "on":
                gsmobail = GsList.objects.filter(gs_id=ticket.gs.id, owner__role__role='tek')[:1]
                for item in gsmobail:
                    mobail = item.owner.mobail
                message = desc.format(param1=123)
                try:
                    SendOTP2(mobail, message, 0, 0, 0)
                except:
                    print('ok')

            if erjaunitid == '5':
                gsmobail = Owner.objects.filter(zone_id=ticket.gs.area.zone.id, refrence_id=1)[:1]
                for item in gsmobail:
                    mobail = item.mobail
                message = '''
                 سلام ،  یک تیکت  به شما ارجاع شده لطفا  بررسی بفرمایید. 
                شرکت ملی پخش فرآورده های نفتی ایران
                                '''.format(param1=123)
                try:
                    SendOTP2(mobail, message, 0, 0, 0)
                except:
                    print('ok')
            fail = str(ticket.failure.failurecategory.info) + " | " + str(ticket.failure.info)
            if request.user.owner.role.role in ['test', 'fani', 'setad']:
                isdel = 1
        return JsonResponse({"message": 'success', 'erjaunitId': erjaunitid, 'name': a, 'fail': fail, 'isdel': isdel})


class UserSave(APIView):
    permission_classes = [IsAuthenticated, OwnerCreatePermission]

    @transaction.atomic
    def post(self, request):
        thislist = []
        id_name = request.POST.get('id_name')
        id_name = checkxss(id_name)
        id_codemeli = request.POST.get('id_codemeli')
        id_codemeli = checkxss(id_codemeli)
        id_codemeli = checknumber(id_codemeli)
        password1 = request.POST.get('Password1')
        id_lname = request.POST.get('id_lname')
        id_lname = checkxss(id_lname)
        id_mobail = request.POST.get('id_mobail')
        id_mobail = checkxss(id_mobail)
        id_mobail = checknumber(id_mobail)
        userzone = request.POST.get('userZone')
        userarea = request.POST.get('userArea')
        userstorage = request.POST.get('userStorage')
        mylad = request.POST.get('Mylad')
        semat = request.POST.get('semat')

        zone = '' if userzone == '0' else userzone
        area = '' if userarea == '0' else userarea
        if Owner.objects.filter(mobail=id_mobail, active=True).count() > 0:
            msg = 'این شماره همراه قبلا استفاده شده'
            return JsonResponse({"message": msg, 'mylist': thislist})

        if userstorage == '0' or len(userstorage) == 0:
            storage = ''
        else:
            storage = userstorage
            zone = Storage.objects.get(id=int(userstorage)).zone_id

        if request.user.owner.role.role == 'zone':
            zone = request.user.owner.zone_id
        try:
            user = User.objects.create_user(id_codemeli, 'aa@tt.com')
            user.set_password(checkxss(password1))
            user.last_name = checkxss(id_lname)
            user.first_name = checkxss(id_name)
            user.save()
        except IntegrityError:
            msg = 'این یوزر قبلا ایجاد شده'
            return JsonResponse({"message": msg, 'mylist': thislist})
        try:
            a = Owner.objects.create(user_id=user.id, name=checkxss(id_name), lname=checkxss(id_lname),
                                     mobail=checkxss(id_mobail),
                                     codemeli=checkxss(id_codemeli), zone_id=zone, area_id=area, role_id=mylad,
                                     storage_id=storage, active=True,
                                     refrence_id=semat)
        except IntegrityError:
            msg = 'این نام کاربری قبلا ایجاد شده'
            return JsonResponse({"message": msg, 'mylist': thislist})
        except ValueError as e:
            msg = 'اطلاعات به درستی تکمیل نشده یا داده ها معتبر نمیباشد'
            return JsonResponse({"message": msg, 'mylist': thislist})
        add_to_log(request, 'ایجاد کاربر ' + str(checkxss(id_codemeli)), 0)

        thisdict = {

            "info": str(a.name) + ' ' + str(a.lname),
            "codemeli": a.codemeli,
            "role": a.role.name,
            "date": a.pdate(),
            "active": a.active,
            "roleid": a.role.role,

        }
        thislist.append(thisdict)
        msg = 'success'

        return JsonResponse({"message": msg, 'mylist': thislist})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addgsuser(request):
    thislist = []
    if request.method == 'POST':
        userid = request.POST.get('userid')
        mylist = request.POST.get('strIds')
        x = mylist.split(',')
        for item in x:
            gsinfo = GsList.objects.create(gs_id=item, owner_id=userid)

            thisdict = {
                "id": gsinfo.id,
                "gsid": gsinfo.gs.gsid,
                "name": gsinfo.gs.name,
                "area": gsinfo.gs.area.name,

            }
            add_to_log(request, 'اضافه کرن جایگاه به کاربر', gsinfo.gs.id)
            thislist.append(thisdict)
    return JsonResponse({"message": "success", 'mylist': thislist})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def removegsuser(request):
    thislist = []
    if request.method == 'POST':
        mylist = request.POST.get('strIds')
        x = mylist.split(',')
        for item in x:
            gsinfo = GsList.objects.get(id=item)

            thisdict = {
                "id": gsinfo.gs.id,
                "gsid": gsinfo.gs.gsid,
                "name": gsinfo.gs.name,
                "area": gsinfo.gs.area.name,
            }
            gsinfo.delete()
            add_to_log(request, 'حذف جایگاه از کاربر ' + str(gsinfo.gs.gsid) + ' - ' + str(gsinfo.owner), gsinfo.gs.id)
            thislist.append(thisdict)
    return JsonResponse({"message": "success", 'mylist': thislist})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getroles(request):
    serializer = ZoneSerializer
    tedad = request.user.owner.ownerlist.count()
    if tedad > 1:
        zonez = OwnerZone.objects.filter(owner_id=request.user.owner.id)
    else:
        zonez = Zone.objects_limit.all()

    zlist = []
    for item in zonez:
        if tedad > 1:
            _id = item.zone.id
            _name = item.zone.name
        else:
            _id = item.id
            _name = item.name
        _dict = {
            'id': str(_id),
            'name': str(_name),
        }
        zlist.append(_dict)
    semats = Refrence.objects.all()
    _list = []
    semat = []
    for item in semats:
        _dict = {
            'id': item.id,
            'name': item.name,
        }
        semat.append(_dict)
    result = Role.objects.all()
    owner = Owner.objects.get(id=request.user.owner.id)
    n_role = owner.role_id
    n_zone = owner.zone_id
    n_semat = owner.refrence_id
    for item in result:
        _dict = {
            'id': item.id,
            'name': item.name,
        }
        _list.append(_dict)

    return JsonResponse(
        {'message': 'success', 'list': _list, 'n_role': n_role, 'n_semat': n_semat, 'semat': semat, 'n_zone': n_zone,
         'zlist': zlist, 'tedad': tedad})


@csrf_exempt
@require_POST
def move_pump_up(request):
    pump_id = request.POST.get('pump_id')
    try:
        pump = Pump.objects.get(id=pump_id)
        # پیدا کردن پمپ قبلی
        prev_pump = Pump.objects.filter(
            gs=pump.gs,
            sortnumber__lt=pump.sortnumber
        ).order_by('-sortnumber').first()

        if prev_pump:
            # جابجایی مقادیر sortnumber
            current_sort = pump.sortnumber
            pump.sortnumber = prev_pump.sortnumber
            prev_pump.sortnumber = current_sort
            pump.save()
            prev_pump.save()

            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'message': 'پمپی برای جابجایی یافت نشد'})
    except Pump.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'پمپ مورد نظر یافت نشد'})


@csrf_exempt
@require_POST
def move_pump_down(request):
    pump_id = request.POST.get('pump_id')
    try:
        pump = Pump.objects.get(id=pump_id)
        # پیدا کردن پمپ بعدی
        next_pump = Pump.objects.filter(
            gs=pump.gs,
            sortnumber__gt=pump.sortnumber
        ).order_by('sortnumber').first()

        if next_pump:
            # جابجایی مقادیر sortnumber
            current_sort = pump.sortnumber
            pump.sortnumber = next_pump.sortnumber
            next_pump.sortnumber = current_sort
            pump.save()
            next_pump.save()

            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'message': 'پمپی برای جابجایی یافت نشد'})
    except Pump.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'پمپ مورد نظر یافت نشد'})
