from django.contrib import admin

from .models import Question, Choice, Token

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3

class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['question_text', 'question_description']}),
        ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
    ]
    list_display = ('question_text', 'question_description', 'pub_date', 'was_published_recently')
    list_filter = ['pub_date']
    search_fields = ['question_text', 'question_description']
    inlines = [ChoiceInline]

admin.site.register(Question, QuestionAdmin)
admin.site.register(Token)
