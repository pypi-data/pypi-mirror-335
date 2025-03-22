from django.contrib import admin

from .models import WrappedSubject


class WrappedSubjectAdmin(admin.ModelAdmin):
    list_display = 'pseudonym', 'subject'


admin.site.register(WrappedSubject, WrappedSubjectAdmin)
