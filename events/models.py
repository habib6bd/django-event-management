from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name

class Event(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='events')
    asset = models.ImageField(upload_to='events-asset', blank=True, null= True, default='events-asset/default-image.jpg')
    rsvps = models.ManyToManyField(User, related_name='rsvp_events', blank=True)

    def __str__(self):
        return self.name
