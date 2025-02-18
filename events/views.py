from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.utils import timezone
from django.contrib import messages
from .models import Event, Category
from .forms import EventForm

@login_required
def event_list(request):
    events = Event.objects.select_related('category')
    selected_category = request.GET.get('category')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    search_query = request.GET.get('search') 

    if selected_category:
        events = events.filter(category_id=selected_category)
    if start_date and end_date:
        events = events.filter(date__range=[start_date, end_date])
    elif start_date:
        events = events.filter(date__gte=start_date)
    elif end_date:
        events = events.filter(date__lte=end_date)

    if search_query:
        events = events.filter(Q(name__icontains=search_query) | Q(location__icontains=search_query))

    categories = Category.objects.all()
    
    context = {
        'events': events,
        'categories': categories,
        'selected_category': int(selected_category) if selected_category else None,
    }
    return render(request, 'events/event_list.html', context)

@login_required
def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    context = {'event': event}
    return render(request, 'events/event_detail.html', context)


# Create Event (Only Organizer)
@login_required
@permission_required('events.add_event', login_url='no-permission')
def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user  # Assign logged-in user as organizer
            event.save()
            messages.success(request, "Event created successfully!")
            return redirect('event_list')
    else:
        form = EventForm()
    return render(request, 'events/event_form.html', {'form': form})

# Update Event (Only Organizer)
@login_required
@permission_required('events.change_event', login_url='no-permission')
def event_update(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if request.user != event.organizer:
        messages.error(request, "You don't have permission to update this event.")
        return redirect('event_list')

    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Event updated successfully!")
            return redirect('dashboard')
    else:
        form = EventForm(instance=event)
    return render(request, 'events/event_form.html', {'form': form})

# Delete Event (Only Organizer)
@login_required
@permission_required('events.delete_event', login_url='no-permission')
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if request.user != event.organizer:
        messages.error(request, "You don't have permission to delete this event.")
        return redirect('event_list')

    if request.method == 'POST':
        event.delete()
        messages.success(request, "Event deleted successfully!")
        return redirect('dashboard')
    return render(request, 'events/event_confirm_delete.html', {'event': event})

# Total Participants Count
def total_participants(request):
    total = User.objects.aggregate(total=Count('id'))
    return render(request, 'events/total_participants.html', {'total': total})

# Filter Events
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

# Dashboard with Filters
@login_required
def dashboard(request):
    filter_type = request.GET.get('filter', 'today')
    total_participants = User.objects.count()
    total_events = Event.objects.count()
    upcoming_events = Event.objects.filter(date__gt=timezone.now().date()).count()
    past_events = Event.objects.filter(date__lt=timezone.now().date()).count()

    context = {
        'total_participants': total_participants,
        'total_events': total_events,
        'upcoming_events': upcoming_events,
        'past_events': past_events,
    }

    if filter_type == 'participants':
        context.update({
            'title': "Total Participants",
            'participants': User.objects.all(),
        })

    elif filter_type == 'upcoming':
        context.update({
            'title': "Upcoming Events",
            'filtered_events': Event.objects.filter(date__gt=timezone.now().date()).select_related('category'),
        })

    elif filter_type == 'past':
        context.update({
            'title': "Past Events",
            'filtered_events': Event.objects.filter(date__lt=timezone.now().date()).select_related('category'),
        })

    elif filter_type == 'all':
        context.update({
            'title': "Total Events",
            'filtered_events': Event.objects.all().select_related('category')
        })

    else:
        context.update({
            'title': "Today's Events",
            'todays_events': Event.objects.filter(date=timezone.now().date()).select_related('category'),
        })

    return render(request, 'events/dashboard.html', context)

@login_required
def rsvp_event(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if request.user in event.rsvps.all():
        messages.warning(request, "You have already RSVP'd for this event.")
    else:
        event.rsvps.add(request.user)
        messages.success(request, "RSVP successful! A confirmation email has been sent.")

    return redirect('event_detail', pk=pk) 


@login_required
def rsvped_events(request):
    """Display events the user has RSVP'd to."""
    events = Event.objects.filter(rsvps=request.user)  # Fetch events where user has RSVPed
    return render(request, "events/participant_dashboard.html", {"events": events})

