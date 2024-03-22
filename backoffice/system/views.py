import datetime
import time
import uuid

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.core.cache import cache
from django.shortcuts import render, redirect
from django.urls import reverse
from passlib.context import CryptContext
from .models import Settings, Customer, Transactions, Subscriptions
from django.utils import timezone
from .forms import LoginForm, ResetForm, EmailForm, EditProfile, EditPassword, SignUp, SupportForm, SupportMessageForm, \
    SubscribeForm
from support.models import TicketMessage, Ticket, FAQ

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def is_user_exists(email, phone):
    return Customer.objects.filter(email=email).exists() or \
        Customer.objects.filter(phone=phone).exists()


def index(request):
    if request.user.is_authenticated:
        return redirect('panel')
    return render(request, 'panel/index.html', {'title': 'Главная'})


@login_required
def panel(request):
    return render(request, 'panel/panel.html', {'title': 'Кабинет'})


@login_required
def profile(request):
    profile_form = EditProfile(instance=request.user.customer)
    password_form = EditPassword()
    return render(request, 'panel/settings.html', {'profile_form': profile_form,
                                                     'title': 'Настройки', 'password_form': password_form})


@login_required
def edit_password(request):
    password_form = EditPassword(request.POST)
    if pwd_context.verify(password_form.data['current_password'], request.user.password):
        if password_form.data['password'] == password_form.data['confirm_password']:
            employee = Customer.objects.filter(email=request.user.email, show=1).first()
            employee.password = pwd_context.hash(password_form.data['password'])
            employee.save()
            login(request, Customer.objects.get(id=request.user.id))
            return redirect('profile')
        password_form.add_error(None, 'Пароли не совпадают')
        profile_form = EditProfile(instance=request.user.employee)
        return render(request, 'accounts/profile.html', {'profile_form': profile_form, 'title': 'Профиль',
                                                         'password_form': password_form, 'page': 'password'})
    password_form.add_error(None, 'Неверный текущий пароль')
    profile_form = EditProfile(instance=request.user.employee)
    return render(request, 'accounts/profile.html', {'profile_form': profile_form, 'title': 'Профиль',
                                                     'password_form': password_form, 'page': 'password'})


@login_required
def edit_profile(request):
    profile_form = EditProfile(request.POST, request.FILES, instance=request.user.employee)
    if profile_form.is_valid():
        profile_form.save()
        return redirect('profile')
    profile_form.add_error(None, 'Неверные поля')
    password_form = EditProfile(instance=request.user.employee)
    return render(request, 'accounts/profile.html', {'profile_form': profile_form, 'title': 'Профиль',
                                                     'password_form': password_form, 'page': 'edit'})


@login_required
def subscription(request):
    return render(request, 'panel/subscription.html', {'invitation_tokens': Settings.objects.first().referer_tokens})


@login_required
def support(request):
    if request.method == 'POST':
        form = SupportForm(request.POST, request.FILES)
        new_ticket = Ticket(
            title=form.data['title'],
            priority=1,
            client=request.user.customer,
            status=0
        )
        new_ticket.save()
        message = TicketMessage(
            message=form.data['comment'],
            author=0,
            ticket=new_ticket,
            attachment=request.FILES['file'] if 'file' in request.FILES else '',
            read=0
        )
        message.save()
    tickets = Ticket.objects.filter(client=request.user).all()
    faq = FAQ.objects.all()
    form = SupportForm()
    return render(request, 'panel/support.html', {'tickets': tickets, 'faq': faq, 'form': form, 'title': 'Помощь'})


@login_required
def ticket(request, ticket_id):
    if request.method == 'POST':
        form = SupportMessageForm(request.POST, request.FILES)
        message = TicketMessage(
            message=form.data['message'],
            author=0,
            ticket_id=ticket_id,
            attachment=request.FILES['file'] if 'file' in request.FILES else '',
            read=0
        )
        message.save()
    for message in TicketMessage.objects.filter(ticket_id=ticket_id, author=1).all():
        message.read = True
        message.save()
    ticket_messages = TicketMessage.objects.filter(ticket_id=ticket_id).all()
    return render(request, 'panel/ticket.html', {'msgs': ticket_messages, 'ticket_id': ticket_id, 'title': f'Тикет №{ticket_id}'})


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


def referral_view(request, invite_code):
    if not Customer.objects.filter(invite_code=invite_code).first():
        return redirect('index')
    return render(request, 'auth/referral.html', {'invite_code': invite_code, 'invitation_tokens': Settings.objects.first().referer_tokens})


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
                return redirect(reverse('step3') + f'?customer={user.key}')
            if pwd_context.verify(password, user.password):
                login(request, Customer.objects.get(id=user.id))
                return HttpResponseRedirect(reverse('index'))
            form.add_error(None, "Неверный логин или пароль. Попробуйте еще раз или восстановите пароль")
    return render(request, 'auth/login.html', {'form': form})


def set_password(request, token):
    form = ResetForm()
    email = cache.get(f'email:confirm:{token}')
    print(email)
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
