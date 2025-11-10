from django.shortcuts import render
from .models import Conference
from django.views.generic import *
from django.urls import reverse_lazy
from .form import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from .models import Submission
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

class ConferenceCreate(LoginRequiredMixin,CreateView):
    model= Conference
    template_name ="conferences/form.html"
    #fields = "__all__"
    form_class=ConferenceForm
    success_url = reverse_lazy("liste_conferences")
class ConferenceUpdate(LoginRequiredMixin,UpdateView):
    model = Conference
    template_name = "conferences/form.html"
    #fields = "__all__"
    form_class=ConferenceForm
    success_url = reverse_lazy("liste_conferences")
class ConferenceDelete(LoginRequiredMixin,DeleteView):
    model=Conference
    template_name="conferences/conference_confirm_delete.html"
    fields = "__all__"
    success_url = reverse_lazy("liste_conferences")

class ListSubmissions(LoginRequiredMixin, ListView):
    model = Submission
    template_name = "submissions/list.html"
    context_object_name = "submissions"

    def get_queryset(self):
        return Submission.objects.filter(user=self.request.user)    
class DetailSubmission(LoginRequiredMixin, DetailView):
    model = Submission
    template_name = "submissions/detail.html"
    context_object_name = "submission"
class AddSubmission(LoginRequiredMixin, CreateView):
    model = Submission
    fields = ["title", "abstract", "keywords", "paper", "conference"]
    template_name = "submissions/form.html"
    success_url = reverse_lazy("list_submissions")

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.status = "submitted"
        return super().form_valid(form)
class UpdateSubmission(LoginRequiredMixin, UpdateView):
    model = Submission
    fields = ["title", "abstract", "keywords", "paper"]
    template_name = "submissions/form.html"
    success_url = reverse_lazy("list_submissions")

    def get_object(self, queryset=None):
        submission = super().get_object(queryset)
        if submission.status in ["accepted", "rejected"]:
            raise PermissionError("Vous ne pouvez pas modifier cette soumission.")
        return submission
