from django.db import models


class RoleeManager(models.Manager):

    def c_gs(self, request, _id):
        if request.user.owner.role.role == 'gs':
            return self.filter(gs__gsowner__owner_id=request.user.owner.id)
        if request.user.owner.role.role == 'tek' and request.user.owner.refrence_id != 8:
            return self.filter(gs__gsowner__owner_id=request.user.owner.id)
        if request.user.owner.role.role == 'area':
            return self.filter(gs__area_id=request.user.owner.area_id)
        if request.user.owner.role.role in ['zone', 'engin']:
            return self.filter(gs__area__zone_id=request.user.owner.zone_id)
        if _id == 0 and request.user.owner.role.role == 'tek' and request.user.owner.refrence_id == 8:
            return self.filter(gs__gsowner__owner_id=request.user.owner.id)
        if _id == 1 and request.user.owner.role.role == 'tek' and request.user.owner.refrence_id == 8:
            return self.filter(gs__area__zone_id=request.user.owner.zone_id)
        if request.user.owner.role.role in ['mgr', 'setad', 'fani', 'test']:
            return self.all()

    def c_gsmodel(self, request):

        if request.user.owner.role.role == 'tek':
            return self.filter(gsowner__owner_id=request.user.owner.id)
        if request.user.owner.role.role == 'gs':
            return self.filter(gsowner__owner_id=request.user.owner.id)
        if request.user.owner.role.role == 'area':
            return self.filter(area_id=request.user.owner.area_id)
        if request.user.owner.role.role in ['zone', 'engin']:
            return self.filter(area__zone_id=request.user.owner.zone_id)
        if request.user.owner.role.role in ['mgr', 'setad', 'fani', 'test']:
            return self.all()

    def c_ticket(self, request):
        if request.user.owner.role.role == 'gs':
            return self.filter(ticket__gs_id=request.user.owner.id)
        if request.user.owner.role.role == 'area':
            return self.filter(ticket__gs__area_id=request.user.owner.area_id)
        if request.user.owner.role.role in ['zone', 'engin']:
            return self.filter(ticket__gs__area__zone_id=request.user.owner.zone_id)
        if request.user.owner.role.role in ['mgr', 'setad', 'fani', 'test']:
            return self.all()

    def c_base(self, request):
        if request.user.owner.role.role in ['gs']:
            return self.filter(gs__gsowner__owner_id=request.user.owner.id)
        if request.user.owner.role.role == 'area':
            return self.filter(area_id=request.user.owner.area_id)
        if request.user.owner.role.role in ['zone', 'engin', 'tek']:
            return self.filter(zone_id=request.user.owner.zone_id)
        if request.user.owner.role.role in ['mgr', 'setad', 'fani', 'test']:
            return self.all()

    def c_me(self, request):

        if request.user.owner.refrence_id in [4, 8, 28]:
            return self.filter(gs__gsowner__owner_id=request.user.owner.id)
        elif request.user.owner.refrence_id in [1]:
            return self.filter(gs__area__zone_id=request.user.owner.zone_id, organization_id=5)
        elif request.user.owner.refrence_id == 4:
            return self.filter(gs__area_id=request.user.owner.area_id, organization_id=7)
        elif request.user.owner.refrence_id in [7, 9]:
            return self.filter(gs__gsowner__owner_id=request.user.owner.id)
        elif request.user.owner.refrence_id in [16]:
            return self.filter(gs__area__zone_id=request.user.owner.zone_id, organization__organiztion='engin')
        elif request.user.owner.refrence_id in [27]:
            return self.filter(gs__area__zone_id=request.user.owner.zone_id)
        else:
            return self.filter(gs__area__zone_id=request.user.owner.zone_id)

    def c_work_me(self, request):
        if request.user.owner.refrence_id in [4, 8]:
            return self.filter(ticket__gs__gsowner__owner_id=request.user.owner.id)
        elif request.user.owner.refrence_id == 1:
            return self.filter(ticket__gs__area__zone_id=request.user.owner.zone_id, organization_id=5)
        elif request.user.owner.refrence_id == 4:
            return self.filter(ticket__gs__area_id=request.user.owner.area_id, organization_id=7)
        elif request.user.owner.refrence_id in [7, 9]:
            return self.filter(ticket__gs__gsowner__owner_id=request.user.owner.id)
        else:
            return self.filter(ticket__gs__area__zone_id=request.user.owner.zone_id)

    def c_owner(self, request):

        if request.user.owner.role.role == 'tek':
            return self.filter(area_id=0)
        if request.user.owner.role.role == 'gs':
            return self.filter(area_id=0)
        if request.user.owner.role.role == 'area':
            return self.filter(area_id=request.user.owner.area_id)
        if request.user.owner.role.role in ['zone', 'engin']:
            return self.filter(zone_id=request.user.owner.zone_id)
        if request.user.owner.role.role in ['mgr', 'setad', 'fani', 'test']:
            return self.all()
