from django.urls import path
from . import views
from .views import WordTemplateListView, WordTemplateCreateView, WordTemplateUpdateView, WordTemplateDeleteView

app_name = 'automation'

urlpatterns = [
    path('inbox/', views.inbox, name='inbox'),
    path('sent/', views.sent_messages, name='sent'),
    path('compose/', views.compose, name='compose'),
    path('compose/<int:parent_id>/', views.compose, name='compose_reply'),
    path('message/<int:message_id>/', views.message_detail, name='message_detail'),
    path('message/<int:message_id>/view/', views.image_viewer, name='image_viewer'),
    path('message/<int:message_id>/view/<int:page_number>/', views.image_viewer, name='image_viewer_page'),
    path('reports/<int:message_id>/read/', views.read_reports, name='read_reports'),
    path('word-templates/', WordTemplateListView.as_view(), name='word_template_list'),
    path('word-templates/create/', WordTemplateCreateView.as_view(), name='word_template_create'),
    path('word-templates/<int:pk>/edit/', WordTemplateUpdateView.as_view(), name='word_template_update'),
    path('word-templates/<int:pk>/delete/', WordTemplateDeleteView.as_view(), name='word_template_delete'),
]