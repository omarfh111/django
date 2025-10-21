from django.db import models
from django.core.validators import MaxLengthValidator
from django.core.exceptions import ValidationError
# Create your models here.
import uuid
def generate_submission_id():
    return "SUB"+uuid.uuid4().hex[:8].upper()
class Conference(models.Model):
    conference_id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=255)
    THEME=[
        ("IA","Computer science & ia"),
        ("SE","Science & eng"),
        ("SC","Social sciences"),
    ]
    theme=models.CharField(max_length=255,choices=THEME)
    location=models.CharField(max_length=50)
    description=models.TextField(validators=[
            MaxLengthValidator(30,"vous avez utuliser la limite des mots autorisés")
    ])
    start_date=models.DateField()
    end_date=models.DateField()
    created_at=models.DateTimeField(auto_now_add=True)
    update_at=models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"la conférence a comme titre {self.name}"
    def clean(self):
        if self.start_date > self.end_date:
            raise ValidationError("la date de début de la conférence doit être antérieur à la date fin ")
class Submission(models.Model):
    submission_id=models.CharField(max_length=255,primary_key=True,unique=True,editable=False)
    title=models.CharField(max_length=50)
    abstract=models.TextField()
    keywords=models.TextField()
    paper=models.FileField(
        upload_to="papers/"
    )
    STATUS= [
        ("submitted","submitted"),
        ("under review","under review"),
        ("accepted","accepted"),
        ("rejected","rejected"),
    ]
    status=models.CharField(max_length=50,choices=STATUS)
    payed=models.BooleanField(default=False)
    submission_date=models.DateField(auto_now_add=True)
    created_at=models.DateTimeField(auto_now_add=True)
    update_at=models.DateTimeField(auto_now=True)
    user=models.ForeignKey("UserApp.User",on_delete=models.CASCADE,
                           related_name="submissions")
    conference=models.ForeignKey(Conference,on_delete=models.CASCADE,
                                 related_name="submissions")

    def save(self,*args,**kwargs):
        if not self.submission_id:
            newid=generate_submission_id()
            while Submission.objects.filter(submission_id=newid).exists():
                newid=generate_submission_id()
            self.submission_id=newid
        super().save(*args,**kwargs)
