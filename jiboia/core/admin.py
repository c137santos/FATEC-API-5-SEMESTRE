from django.contrib import admin

from .models import Card


class CardAdmin(admin.ModelAdmin):
    list_display = ("description", "done")


admin.site.register(Card, CardAdmin)
