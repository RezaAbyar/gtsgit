from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('gtsmgr/', admin.site.urls),
    path('', include('base.urls')),
    path('accounts/', include('accounts.urls')),
    path('cart/', include('cart.urls')),
    path('pay/', include('pay.urls')),
    path('api/', include('api.urls')),
    path('msg/', include('msg.urls')),
    path('sell/', include('sell.urls')),
    path('chart/', include('api.chart.urls')),
    path('cardapi/', include('api.urls_flutter')),
    path('lock/', include('lock.urls')),
    path('blog/', include('blog.urls')),
    path('visit/', include('visit.urls')),
    path('notification/', include('notification.urls')),
    path('bazrasnegar/', include('bazrasnegar.urls')),
    path('automation/', include('automation.urls')),
    path('pm/', include('pm.urls')),
    path('dashboard/', include('dashboard.urls')),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)