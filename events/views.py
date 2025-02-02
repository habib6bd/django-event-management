from django.shortcuts import render, get_object_or_404, redirect
from .models import Event, Category, Participant
from .forms import EventForm
from django.db.models import Count
from django.utils import timezone

# List Events with optimized queries
def event_list(request):
    category_id = request.GET.get('category')
    categories = Category.objects.all()
    
    if category_id:
        events = Event.objects.filter(category_id=category_id)
    else:
        events = Event.objects.all()

    context = {
        'categories': categories,
        'events': events,
        'selected_category': int(category_id) if category_id else None,
    }
    return render(request, 'events/event_list.html', context)
# Create Event
def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('event_list')
    else:
        form = EventForm()
    return render(request, 'events/event_form.html', {'form': form})

# Update Event
def event_update(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('event_list')
    else:
        form = EventForm(instance=event)
    return render(request, 'events/event_form.html', {'form': form})

# Delete Event
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        event.delete()
        return redirect('event_list')
    return render(request, 'events/event_confirm_delete.html', {'event': event})

def total_participants(request):
    total = Participant.objects.aggregate(total=Count('id'))
    return render(request, 'events/total_participants.html', {'total': total})

def filter_events(request):
    category_id = request.GET.get('category')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    events = Event.objects.all()

    if category_id:
        events = events.filter(category_id=category_id)
    if start_date and end_date:
        events = events.filter(date__range=[start_date, end_date])

    return render(request, 'events/event_list.html', {'events': events})

def dashboard(request):
    filter_type = request.GET.get('filter', 'today')  # Default to today's events

    # Statistics
    total_participants = Participant.objects.count()
    total_events = Event.objects.count()
    upcoming_events = Event.objects.filter(date__gt=timezone.now().date()).count()
    past_events = Event.objects.filter(date__lt=timezone.now().date()).count()

    # Filtering Logic
    if filter_type == 'participants':
        participants = Participant.objects.all()
        title = "Total Participants"
        context = {
            'title': title,
            'participants': participants,  # Pass participants
        }
    
    elif filter_type == 'upcoming':
        filtered_events = Event.objects.filter(date__gt=timezone.now().date())
        title = "Upcoming Events"
        context = {
            'title': title,
            'filtered_events': filtered_events,
        }
    elif filter_type == 'past':
        filtered_events = Event.objects.filter(date__lt=timezone.now().date())
        title = "Past Events"
        context = {
            'title': title,
            'filtered_events': filtered_events,
        }
    else:
        # Default (Today's Events)
        todays_events = Event.objects.filter(date=timezone.now().date())
        title = "Today's Events"
        context = {
            'title': title,
            'todays_events': todays_events,
        }

    # Add stats to context
    context.update({
        'total_participants': total_participants,
        'total_events': total_events,
        'upcoming_events': upcoming_events,
        'past_events': past_events,
    })

    return render(request, 'events/dashboard.html', context)
