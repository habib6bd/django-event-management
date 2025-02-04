from django.shortcuts import render, get_object_or_404, redirect
from .models import Event, Category, Participant
from .forms import EventForm
from django.db.models import Count, Q
from django.utils import timezone


def event_list(request):
    events = Event.objects.select_related('category').prefetch_related('participants')
    selected_category = request.GET.get('category')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    search_query = request.GET.get('search') 

    # Filter by category
    if selected_category:
        events = events.filter(category_id=selected_category)

    # Filter by date range
    if start_date and end_date:
        events = events.filter(date__range=[start_date, end_date])
    elif start_date:
        events = events.filter(date__gte=start_date)
    elif end_date:
        events = events.filter(date__lte=end_date)

    # Search by name or location
    if search_query:
        events = events.filter(
            Q(name__icontains=search_query) | Q(location__icontains=search_query)
        )

    categories = Category.objects.all()

    context = {
        'events': events,
        'categories': categories,
        'selected_category': int(selected_category) if selected_category else None,
    }
    return render(request, 'events/event_list.html', context)

def event_detail(request, pk):
    event = get_object_or_404(Event.objects.prefetch_related('participants'), pk=pk)
    context = {
        'event': event,
        'participants': event.participants.all(),
    }
    return render(request, 'events/event_detail.html', context)
    
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
            return redirect('dashboard')  
    else:
        form = EventForm(instance=event)
    return render(request, 'events/event_form.html', {'form': form})

# Delete Event
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        event.delete()
        return redirect('dashboard') 
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
    filter_type = request.GET.get('filter', 'today')
    total_participants = Participant.objects.count()
    total_events = Event.objects.count()
    upcoming_events = Event.objects.filter(date__gt=timezone.now().date()).count()
    past_events = Event.objects.filter(date__lt=timezone.now().date()).count()

    if filter_type == 'participants':
        participants = Participant.objects.all()
        title = "Total Participants"
        context = {
            'title': title,
            'participants': participants,
        }

    elif filter_type == 'upcoming':
        filtered_events = Event.objects.filter(date__gt=timezone.now().date()).select_related('category').prefetch_related('participants')
        title = "Upcoming Events"
        context = {
            'title': title,
            'filtered_events': filtered_events,
        }

    elif filter_type == 'past':
        filtered_events = Event.objects.filter(date__lt=timezone.now().date()).select_related('category').prefetch_related('participants')
        title = "Past Events"
        context = {
            'title': title,
            'filtered_events': filtered_events,
        }

    elif filter_type == 'all':
        filtered_events = Event.objects.all().select_related('category').prefetch_related('participants')
        title = "Total Events"
        context = {
            'title': title,
            'filtered_events': filtered_events,
        }

    else:
        todays_events = Event.objects.filter(date=timezone.now().date()).select_related('category').prefetch_related('participants')
        title = "Today's Events"
        context = {
            'title': title,
            'todays_events': todays_events,
        }

    context.update({
        'total_participants': total_participants,
        'total_events': total_events,
        'upcoming_events': upcoming_events,
        'past_events': past_events,
    })

    return render(request, 'events/dashboard.html', context)

