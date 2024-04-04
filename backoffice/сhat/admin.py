import datetime
import random
import string
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import Count, Sum, F
from django.utils.safestring import mark_safe

from .models import Chat


@admin.register(Chat)
class ChatsAdmin(admin.ModelAdmin):
    pass
