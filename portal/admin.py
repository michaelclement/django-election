from django.contrib import admin

from .models import Submitter, WordleSubmission, Champion

# Register your models here.
admin.site.register(Submitter)
admin.site.register(WordleSubmission)
admin.site.register(Champion)
