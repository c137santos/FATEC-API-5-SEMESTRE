from django.contrib import admin

from .models import Issue


class IssueAdmin(admin.ModelAdmin):
    list_display = ("description", "done")


admin.site.register(Issue, IssueAdmin)
