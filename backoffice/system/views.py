import datetime
import random
import time
import uuid

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.core.cache import cache
from django.middleware.csrf import get_token
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from passlib.context import CryptContext
from .models import Settings, Customer, Transactions, Subscriptions
from django.utils import timezone
from .forms import LoginForm, ResetForm, EmailForm, EditPassword, SignUp, SupportForm, SupportMessageForm,  SubscribeForm
from support.models import TicketMessage, Ticket, FAQ

from .utils import send_email

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def is_user_exists(email, phone):
    return Customer.objects.filter(email=email).exists() or \
        Customer.objects.filter(phone=phone).exists()


def index(request):
    if request.user.is_authenticated:
        return redirect('panel')
    return render(request, 'landing.html', {'title': 'Главная'})


@login_required
def panel(request):
    return render(request, 'panel/panel.html')


@login_required
def voice(request):
    return render(request, 'panel/voice.html')


@login_required
def voice_light(request):
    return render(request, 'light-panel/voice.html')


@login_required
def profile(request):
    return render(request, 'panel/settings.html', {'title': 'Настройки'})


def index_light(request):
    if request.user.is_authenticated:
        return redirect('panel-light')
    return render(request, 'light-panel/index.html', {'title': 'Главная'})


@login_required
def panel_light(request):
    return render(request, 'light-panel/panel.html', {'title': 'Кабинет'})


@login_required
def profile_light(request):
    return render(request, 'light-panel/settings.html', {'title': 'Настройки'})


@login_required
def edit_password(request):
    old_password = request.POST.get('old-password')
    new_password = request.POST.get('new-password')
    if request.user.customer.verify_password(old_password):
        print('OK')
        employee = Customer.objects.filter(email=request.user.email, show=1).first()
        employee.set_password_hash(new_password)
        employee.save()
        login(request, employee)
        return JsonResponse(
            {
                'success': True,
                'csrf_token': get_token(request)
            }
        )
    return JsonResponse(
        {'success': False}, status=401
    )


@login_required
def edit_profile(request):
    email = request.POST.get('email')
    if Customer.objects.filter(email=email).first():
        JsonResponse(
            {'success': False}, status=401
        )
    code = random.randint(100000, 999999)
    cache.set(f'change:code:{request.user.email}', code, 3600)
    cache.set(f'change:value:{request.user.email}', email, 3600)
    message = f'''Здравствуйте, {request.user.customer.name}!
Ваш код подтверждения электронной почты: {code} 

С уважением,
Examoff'''
    send_email(email, 'Смена Email', message)
    return JsonResponse(
        {
            'success': True,
            'csrf_token': get_token(request)
        }
    )


@login_required
def edit_profile_confirm(request):
    code = request.POST.get('code')
    print(code, cache.get(f'change:code:{request.user.email}'))
    if str(code) != str(cache.get(f'change:code:{request.user.email}')):
        return JsonResponse(
            {'success': False}, status=401
        )
    new_email = cache.get(f'change:value:{request.user.email}')
    customer = Customer.objects.get(id=request.user.customer.id)
    customer.email = new_email
    customer.save()
    return JsonResponse(
        {'success': True, 'email': new_email}
    )


@login_required
def subscription(request):
    return render(request, 'panel/subscription.html', {'invitation_tokens': Settings.objects.first().referer_tokens, 'title': 'Подписка'})


@login_required
def support_light(request):
    faq = FAQ.objects.all()
    return render(request, 'light-panel/support.html', {'faq': faq, 'title': 'Помощь'})


@login_required
def subscription_light(request):
    return render(request, 'light-panel/subscription.html', {'invitation_tokens': Settings.objects.first().referer_tokens, 'title': 'Подписка'})


@login_required
def support(request):
    faq = FAQ.objects.all()
    return render(request, 'panel/support.html', {'faq': faq, 'title': 'Помощь'})


@login_required
def subscribe(request):
    if request.method == 'POST':
        form = SubscribeForm(request.POST)
        price = Settings.objects.first().subscription_price + float(form.data['added_tokens']) * float(Settings.objects.first().token_price)
        transaction = Transactions(
            customer=request.user.customer,
            amount=price,
            type=0 if form.data['added_tokens'] == 0 else 2,
            method=0,
            tokens=form.data['added_tokens']
        )
        transaction.save()
        return render(request, 'pay.html', {'price': price, 'transaction_id': transaction.id})


@login_required
def add_tokens(request):
    if request.method == 'POST':
        form = SubscribeForm(request.POST)
        price = float(form.data['added_tokens']) * float(Settings.objects.first().token_price)
        transaction = Transactions(
            customer=request.user.customer,
            amount=price,
            type=1,
            method=0,
            tokens=form.data['added_tokens']
        )
        transaction.save()
        return render(request, 'pay.html', {'price': price, 'transaction_id': transaction.id})


