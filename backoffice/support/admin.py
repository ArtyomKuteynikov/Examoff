from django.contrib import admin
from django.db import transaction
from django.db.models import Sum, Count, Q
from .models import FAQ


class FAQAdmin(admin.ModelAdmin):
    list_display = ['title']


admin.site.register(FAQ, FAQAdmin)
