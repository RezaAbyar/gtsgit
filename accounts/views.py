import datetime
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from api.samplekey import encrypt2 as Encrypt, decrypt as Decrypt
from django.conf import settings
from django.db.models import F, Avg, Count, Sum, When, Case
from django.views.decorators.http import require_GET, require_POST
from base.models import Role, Permission, DefaultPermission, UserPermission, Owner, Refrence, AccessRole, Zone
from .logger import add_to_log
from .models import Logs
from django.http import HttpResponse, JsonResponse
from django.db import IntegrityError
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django.contrib import messages
from django.contrib.auth.models import User
from util import HOME_PAGE, DENY_PAGE
from django.views import View
import jdatetime
from base.views import createotp, SendOTP2
from base.models import Storage
from cart.views import checknumber
from .forms import RecoverForm, RolePermissionForm,BulkRolePermissionForm, MassPermissionAssignmentForm, PermissionFilterForm
import redis
from django.shortcuts import get_object_or_404


today = str(jdatetime.date.today())

today = today.replace("-", "/")
startdate = today[:8]
startdate = startdate + "01"


def recoverpassword(request):
    if request.method == 'POST':

        form = RecoverForm(request.POST)
        if form.is_valid():

            cd = form.cleaned_data

            try:
                owner = Owner.objects.get(codemeli=cd['code'])
                mobail = owner.mobail
                if Owner.objects.filter(mobail=mobail, active=True).count() > 1:
                    request.session['mobail'] = "0"
                    messages.error(request, 'این شماره موبایل برای دو کاربر ثبت شده است')
                    return redirect('base:login')

                request.session["mobail"] = mobail
                owner.numbersms += 1
                owner.save()
                try:
                    _test = (datetime.datetime.now() - owner.endsendsms).seconds
                    if _test >= 3600:
                        owner.lockedsendsms = False
                        owner.numbersms = 0
                        owner.save()
                except Exception as e:
                    pass
                if owner.lockedsendsms:
                    _test = (datetime.datetime.now() - owner.datelocked).seconds
                    if _test >= 3600:
                        owner.lockedsendsms = False
                        owner.numbersms = 0
                        owner.save()
                if owner.numbersms >= 3:
                    owner.lockedsendsms = True
                    owner.datelocked = datetime.datetime.now()
                    owner.save()
                    messages.error(request, 'امکان ارسال پیامک برای شما تا یک ساعت مسدود شد.')
                    return redirect('base:login')
                else:
                    createotp(owner.mobail, 2)
                    messages.success(request, 'کد اعتبار سنجی پیامک شد')

                return redirect('base:veryfi')
            except Owner.DoesNotExist:
                messages.error(request, 'اطلاعات وارد شده صحیح نمیباشد')
                return redirect('base:login')

        else:

            messages.error(request, 'اطلاعات وارد شده صحیح نمیباشد')
    return render(request, 'recover-password.html')


def checkmobailfa(request):
    owners = Owner.objects.all()
    for owner in owners:
        if owner.mobail and len(owner.mobail) == 10:
            owner.mobail = '0' + str(owner.mobail)
        if owner.mobail and len(owner.mobail) == 11:
            mobail = checknumber(owner.mobail)
            owner.mobail = mobail
            owner.save()
    return HttpResponse('ok')


class DefaultRole(View):
    def get(self, request):
        roles = Role.objects.all()
        return render(request, 'DefaultPermission.html', {'roles': roles})


class GetRole(View):
    def post(self, request):
        newlist = []
        if request.method == 'POST':
            newid = request.POST.get('id')
            for i in Permission.objects.all():
                try:
                    DefaultPermission.objects.create(role_id=newid, accessrole_id=2, permission_id=i.id,
                                                     unid=str(newid) + '-' + str(i.id))
                except IntegrityError:
                    pass
            result = DefaultPermission.objects.filter(role_id=newid)

            for item in result:
                mydict = {
                    'accessrole': item.accessrole.name,
                    'permission': item.permission.info,
                    'aid': item.accessrole.ename,
                }
                newlist.append(mydict)

        return JsonResponse({'message': 'success', 'list': newlist})


