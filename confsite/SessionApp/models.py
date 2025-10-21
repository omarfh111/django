from django.db import models
from ConferenceApp.models import Conference
# Create your models here.

class Session(models.Model):
    session_id=models.AutoField(primary_key=True)
    title=models.CharField(max_length=255)
    topic=models.CharField(max_length=255)
    session_day=models.DateField()
    start_time=models.TimeField()
    end_time=models.TimeField()
    room=models.CharField(max_length=255)
    created_at=models.DateTimeField(auto_now_add=True)
    update_at=models.DateTimeField(auto_now=True)
    conference=models.ForeignKey("ConferenceApp.Conference",
                                  on_delete=models.CASCADE,
                                 related_name="sessions")
    #conference=models.ForeignKey(Conference, on_delete=models.CASCADE)