from django.contrib import admin
from .models import Conference, Submission

# -----------------------
# Inline (version stacked)
# -----------------------
class SubmissionStackedInline(admin.StackedInline):
    model = Submission
    fk_name = "conference"
    extra = 0

    # on remplace submission_id par un affichage readonly basé sur PK
    fields = (
        "title", "abstract", "status", "payed",
        "author", "keywords", "paper",
        "display_id", "submission_date",
    )
    readonly_fields = ("display_id", "submission_date")

    # callable autorisé par Django pour readonly_fields
    def display_id(self, obj):
        return obj.pk
    display_id.short_description = "ID"

# -----------------------
# Inline (version tabular)
# -----------------------
class SubmissionTabularInline(admin.TabularInline):
    model = Submission
    fk_name = "conference"
    extra = 0
    fields = ("title", "status", "author", "payed")


@admin.register(Conference)
class ConferenceAdmin(admin.ModelAdmin):
    list_display = ("title", "theme", "location", "start_date", "end_date", "duration")
    list_filter = ("theme", "location", "start_date")
    search_fields = ("title", "description", "location")
    ordering = ("start_date",)
    date_hierarchy = "start_date"
    fieldsets = (
        ("Informations générales", {"fields": ("title", "theme", "description")}),
        ("Logistique", {"fields": ("place", "location", "start_date", "end_date")}),
    )
    # choisis l’un des deux inlines :
    inlines = [SubmissionStackedInline]
    # inlines = [SubmissionTabularInline]

    def duration(self, obj):
        if obj.start_date and obj.end_date:
            return (obj.end_date - obj.start_date).days
        return None
    duration.short_description = "Durée (jours)"


# ----------------------------
# Admin du modèle Submission
# ----------------------------
@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    # colonnes
    list_display = ("title", "short_abstract", "status", "author",
                    "conference", "submission_date", "payed")

    # filtres et recherche
    list_filter = ("status", "payed", "conference", "submission_date")
    search_fields = ("title", "keywords", "author__username")

    # édition inline dans la liste
    list_editable = ("status", "payed")
    list_display_links = ("title",)

    # on n’utilise pas submission_id, donc on affiche un ID readonly via callable
    readonly_fields = ("display_id", "submission_date")
    fieldsets = (
        ("Infos générales", {"fields": ("display_id", "title", "abstract", "keywords")}),
        ("Fichier & conférence", {"fields": ("paper", "conference")}),
        ("Suivi", {"fields": ("status", "payed", "submission_date", "author")}),
    )

    # méthode pour l’ID affiché (PK)
    def display_id(self, obj):
        return obj.pk
    display_id.short_description = "ID"

    # abstract tronqué
    def short_abstract(self, obj):
        if not obj.abstract:
            return ""
        txt = str(obj.abstract)
        return (txt[:50] + "…") if len(txt) > 50 else txt
    short_abstract.short_description = "Abstract (50)"

    # actions
    actions = ["mark_as_payed", "accept_selected"]

    def mark_as_payed(self, request, queryset):
        updated = queryset.update(payed=True)
        self.message_user(request, f"{updated} soumission(s) marquée(s) payée(s).")
    mark_as_payed.short_description = "Marquer comme payées"

    def accept_selected(self, request, queryset):
        # tes CHOICES utilisent 'ACCEPTED'
        updated = queryset.update(status="ACCEPTED")
        self.message_user(request, f"{updated} soumission(s) acceptée(s).")
    accept_selected.short_description = "Accepter les soumissions sélectionnées"