def change_password(request):
    owner_p = UserPermission.objects.filter(owner_id=request.user.owner.id)
    if owner_p.count() == 0:
        owner_p = DefaultPermission.objects.filter(role_id=request.user.owner.role_id,
                                                   semat_id=request.user.owner.refrence_id)

    formpermmision = {}
    for i in owner_p:
        formpermmision[i.permission.name] = i.accessrole.ename

    if request.method == 'POST':

        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            add_to_log(request, 'عملیات تغییر رمز ', 0)

            mobail = request.user.owner.mobail
            message = '''
                                 سلام ،  رمز عبور شما در سامانه GTS توسط {param1} تغییر کرد. 
            شرکت ملی پخش فرآورده های نفتی ایران
                                                '''.format(param1=request.user.owner.get_full_name())

            try:
                SendOTP2(mobail, message, request.user.owner.get_full_name(), 0, 0)
            except:
                print('ok')
            messages.success(request, 'پسورد شما با موفقیت تغییر کرد')
            return redirect(HOME_PAGE)
        else:
            messages.warning(request, 'شکست عملیات')
            return redirect('accounts:change')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change.html', {'form': form, 'formpermmision': formpermmision})


def password_change(request, id):
    owner_p = UserPermission.objects.filter(owner_id=request.user.owner.id)
    if owner_p.count() == 0:
        owner_p = DefaultPermission.objects.filter(role_id=request.user.owner.role_id,
                                                   semat_id=request.user.owner.refrence_id)
    ua = owner_p.get(permission__name='users')
    if ua.accessrole.ename != 'full':
        messages.warning(request, DENY_PAGE)
        return redirect(HOME_PAGE)
    formpermmision = {}
    for i in owner_p:
        formpermmision[i.permission.name] = i.accessrole.ename
    # --------------------------------------------------------------------------------------
    if len(str(id)) < 6:
        messages.warning(request, 'دسترسی غیر مجاز')
        return redirect(HOME_PAGE)
    id = Decrypt(id)
    user = User.objects.get(id=id)
    form = SetPasswordForm(user)
    if request.user.owner.role.role in ['mgr', 'setad', 'zone']:
        if request.user.owner.role.role == 'zone':
            if user.owner.zone_id != request.user.owner.zone_id:
                messages.warning(request, 'شما به این صفحه دسترسی ندارید')
                return redirect(HOME_PAGE)

        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                add_to_log(request, f'{user.username}عملیات تغییر رمز ', 0)
                mobail = user.owner.mobail
                message = '''
                                                 سلام ،  رمز عبور شما در سامانه GTS توسط {param1} تغییر کرد. 
                                        شرکت ملی پخش فرآورده های نفتی ایران                                 
                                                                '''.format(param1=request.user.owner.get_full_name())

                try:
                    SendOTP2(mobail, message, request.user.owner.get_full_name(), 0, 0)
                except:
                    print('ok')
                messages.success(request, "رمز عبور با موفقیت تغییر کرد")
                return redirect(HOME_PAGE)
            else:
                for error in list(form.errors.values()):
                    messages.warning(request, error)
    else:
        messages.warning(request, 'شما به این صفحه دسترسی ندارید')
    return render(request, 'change.html', {'form': form, 'formpermmision': formpermmision})


def myprofile(request):
    owner_p = UserPermission.objects.filter(owner_id=request.user.owner.id)
    if owner_p.count() == 0:
        owner_p = DefaultPermission.objects.filter(role_id=request.user.owner.role_id,
                                                   semat_id=request.user.owner.refrence_id)

    formpermmision = {}
    for i in owner_p:
        formpermmision[i.permission.name] = i.accessrole.ename
    owner = Owner.objects.get(id=request.user.owner.id)
    storages = Storage.objects.filter(active=True)
    storage = owner.defaultstorage
    if request.method == 'POST':
        reload = False
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        mobail = request.POST.get('mobail')
        isboarder = request.POST.get('isboarder')
        storage = request.POST.get('storage')

        mobail = checknumber(mobail)
        if mobail != owner.mobail:
            owner.mobail_ischeck = False
            reload = True
        colorpage = request.POST.get('colorpage')
        viewtickets = request.POST.get('viewtickets')
        owner.name = fname
        owner.lname = lname
        owner.mobail = mobail
        owner.colorpage = colorpage
        owner.isboarder = isboarder
        owner.defaultstorage = int(storage)
        owner.viewtickets = viewtickets
        owner.save()
        user = User.objects.get(id=owner.user.id)
        user.first_name = fname
        user.last_name = lname

        user.save()
        add_to_log(request, f' {user.username}ویرایش پروفایل ', 0)
        messages.success(request, 'پروفایل شما به درستی ویرایش شد')
        owner = Owner.objects.get(id=request.user.owner.id)
        if reload:
            createotp(mobail, 1)
            return redirect('base:veryfi')

    return render(request, 'myprofile.html',
                  {'owner': owner, 'formpermmision': formpermmision, 'storages': storages, 'storage': int(storage)})


