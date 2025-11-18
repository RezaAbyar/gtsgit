from django.urls import path
from . import api


app_name = 'base'

urlpatterns = [
    path('showmalek/', api.showmalek, name='showmalek'),
    path('SaveUsr/', api.saveusr, name='SaveUsr'),
    path('GetRole/<int:id>/', api.getrole, name='GetRole'),
    path('SaveEditUsr/', api.saveeditusr, name='SaveEditUsr'),
    path('SaveAddGs/', api.saveaddgs, name='SaveAddGs'),
    path('getNazel/', api.getnazel, name='getNazel'),
    path('SaveNazel/', api.SaveNazel.as_view(), name='SaveNazel'),
    path('subFailure/', api.subfailure, name='subFailure'),
    path('loadNazel/', api.loadnazel, name='loadNazel'),
    path('getWorkflow/', api.getworkflow, name='getWorkflow'),
    path('catFailure/', api.CatFailure.as_view(), name='catFailure'),
    path('catFailureedit/', api.CatFailureEdit.as_view(), name='catFailureedit'),
    path('closeTicket/', api.closeticket, name='closeTicket'),
    path('getForward/', api.getforward, name='getForward'),
    path('getReplyischange/', api.getreplyischange, name='getReplyischange'),
    path('getCloseTicket/', api.GetCloseTicket.as_view(), name='getCloseTicket'),
    path('getForwardTicket/', api.getforwardticket.as_view(), name='getForwardTicket'),
    path('UserSave/', api.UserSave.as_view(), name='UserSave'),
    path('AddGSUSER/', api.addgsuser, name='AddGSUSER'),
    path('RemoveGSUSER/', api.removegsuser, name='RemoveGSUSER'),
    path('getRoles/', api.getroles, name='getRoles'),
    path('move-pump-up/', api.move_pump_up, name='move_pump_up'),
    path('move-pump-down/', api.move_pump_down, name='move_pump_down'),

]