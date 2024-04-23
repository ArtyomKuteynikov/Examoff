# from django import forms
#
# from django.contrib.auth.models import User
#
# from .models import Customer
#
#
# class EmailForm(forms.Form):
#     email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'example@gmail.com'}), label='', )
#
#
# class LoginForm(forms.Form):
#     email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'example@gmail.com'}), label='', )
#     password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': '••••••••'}), label='', )
#
#
# class ResetForm(forms.Form):
#     password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Пароль'}), label='', )
#     confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Подтвердить пароль'}), label='', )
#
#
# class SignUp(forms.ModelForm):
#     class Meta:
#         model = Customer
#         fields = ['email', 'phone', 'surname', 'name']
#         widgets = {
#             'email': forms.EmailInput(attrs={'placeholder': 'Email', 'class': 'form-control'}),
#             'phone': forms.TextInput(attrs={'placeholder': 'Телефон', 'class': 'form-control'}),
#             'surname': forms.TextInput(attrs={'placeholder': 'Фамилия', 'class': 'form-control'}),
#             'name': forms.TextInput(attrs={'placeholder': 'Имя', 'class': 'form-control'})
#         }
#
#
# class EditPassword(forms.Form):
#     current_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Текущий пароль', 'class': 'form-control'}), label='', )
#     password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Новый пароль', 'class': 'form-control'}), label='', )
#     confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Подтвердить пароль', 'class': 'form-control'}), label='', )
#
#
# class SupportForm(forms.Form):
#     title = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Суть вашей проблемы'}), label='Тема')
#     comment = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'подробно опишите проблему'}), label='Комментарий')
#     file = forms.FileField(label='Файл')
#     # captcha = ReCaptchaField(label='')
#
#
# class SupportMessageForm(forms.Form):
#     message = forms.CharField()
#     file = forms.FileField()
#
#
# class SubscribeForm(forms.Form):
#     added_tokens = forms.IntegerField()
#
#
# class BuyTokensForm(forms.Form):
#     added_tokens = forms.IntegerField()