def roles(request):
    owner_p = UserPermission.objects.filter(owner_id=request.user.owner.id)
    if owner_p.count() == 0:
        owner_p = DefaultPermission.objects.filter(role_id=request.user.owner.role_id,
                                                   semat_id=request.user.owner.refrence_id)
    ua = owner_p.get(permission__name='acroles')
    if ua.accessrole.ename == 'no':
        messages.warning(request, 'شما به این صفحه دسترسی ندارید')
        return redirect(HOME_PAGE)
    formpermmision = {}
    for i in owner_p:
        formpermmision[i.permission.name] = i.accessrole.ename
    # --------------------------------------------------------------------------------------
    # SendOTP('09111284942', '2161846736')
    roles = Role.objects.all()
    semats = Refrence.objects.all()

    if request.method == 'POST':
        rid = request.POST.get('role')
        sid = request.POST.get('semat')
        items = AccessRole.objects.all().order_by('id')
        DPS = DefaultPermission.objects.filter(role_id=rid, semat_id=sid).order_by('permission__cat_sort',
                                                                                   'permission__Sortper_id',
                                                                                   'id')

        for p in Permission.objects.all().order_by('id'):
            try:
                uniq = str(sid) + '-' + str(rid) + '-' + str(p.id)
                DefaultPermission.objects.create(permission_id=p.id, accessrole_id=5, semat_id=sid, role_id=rid,
                                                 unid=uniq)
            except IntegrityError:
                continue
        return render(request, 'permission/roles.html',
                      {'semats': semats, 'roles': roles, 'items': items, 'formpermmision': formpermmision, 'DPS': DPS,
                       'Rid': int(rid), 'Sid': int(sid)})
    return render(request, 'permission/roles.html',
                  {'semats': semats, 'roles': roles, 'formpermmision': formpermmision})


def adddefualtaccesslist(request):
    if request.method == 'POST':
        rid = request.POST.get('myrid')
        sid = request.POST.get('mysid')
        dps = DefaultPermission.objects.filter(role_id=rid, semat_id=sid).order_by('permission_id')

        for dp in dps:
            accessid = request.POST.get('acceess' + str(dp.id))
            if dp.accessrole_id != int(accessid):
                dp.ischange = True
            else:
                dp.ischange = False
            dp.accessrole_id = accessid
            dp.save()
            messages.success(request, 'تغییرات با موفقیت ذخیره شد')

        return redirect('accounts:Roles')


def remove_user_permission(request, id):
    result = UserPermission.objects.filter(owner_id=id)
    for item in result:
        item.delete()
    add_to_log(request, f' {id}حذف دسترسی های اختصاصی کاربر  ', 0)
    messages.info(request, 'دسترسی های اختصاصی این شخص حذف شد')
    return redirect('base:UserList')