def paid(request, transaction_id):
    transaction = Transactions.objects.get(id=transaction_id)
    if transaction.paid:
        return
    transaction.paid = True
    transaction.save()
    if transaction.type in [0, 2]:
        start = max([datetime.datetime.now().date(), Subscriptions.objects.filter(customer=transaction.customer).order_by('-end').first().end]) if Subscriptions.objects.filter(customer=transaction.customer).order_by('-end').first() else datetime.datetime.now().date()
        subscription = Subscriptions(
            customer=transaction.customer,
            start=start,
            end=start + datetime.timedelta(days=30)
        )
        subscription.save()
    customer = Customer.objects.get(id=transaction.customer.id)
    customer.tokens = customer.tokens + transaction.tokens
    customer.save()
    return redirect('success')


def success(request):
    return render(request, 'panel/success.html', )


@csrf_exempt
def signup_view(request, invite_code=None):
    form = SignUp()
    if request.method == 'POST':
        form = SignUp(request.POST)
        exists = is_user_exists(form.data['email'], form.data['phone'])
        if exists:
            form.add_error(None, 'Пользователь с таким номером телефона или email уже существует')
            return render(request, 'auth/signup.html', {'form': form, 'invite_code': invite_code})
        if form.is_valid():
            customer = form.save(commit=False)
            customer.username = uuid.uuid4()
            customer.confirm_email()
            if invite_code:
                referrer = Customer.objects.filter(invite_code=invite_code).first()
                customer.referer = referrer
                referrer.tokens = referrer.tokens + Settings.objects.first().referer_tokens
                customer.tokens = Settings.objects.first().referer_tokens
                referrer.save()
            customer.save()
            return render(request, 'auth/success.html')
    return render(request, 'auth/signup.html', {'form': form, 'invite_code': invite_code})


@csrf_exempt
def referral_view(request, invite_code):
    if not Customer.objects.filter(invite_code=invite_code).first():
        return redirect('index')
    return render(request, 'auth/referral.html', {'invite_code': invite_code, 'invitation_tokens': Settings.objects.first().referer_tokens})


@csrf_exempt
def login_view(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.data['email']
            password = form.data['password']
            user = Customer.objects.filter(email=email, show=True).first()
            if not user:
                form.add_error(None, "Такого пользователя не существует")
                return render(request, 'auth/login.html', {'form': form})
            if not user.active:
                form.add_error(None, "Пользователь заблокирован")
                return render(request, 'auth/login.html', {'form': form})
            if not user.password:
                return render(request, 'auth/success.html')
            if pwd_context.verify(password, user.password):
                login(request, Customer.objects.get(id=user.id))
                return HttpResponseRedirect(reverse('index'))
            form.add_error(None, "Неверный логин или пароль. Попробуйте еще раз или восстановите пароль")
    return render(request, 'auth/login.html', {'form': form})


@csrf_exempt
def set_password(request, token):
    form = ResetForm()
    email = cache.get(f'email:confirm:{token}')
    if not email:
        return render(request, 'auth/expired.html', {'form': form, 'token': token})
    if request.method == 'POST':
        form = ResetForm(request.POST)
        if form.data['password'] != form.data['confirm_password']:
            form.add_error(None, "Пароли не совпадают")
            return render(request, 'auth/email-verify.html', {'form': form, 'token': token})
        employee = Customer.objects.filter(email=email, show=1).first()
        if employee:
            employee.password = pwd_context.hash(form.data['password'])
            employee.save()
            cache.set(f"email:token:{token}", None, timeout=86400)
            login(request, Customer.objects.get(id=employee.id))
            return HttpResponseRedirect(reverse('index'))
    return render(request, 'auth/email-verify.html', {'form': form, 'token': token})


@csrf_exempt
def request_password_reset(request):
    form = EmailForm()
    if request.method == 'POST':
        form = EmailForm(request.POST)
        employee = Customer.objects.filter(email=form.data['email'], show=True).first()
        if not employee:
            return render(request, 'auth/reset-1.html', {'form': form, 'mistake': True})
        employee.reset_password_hash()
        return render(request, 'auth/reset-1.html', {'form': form, 'success': True})
    return render(request, 'auth/reset-1.html', {'form': form})


@csrf_exempt
def reset_password(request, token):
    form = ResetForm()
    email = cache.get(f'email:reset:{token}')
    if not email:
        return render(request, 'auth/expired.html', {'form': form, 'token': token})
    if request.method == 'POST':
        form = ResetForm(request.POST)
        if form.data['password'] != form.data['confirm_password']:
            form.add_error(None, "Пароли не совпадают")
            return render(request, 'auth/reset-2.html', {'form': form, 'token': token})
        employee = Customer.objects.filter(email=email).first()
        employee.password = pwd_context.hash(form.data['password'])
        employee.save()
        cache.set(f"email:reset:{token}", None, timeout=86400)
        login(request, Customer.objects.get(id=employee.id))
        return HttpResponseRedirect(reverse('index'))
    return render(request, 'auth/reset-2.html', {'form': form, 'token': token})


def logout_view(request):
    logout(request)
    return redirect('login')
