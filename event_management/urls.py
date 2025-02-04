from django.contrib import admin
from django.urls import path, include
from events import views
from debug_toolbar.toolbar import debug_toolbar_urls


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.event_list, name='event_list'),
    path('events/', include('events.urls')),
] + debug_toolbar_urls()