def useraccess(request, id):
    owner_p = UserPermission.objects.filter(owner_id=request.user.owner.id)
    if owner_p.count() == 0:
        owner_p = DefaultPermission.objects.filter(role_id=request.user.owner.role_id,
                                                   semat_id=request.user.owner.refrence_id)
    ua = owner_p.get(permission__name='acusers')
    if ua.accessrole.ename == 'no':
        messages.warning(request, 'شما به این صفحه دسترسی ندارید')
        return redirect(HOME_PAGE)
    formpermmision = {}
    for i in owner_p:
        formpermmision[i.permission.name] = i.accessrole.ename
    # --------------------------------------------------------------------------------------

    if len(str(id)) < 6:
        messages.warning(request, 'دسترسی غیر مجاز')
        return redirect(HOME_PAGE)
    id = Decrypt(id)
    owner = Owner.objects.get(id=id)
    add_to_log(request, f' {owner.codemeli}مشاهده اعمال دسترسی های اختصاصی  ', 0)
    items = AccessRole.objects.all().order_by('id')

    if request.method == 'POST':
        if request.user.owner.role.role == 'zone':
            DPS = UserPermission.objects.filter(owner_id=id, permission__permit=1).order_by('permission_id')
        else:
            DPS = UserPermission.objects.filter(owner_id=id).order_by('permission_id')

        for dp in DPS:
            accessid = request.POST.get('acceess' + str(dp.id))
            dp.accessrole_id = accessid
            dp.save()
            add_to_log(request, f' {owner.codemeli}ذخیره اعمال دسترسی های اختصاصی  ', 0)
            messages.success(request, 'تغییرات با موفقیت ذخیره شد')
    if request.user.owner.role.role == 'zone':
        if owner.role.role == 'zone' and owner.refrence.id == 6:
            DPS = UserPermission.objects.filter(owner_id=id, permission__permit=1).order_by('permission__cat_sort',
                                                                                            'permission__Sortper_id',
                                                                                            'id')
            # UserPermission.objects.filter(owner_id=id, permission__permit=0).update(accessrole_id=5)
        else:
            messages.error(request, 'شما به این شخص دسترسی ندارید')
            return redirect('base:home')

    else:
        DPS = UserPermission.objects.filter(owner_id=id).order_by('permission__cat_sort', 'permission__Sortper_id',
                                                                  'id')

    for p in DefaultPermission.objects.filter(role_id=owner.role.id, semat_id=owner.refrence_id).order_by('id'):
        try:
            uniq = str(owner.id) + '-' + str(p.permission_id)
            UserPermission.objects.create(permission_id=p.permission_id, accessrole_id=p.accessrole_id, owner_id=id,
                                          unid=uniq)
        except IntegrityError:
            continue
    return render(request, 'permission/useraccess.html',
                  {'items': items, 'DPS': DPS, 'owner': owner, 'formpermmision': formpermmision})


def profileitems(request):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        owner = Owner.objects.get(id=request.user.owner.id)
        owner.shomare = testprofileitems(request.POST.get('shomare'))
        owner.sarfasl = testprofileitems(request.POST.get('sarfasl'))
        owner.onvan = testprofileitems(request.POST.get('onvan'))
        owner.zoner = testprofileitems(request.POST.get('zoner'))
        owner.arear = testprofileitems(request.POST.get('arear'))
        owner.gsid = testprofileitems(request.POST.get('gsid'))
        owner.gsname = testprofileitems(request.POST.get('gsname'))
        owner.nazel = testprofileitems(request.POST.get('shnazel'))
        owner.product = testprofileitems(request.POST.get('product'))
        owner.createtime = testprofileitems(request.POST.get('createtime'))
        owner.creator = testprofileitems(request.POST.get('creator'))
        owner.save()
        add_to_log(request, f' {owner.codemeli}ذخیره شخصی سازی آیتم های تیکت ', 0)
        messages.success(request, 'عملیات با موفقیت انجام شد.')
        return redirect(url)


def testprofileitems(value):
    if value == 'on':
        value = True
    else:
        value = False
    return value


