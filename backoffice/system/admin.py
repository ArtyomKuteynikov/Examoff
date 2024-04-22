import datetime
import random
import string
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import Count, Sum, F
from django.utils.safestring import mark_safe

# from .models import Settings, Customer, Transactions, Subscriptions
#
#
# class SubscriptionsInline(admin.TabularInline):
#     model = Subscriptions
#     extra = 0
#
#     def has_change_permission(self, request, obj=None):
#         return False
#
#     def has_add_permission(self, request, obj):
#         return False
#
#     def has_delete_permission(self, request, obj=None):
#         return False
#
#
# @admin.register(Transactions)
# class TransactionsAdmin(admin.ModelAdmin):
#     list_filter = ['type', 'method', 'paid', 'created']
#     ordering = ['-created']
#     list_display = ['customer', 'amount', 'type', 'method', 'tokens', 'paid', 'created']
#
#     def has_change_permission(self, request):
#         return False
#
#     def has_add_permission(self, request):
#         return False
#
#     def has_delete_permission(self, request, obj=None):
#         return False
#
#
# @admin.register(Settings)
# class SettingsAdmin(admin.ModelAdmin):
#     fieldsets = (
#         ('Настройки подписки', {
#             'fields': ('subscription_price', 'token_price', 'tokens_in_subscription', 'text'),
#         }),
#         ('Настройки реферальной системы', {
#             'fields': ('max_refers', 'referer_tokens', ),
#         })
#     )
#
#     def has_add_permission(self, request):
#         if Settings.objects.all():
#             return False
#         return True
#
#     def has_delete_permission(self, request, obj=None):
#         return False
#
#
# class StaffAdmin(UserAdmin):
#     def get_queryset(self, request):
#         return super().get_queryset(request).filter(is_staff=True)
#
#     def save_model(self, request, obj, form, change):
#         obj.is_staff = True
#         super().save_model(request, obj, form, change)
#
#
# @admin.register(Customer)
# class EmployeeAdmin(admin.ModelAdmin):
#
#     exclude = ['uuid', 'show', 'password']
#     list_display = ['edit', 'name', 'surname', 'email']
#
#     actions = ['delete', 'invite']
#
#     inlines = [SubscriptionsInline]
#
#     def delete(self, request, queryset):
#         for courier in queryset:
#             courier.show = False
#             courier.save()
#
#     delete.short_description = 'Удалить'
#
#     def invite(self, request, queryset):
#         for employee in queryset:
#             if not employee.password:
#                 employee.confirm_email()
#
#     invite.short_description = 'Повторно отправить подтверждение'
#
#     def has_delete_permission(self, request, obj=None):
#         return False
#
#     def get_queryset(self, request):
#         return super().get_queryset(request).filter(show=True)
#
#     def edit(self, obj):
#         return mark_safe('<i class="fa-solid fa-pen fa-fw"></i>')
#
#     def view(self, obj):
#         return mark_safe('<i class="fa-solid fa-eye"></i>')
#
#     edit.short_description = ''
#     view.short_description = ''
#
#
# # admin.site.register(Customer, StaffAdmin)
#
