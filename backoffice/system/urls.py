from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('panel/', panel, name='panel'),
    path('subscription/', subscription, name='subscription'),
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('signup/<str:invite_code>', signup_view, name='signup'),
    path('accounts/login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('confirm/<str:token>', set_password, name='set-password'),
    path('request/', request_password_reset, name='request-reset-password'),
    path('referral/<str:invite_code>', referral_view, name='referral'),
    path('reset/<str:token>', reset_password, name='reset-password'),
    path('settings/', profile, name='profile'),
    path('edit-password/', edit_password, name='edit-password'),
    path('edit-profile/', edit_profile, name='edit-profile'),
    path('edit-email-confirm/', edit_profile_confirm, name='edit-email-confirm'),
    path('support/', support, name='support'),
    path('subscribe/', subscribe, name="subscribe"),
    path('light/', index_light, name='index-light'),
    path('panel/light/', panel_light, name='panel-light'),
    path('light/support/', support_light, name='support-light'),
    path('light/subscription/', subscription_light, name="subscribe-light"),
    path('light/settings/', profile_light, name='profile-light'),
    path('buy/', add_tokens, name="add-tokens"),
    path('paid/<int:transaction_id>', paid, name="paid"),
    path('success/', success, name="success")
]
