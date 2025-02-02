from django.urls import path
from . import views

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('create/', views.event_create, name='create_event'),
    path('update/<int:pk>/', views.event_update, name='event_update'),
    path('delete/<int:pk>/', views.event_delete, name='event_delete'),
    path('total_participants/', views.total_participants, name='total_participants'),
    path('filter/', views.filter_events, name='filter_events'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
