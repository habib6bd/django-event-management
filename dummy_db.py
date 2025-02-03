from events.models import Category, Event, Participant
from django.utils import timezone
from datetime import timedelta, time
import random

# Clear existing events and participants (keeps categories intact)
Event.objects.all().delete()
Participant.objects.all().delete()

# 1. Fetch Existing Categories
categories = list(Category.objects.all())
if not categories:
    print("⚠️ No categories found. Please create categories first.")
else:
    # 2. Create Events
    event_names = [
        'Tech Summit 2025', 'AI Conference', 'Django Meetup', 'Python Workshop',
        'Data Science Bootcamp', 'Startup Pitch', 'Blockchain Expo', 
        'Web Dev Seminar', 'Cloud Computing Workshop', 'Cybersecurity Forum'
    ]

    events = []
    for i, name in enumerate(event_names):
        event = Event.objects.create(
            name=name,
            description=f'{name} event description.',
            date=timezone.now().date() + timedelta(days=random.randint(-5, 10)),  # Some past, some future
            time=time(hour=random.randint(9, 18), minute=0),
            location=f'Location {i+1}',
            category=random.choice(categories)  # Use existing categories
        )
        events.append(event)

    # 3. Create Participants
    participant_names = [
        'Alice Johnson', 'Bob Smith', 'Charlie Lee', 'David Brown', 
        'Evelyn Clark', 'Frank Harris', 'Grace Lewis', 'Henry Walker', 
        'Isabella Young', 'Jack Wilson'
    ]

    for name in participant_names:
        participant = Participant.objects.create(
            name=name,
            email=f"{name.lower().replace(' ', '.')}@example.com"
        )
        # Each participant attends 2-4 random events
        participant.events.set(random.sample(events, k=random.randint(2, 4)))

    print("✅ Dummy data (10 events & 10 participants) created successfully!")
