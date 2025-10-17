from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
from django.conf import settings
from ConferenceApp.models import Conference
import re
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

# 1) domaines universités
ALLOWED_UNI_DOMAINS = {"esprit.tn"}  # ajoute d'autres si besoin

def validate_user_email_domain(value: str):
    if "@" not in value:
        raise ValidationError(_("Invalid email format."))
    domain = value.split("@")[-1].lower()
    if not any(domain == d or domain.endswith("." + d) for d in ALLOWED_UNI_DOMAINS):
        raise ValidationError(_("Email must be a university domain (e.g. @esprit.tn)."))

# 2) noms/prénoms : lettres + espaces + tirets
name_regex = RegexValidator(
    regex=r"^[A-Za-zÀ-ÖØ-öø-ÿ\- ]+$",
    message=_("Only letters, spaces, and hyphens are allowed."),
)

# 3) user_id : "USER" + 4 chiffres, longueur 8
def validate_user_id_format(value: str):
    if not re.fullmatch(r"USER\d{4}", value or ""):
        raise ValidationError(_("user_id must match 'USER' + 4 digits, e.g. USER1234."))
    if len(value) != 8:
        raise ValidationError(_("user_id length must be exactly 8."))

# 4) génération de user_id
def generate_user_id():
    from random import choices
    from string import digits
    return "USER" + "".join(choices(digits, k=4))
ROLE_CHOICES = (
    ('participant', 'Participant'),
    ('organizer', 'Organisateur'),
    ('committee', 'Membre Comité Sci.'),
)

class User(AbstractUser):
    # 🔹 Clé primaire personnalisée : chaîne fixe de longueur 8
    user_id = models.CharField(
        max_length=8,
        primary_key=True,
        unique=True,
        editable=False,
        validators=[MinLengthValidator(8)]
    )

    email = models.EmailField(unique=True, validators=[validate_user_email_domain])
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='participant')
    first_name = models.CharField(max_length=150, validators=[name_regex])
    last_name  = models.CharField(max_length=150, validators=[name_regex])

    # 🔹 Ajout direct des champs de suivi (au lieu du BaseModel)
    created_at = models.DateTimeField(auto_now_add=True)  # à la création
    updated_at = models.DateTimeField(auto_now=True)      # à chaque modification
    class Meta:
        verbose_name = "Utulisateur"              # nom singulier
        verbose_name_plural = "Utulisateurs"
    # On garde le système d’authentification par défaut (username + password)
    # USERNAME_FIELD = 'username'
    # REQUIRED_FIELDS = ['email']

    def __str__(self):
        return f"{self.user_id} - {self.username}"
    def clean(self):
        super().clean()
        if self.user_id:
            validate_user_id_format(self.user_id)

    # génère automatiquement USER#### si vide
    def save(self, *args, **kwargs):
        if not self.user_id:
            uid = generate_user_id()
            while User.objects.filter(user_id=uid).exists():
                uid = generate_user_id()
            self.user_id = uid
        return super().save(*args, **kwargs)


class OrganizingCommittee(models.Model):
    COMMITTEE_ROLE = (
    ('chair', 'Chair'),
    ('co-chair', 'Co-Chair'),
    ('member', 'Member'),
)
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE, related_name='committee_members')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='committee_roles')
    committee_role = models.CharField(max_length=20, choices=COMMITTEE_ROLE)
    date_joined = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.get_committee_role_display()} @ {self.conference}"

