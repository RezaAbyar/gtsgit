from django.urls import path
from . import views
from base import autoexcel


app_name = 'cart'

urlpatterns = [
    path('', views.cartinsert, name='cartInsert'),
    path('postyafte/', views.postyafte, name='postyafte'),
    path('addpan/', views.addpan, name='addpan'),
    path('addPanpost/', views.addpanpost, name='addPanpost'),
    path('LostCardInfo/', views.cartview, name='LostCardInfo'),
    path('carttonahye/', views.carttonahye, name='carttonahye'),
    path('carttozone/', views.carttozone, name='carttozone'),
    path('carttomalek/', views.carttomalek, name='carttomalek'),
    path('carttogs/', views.carttogs, name='carttogs'),
    path('PanSearch/', views.pansearch, name='PanSearch'),
    path('AreaZone/', views.areazone, name='AreaZone'),
    path('AreaGS/', views.areags, name='AreaGS'),
    path('cartdaryaftings/', views.cartdaryaftings, name='cartdaryaftings'),
    path('getWorkflowCard/', views.getworkflowcard, name='getWorkflowCard'),
    path('SearchCard/', views.searchcard, name='SearchCard'),
    path('card_azad/', views.card_azad, name='card_azad'),
    path('getWorkflowCardAzad/', views.getworkflowcardazad, name='getWorkflowCardAzad'),
    path('import_excel/', views.import_excel, name='import_excel'),
    path('import_excel_card/', autoexcel.importexcelcard, name='import_excel_card'),
    path('addvin/', views.addvin, name='addvin'),
    path('CartToExcel/', autoexcel.carttoexcel, name='CartToExcel'),
    path('repcardexpire/', views.repcardexpire, name='repcardexpire'),
    path('repcardexpirearea/', views.repcardexpirearea, name='repcardexpirearea'),
    path('carttoemha/', views.carttoemha, name='carttoemha'),
    path('delcart/', views.delcart, name='delcart'),
    path('import_excel_baje/<int:_id>/', views.import_excel_baje, name='import_excel_baje'),
    path('pan-report/', views.pan_report, name='pan_report'),


]