def userlogs(request):
    owner_p = UserPermission.objects.filter(owner_id=request.user.owner.id)
    if owner_p.count() == 0:
        owner_p = DefaultPermission.objects.filter(role_id=request.user.owner.role_id,
                                                   semat_id=request.user.owner.refrence_id)
    ua = owner_p.get(permission__name='userlog')
    if ua.accessrole.ename == 'no':
        messages.warning(request, 'شما به این صفحه دسترسی ندارید')
        return redirect('base:home')
    formpermmision = {}
    for i in owner_p:
        formpermmision[i.permission.name] = i.accessrole.ename
    # --------------------------------------------------------------------------------------
    gss = None
    logs = None
    az = startdate
    ta = today
    if request.user.owner.role.role == 'zone':
        gss = Owner.objects.filter(active=True, zone_id=request.user.owner.zone_id)
    if request.user.owner.role.role in ['mgr', 'setad']:
        gss = Owner.objects.filter(active=True)
    if request.method == 'POST':
        mdate = request.POST.get('select')
        mdate2 = request.POST.get('select2')
        cd = request.POST.get('search')
        az = mdate
        ta = mdate2
        mdate = mdate.replace("/", '-')
        mdate2 = mdate2.replace("/", '-')
        mdate = mdate.split("-")
        mdate2 = mdate2.split("-")
        ownerid = request.POST.get('select3')
        tarikh = jdatetime.date(day=int(mdate[2]), month=int(mdate[1]), year=int(mdate[0])).togregorian()
        tarikhto = jdatetime.date(day=int(mdate2[2]), month=int(mdate2[1]), year=int(mdate2[0])).togregorian()
        tarikh = str(tarikh) + " 00:00:00"
        tarikhto = str(tarikhto) + " 23:59:59"
        if ownerid == '0':
            add_to_log(request, 'مشاهده رویداد کاربران ', 0)
        else:
            owner = Owner.objects.get(id=int(ownerid))
            add_to_log(request, f' مشاهده رویداد کاربر  {owner.name}  {owner.lname}', 0)
        if request.user.owner.role.role == 'zone':
            if ownerid == '0':
                logs = Logs.objects.filter(owner__zone_id=request.user.owner.zone_id, parametr1__icontains=cd)
            else:
                logs = Logs.objects.filter(owner_id=int(ownerid), owner__zone_id=request.user.owner.zone_id,
                                           parametr1__icontains=cd)
        if request.user.owner.role.role in ['setad', 'mgr']:
            if ownerid == '0':
                logs = Logs.objects.filter(parametr1__icontains=cd)
            else:
                logs = Logs.objects.filter(owner_id=int(ownerid), parametr1__icontains=cd)
        _list = logs.filter(create__gte=tarikh, create__lte=tarikhto).order_by('-create')
        return render(request, 'userlogs.html',
                      {'list': _list, 'mdate': mdate, 'mdate2': mdate2, 'gss': gss, 'ownerid': int(ownerid),
                       'formpermmision': formpermmision, 'az': az, 'ta': ta})
    return render(request, 'userlogs.html',
                  {'formpermmision': formpermmision, 'gss': gss, 'az': az, 'ta': ta})


def usergroupnemodar(request):
    owner_p = UserPermission.objects.filter(owner_id=request.user.owner.id)
    if owner_p.count() == 0:
        owner_p = DefaultPermission.objects.filter(role_id=request.user.owner.role_id,
                                                   semat_id=request.user.owner.refrence_id)
    ua = owner_p.get(permission__name='userlog')
    if ua.accessrole.ename == 'no':
        messages.warning(request, 'شما به این صفحه دسترسی ندارید')
        return redirect('base:home')
    formpermmision = {}
    for i in owner_p:
        formpermmision[i.permission.name] = i.accessrole.ename
    # --------------------------------------------------------------------------------------
    refs = Refrence.objects.all()
    if request.method == 'POST':
        add_to_log(request, 'مشاهده نمودار رویداد کاربران ', 0)
        mdate = request.POST.get('select')
        mdate2 = request.POST.get('select2')
        az = mdate
        ta = mdate2
        mdate = mdate.replace("/", '-')
        mdate2 = mdate2.replace("/", '-')
        mdate = mdate.split("-")
        mdate2 = mdate2.split("-")
        ownerid = request.POST.get('select3')
        tarikh = jdatetime.date(day=int(mdate[2]), month=int(mdate[1]), year=int(mdate[0])).togregorian()
        tarikhto = jdatetime.date(day=int(mdate2[2]), month=int(mdate2[1]), year=int(mdate2[0])).togregorian()
        tarikh = str(tarikh) + " 00:00:00"
        tarikhto = str(tarikhto) + " 23:59:59"
        if int(ownerid) == 0:
            _list = Logs.objects.values('owner__role__name', 'owner__refrence__name').filter(
                owner__zone_id=request.user.owner.zone_id, create__gte=tarikh, create__lte=tarikhto).annotate(
                count=Count('id'))
        else:
            _list = Logs.objects.values('owner__codemeli', 'owner__name', 'owner__lname').filter(
                owner__zone_id=request.user.owner.zone_id, owner__refrence_id=int(ownerid), create__gte=tarikh,
                create__lte=tarikhto).annotate(count=Count('id'))

        return render(request, 'nemodar/usergroupnemodar.html',
                      {'list': _list, 'mdate': mdate, 'mdate2': mdate2, 'refs': refs, 'ownerid': int(ownerid),
                       'formpermmision': formpermmision, 'az': az, 'ta': ta})
    return render(request, 'nemodar/usergroupnemodar.html', {'formpermmision': formpermmision, 'refs': refs})


