from django.db import models
from ConferenceApp.models import Conference
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

# 1) room : alphanum + espaces + tirets
room_regex = RegexValidator(
    regex=r"^[A-Za-z0-9\- ]+$",
    message=_("Room must contain only letters, digits, spaces or hyphens."),
)
class Session(models.Model):
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE, related_name='sessions')
    title = models.CharField(max_length=200)
    topic = models.CharField(max_length=200)
    session_day = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=80,  validators=[room_regex])

    # Suivi
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "Session"              # nom singulier
        verbose_name_plural = "Sessions"
    def __str__(self):
        return f"{self.title} @ {self.conference}"
    def clean(self):
        super().clean()
        if self.conference_id and self.session_day:
            if not (self.conference.start_date <= self.session_day <= self.conference.end_date):
                raise ValidationError({"session_day": _("Session day must be within the conference dates.")})
        if self.start_time and self.end_time and not (self.end_time > self.start_time):
            raise ValidationError({"end_time": _("End time must be after start time.")})
