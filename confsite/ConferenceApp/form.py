from django import forms
from .models import Conference
class ConferenceForm(forms.ModelForm):
    class Meta:
        model=Conference
        fields=['name','theme','location','start_date','end_date','description']
        labels = {
            'name' : "titre de la conference",
            'theme' :"thematique de la conferece"
        }
        widgets = {
            'name' : forms.TextInput(attrs={
                'palceHolder' : "Entrer  un titre a la conference"
            }),
            'start_date' : forms.DateInput(attrs={
                'type' : "date"
            }),
            'end_date' : forms.DateInput(attrs={
                'type' : "date"
            }),
        }