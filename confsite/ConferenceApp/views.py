from django.shortcuts import render
from .models import Conference
from django.views.generic import *
from django.urls import reverse_lazy
from .form import *
# Create your views here.


def list_conferences(request):
    conferences_list=Conference.objects.all()
    """retour : liste + page """
    return render(request,"conferences/liste.html", {"liste":conferences_list})

class ConferenceList(ListView):
    model=Conference
    context_object_name="liste"
    template_name="conferences/liste.html"

class ConferenceDetails(DetailView):
    model=Conference
    context_object_name="conference"
    template_name="conferences/details.html"

class ConferenceCreate(CreateView):
    model= Conference
    template_name ="conferences/form.html"
    #fields = "__all__"
    form_class=ConferenceForm
    success_url = reverse_lazy("liste_conferences")
class ConferenceUpdate(UpdateView):
    model = Conference
    template_name = "conferences/form.html"
    #fields = "__all__"
    form_class=ConferenceForm
    success_url = reverse_lazy("liste_conferences")
class ConferenceDelete(DeleteView):
    model=Conference
    template_name="conferences/conference_confirm_delete.html"
    fields = "__all__"
    success_url = reverse_lazy("liste_conferences")
    