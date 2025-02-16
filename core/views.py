from django.shortcuts import render

# Create your views here.

def home(request):
    # Check if the user is part of the Admin, Organizer, or Participant group
    context = {
        'is_admin': request.user.groups.filter(name='Admin').exists(),
        'is_organizer': request.user.groups.filter(name='Organizer').exists(),
        'is_participant': request.user.groups.filter(name='Participant').exists(),
    }
    return render(request, 'home.html', context)

def no_permission(request):
    return render(request, 'no-permission.html')