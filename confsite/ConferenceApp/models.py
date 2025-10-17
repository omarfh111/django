from django.db import models
from django.conf import settings
# --- FONCTIONS DE VALIDATION (Conference & Submission) ---
import re
from datetime import date
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, MinLengthValidator, FileExtensionValidator
from django.utils.translation import gettext_lazy as _

# 1) Titre conférence : lettres + espaces uniquement
conference_title_regex = RegexValidator(
    regex=r"^[A-Za-zÀ-ÖØ-öø-ÿ ]+$",
    message=_("Title must contain only letters and spaces."),
)

# 2) Description conférence : minimum 30 caractères
minlen_30 = MinLengthValidator(30, message=_("Description must be at least 30 characters."))

# 3) Fichier PDF uniquement
pdf_only = FileExtensionValidator(allowed_extensions=["pdf"])

# 4) Keywords ≤ 10 (séparés par virgules)
def validate_keywords_max10(value: str):
    parts = [p.strip() for p in value.split(",") if p.strip()]
    if len(parts) > 10:
        raise ValidationError(_("Max 10 keywords allowed (comma-separated)."))

# 5) Générer un submission_id du type SUBABCDEFGH
def generate_submission_id():
    import random, string
    token = "".join(random.choices(string.ascii_uppercase, k=8))
    return f"SUB{token}"



class Conference(models.Model):  # 👈 hérite directement de models.Model
    THEME_CHOICES = (
    ('CS_AI', 'Computer Science & Artificial Intelligence'),
    ('SCI_ENG', 'Science & Engineering'),
    ('SOC_EDU', 'Social Sciences & Education'),
    ('INTER', 'Interdisciplinary Themes'),
)
    title = models.CharField(max_length=200,  validators=[conference_title_regex])
    # 🔹 Modèle Conference sans BaseModel
    theme = models.CharField(max_length=20, choices=THEME_CHOICES)
    place = models.CharField(max_length=120)        # lieu de la conférence
    location = models.CharField(max_length=120)     # ville/pays
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(validators=[minlen_30])

    # 🔹 Champs ajoutés directement ici (au lieu du BaseModel)
    created_at = models.DateTimeField(auto_now_add=True)  # à la création
    updated_at = models.DateTimeField(auto_now=True)      # à chaque modification

    def __str__(self):
        return self.title
    def clean(self):
        super().clean()
        if self.start_date and self.end_date and self.end_date <= self.start_date:
            raise ValidationError({"end_date": _("End date must be after start date.")})



class Submission(models.Model):
    submission_id = models.CharField(max_length=255,primary_key=True,unique=True,editable=False,default=generate_submission_id)
    conference = models.ForeignKey('Conference', on_delete=models.CASCADE, related_name='submissions')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submissions')

    title = models.CharField(max_length=200)
    abstract = models.TextField()
    keywords = models.CharField(max_length=300,  validators=[validate_keywords_max10])  # ou TextField si tu préfères
    paper = models.FileField(upload_to='papers/', validators=[pdf_only])

    STATUS_CHOICES = (
    ('SUBMITTED', 'Submitted'),
    ('UNDER_REVIEW', 'Under Review'),
    ('ACCEPTED', 'Accepted'),
    ('REJECTED', 'Rejected'),
)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SUBMITTED')
    submission_date = models.DateField(auto_now_add=True)
    payed = models.BooleanField(default=False)

    # Suivi
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_registration_valid(self):
        # Inscription valide si article accepté ET frais payés
        return self.status == 'ACCEPTED' and self.payed

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


    @property
    def is_registration_valid(self):
        return self.status == 'ACCEPTED' and self.payed

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    # règles business : conf à venir + max 3 conf/jour
    def clean(self):
        super().clean()
        # 1) soumission uniquement si conférence à venir
        if self.conference and self.conference.start_date <= date.today():
            raise ValidationError({"conference": _("Submission allowed only for future conferences.")})
        # 2) max 3 conférences DISTINCTES par jour pour le même auteur
        the_day = self.submission_date or date.today()
        if self.author_id and the_day:
            qs = Submission.objects.filter(author_id=self.author_id, submission_date=the_day)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            distinct_confs = qs.values_list("conference_id", flat=True).distinct()
            if self.conference_id and self.conference_id not in distinct_confs and distinct_confs.count() >= 3:
                raise ValidationError(_("Daily limit reached: 3 different conferences per day."))

    # génération auto du submission_id + sécurité validation
def save(self, *args, **kwargs):
    self.full_clean(exclude=None)   # garde tes règles (clean)
    return super().save(*args, **kwargs)


