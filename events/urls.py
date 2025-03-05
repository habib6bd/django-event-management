from django.urls import path
from events.views import event_list, event_update, EventDeleteView, total_participants, filter_events, dashboard, EventDetailView,  EventCreateView, rsvped_events, rsvp_event

urlpatterns = [
    path('event-list/', event_list, name   ='event_list'),
    # path('create/', event_create, name='create_event'),
    path('event/create/', EventCreateView.as_view(), name='create_event'),
    path('update/<int:pk>/', event_update, name='event_update'),
    # path('delete/<int:pk>/', event_delete, name='event_delete'),
    path('event/<int:pk>/delete/', EventDeleteView.as_view(), name='event_delete'),
    path('total_participants/', total_participants, name='total_participants'),
    path('filter/', filter_events, name='filter_events'),
    path('organizer-dashboard/', dashboard, name='organizer-dashboard'),
    # path('events/<int:pk>/', event_detail, name='event_detail'),
    path('event/<int:pk>/', EventDetailView.as_view(), name='event_detail'),
    path('events/<int:pk>/rsvp/', rsvp_event, name='rsvp_event'), 
    path('participant-dashboard/', rsvped_events, name='participant-dashboard'),
]


