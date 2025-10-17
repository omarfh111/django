from django.contrib import admin
from .models import *

@admin.register(User)
class userAdmin(admin.ModelAdmin):
    pass
    
# Register your models here.