def reportuser(request):
    owner_p = UserPermission.objects.filter(owner_id=request.user.owner.id)
    if owner_p.count() == 0:
        owner_p = DefaultPermission.objects.filter(role_id=request.user.owner.role_id,
                                                   semat_id=request.user.owner.refrence_id)
    ua = owner_p.get(permission__name='users')
    if ua.accessrole.ename == 'no':
        messages.warning(request, 'شما به این صفحه دسترسی ندارید')
        return redirect('base:home')
    formpermmision = {}
    for i in owner_p:
        formpermmision[i.permission.name] = i.accessrole.ename
    # --------------------------------------------------------------------------------------
    zones = None
    if request.user.owner.role.role in ['mgr', 'setad']:
        zones = Zone.objects.all()
    elif request.user.owner.role.role == 'zone':
        zones = Zone.objects.filter(id=request.user.owner.zone.id)
    result = []
    for zone in zones:
        _list = Owner.objects.filter(active=True, zone_id=zone.id)
        dict = {
            'name': zone.name,
            'tedad': len(_list)

        }
        result.append(dict)
    return render(request, 'repoeruser.html', {'list': result, })


def access_management_view(request):
    # بررسی دسترسی کاربر
    owner_p = UserPermission.objects.filter(owner_id=request.user.owner.id)
    if owner_p.count() == 0:
        owner_p = DefaultPermission.objects.filter(
            role_id=request.user.owner.role_id,
            semat_id=request.user.owner.refrence_id
        )

    try:
        ua = owner_p.get(permission__name='acroles')
        if ua.accessrole.ename == 'no':
            messages.warning(request, 'شما به این صفحه دسترسی ندارید')
            return redirect(HOME_PAGE)
    except:
        messages.warning(request, 'شما به این صفحه دسترسی ندارید')
        return redirect(HOME_PAGE)

    # فرم فیلتر
    filter_form = PermissionFilterForm(request.GET or None)
    permissions = Permission.objects.all()

    # اعمال فیلترها
    if filter_form.is_valid():
        role = filter_form.cleaned_data.get('role')
        semat = filter_form.cleaned_data.get('semat')

        if role:
            permissions = permissions.filter(defaultpermission__role=role)
        if semat:
            permissions = permissions.filter(defaultpermission__semat=semat)

    # فرم دسترسی گروهی
    mass_form = MassPermissionAssignmentForm(request.POST or None)

    if request.method == 'POST' and mass_form.is_valid():
        roles = mass_form.cleaned_data['roles']
        references = mass_form.cleaned_data['references']
        permissions = mass_form.cleaned_data['permissions']
        access_level = mass_form.cleaned_data['access_level']

        try:
            created_count = 0
            for role_id in roles:
                for ref_id in references:
                    for perm_id in permissions:
                        uniq = f"{ref_id}-{role_id}-{perm_id}"
                        if not DefaultPermission.objects.filter(unid=uniq).exists():
                            DefaultPermission.objects.create(
                                role_id=role_id,
                                semat_id=ref_id,
                                accessrole_id=access_level,
                                permission_id=perm_id,
                                unid=uniq
                            )
                            created_count += 1

            messages.success(request, f'{created_count} دسترسی با موفقیت ایجاد شد')
            return redirect('access_management')

        except IntegrityError:
            messages.error(request, 'خطا در ایجاد دسترسی‌ها')

    context = {
        'filter_form': filter_form,
        'mass_form': mass_form,
        'permissions': permissions,
        'roles': Role.objects.all(),
        'references': Refrence.objects.all(),
        'access_roles': AccessRole.objects.all(),
    }

    return render(request, 'access_management.html', context)


def edit_permission_view(request, permission_id):
    # بررسی دسترسی کاربر (مشابه بالا)

    permission = get_object_or_404(Permission, id=permission_id)
    default_permissions = DefaultPermission.objects.filter(permission=permission)

    if request.method == 'POST':
        for dp in default_permissions:
            field_name = f"access_{dp.id}"
            access_role_id = request.POST.get(field_name)
            if access_role_id:
                dp.accessrole_id = access_role_id
                dp.save()

        messages.success(request, 'دسترسی‌ها با موفقیت به‌روزرسانی شدند')
        return redirect('access_management')

    context = {
        'permission': permission,
        'default_permissions': default_permissions,
        'access_roles': AccessRole.objects.all(),
    }

    return render(request, 'edit_permission.html', context)