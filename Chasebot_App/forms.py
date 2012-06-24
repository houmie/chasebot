

__author__ = 'houman'

from django import forms
import re
from django.contrib.auth.models import User
from django.forms import ModelForm
from Chasebot_App.models import UserProfile
from django.utils.translation import ugettext_lazy as _

class RegistrationForm(ModelForm):
    username        = forms.CharField(label=u'Username', max_length=30)
    company_name    = forms.CharField(label=u'Company', max_length=50)
    company_email   = forms.EmailField(label=u'Company Email')
    email           = forms.EmailField(label=u'Email')
    password1       = forms.CharField(label=u'Password', widget=forms.PasswordInput(render_value=False))
    password2       = forms.CharField(label = u'Password (Again)', widget=forms.PasswordInput(render_value=False))

    class Meta:
        model = UserProfile
        exclude = ('user', 'company', 'company_id')

    def clean_password2(self):
        if 'password1' in self.cleaned_data:
            password1 = self.cleaned_data['password1']
            password2 = self.cleaned_data['password2']
            if password1 == password2:
                return password2
        raise forms.ValidationError('Passwords do not match.')

    def clean_username(self):
        username = self.cleaned_data['username']
        if not re.search(r'^\w+$', username):
            raise forms.ValidationError('Username can only contain alphanumeric characters and the underscore.')
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError('Username is already taken.')

    def clean_email(self):
        email = self.cleaned_data['email']
        users = User.objects.filter(email=email)
        if users.count() > 0:
            raise forms.ValidationError("That email is already taken, please select another.")
        return email
