from django.urls import path
from events.views import event_list, event_update, event_delete, total_participants, filter_events, dashboard, event_detail,  event_create

urlpatterns = [
    path('event-list/', event_list, name   ='event_list'),
    path('create/', event_create, name='create_event'),
    path('update/<int:pk>/', event_update, name='event_update'),
    path('delete/<int:pk>/', event_delete, name='event_delete'),
    path('total_participants/', total_participants, name='total_participants'),
    path('filter/', filter_events, name='filter_events'),
    path('organizer-dashboard/', dashboard, name='organizer-dashboard'),
    path('events/<int:pk>/', event_detail, name='event_detail'),
]


