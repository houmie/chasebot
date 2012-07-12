__author__ = 'houman'
from django.forms.widgets import TextInput
from django.utils.formats import get_format
from django import forms
import re
from django.contrib.auth.models import User
from django.forms import ModelForm
from chasebot_app.models import UserProfile, Contact, ContactType, Country, MaritalStatus, Conversation
from django.utils.translation import ugettext_lazy as _

class RegistrationForm(ModelForm):
    username        = forms.CharField(label = _(u'Username'), max_length=30)
    company_name    = forms.CharField(label = _(u'Company'), max_length=50)
    company_email   = forms.EmailField(label= _(u'Company Email'))
    email           = forms.EmailField(label= _(u'Email'))
    password        = forms.CharField(label = _(u'Password'), widget=forms.PasswordInput(render_value=False))
    password2       = forms.CharField(label = _(u'Password (Again)'), widget=forms.PasswordInput(render_value=False))

    class Meta:
        model = UserProfile
        exclude = ('user', 'company')

    def clean_password2(self):
        if 'password' in self.cleaned_data:
            password = self.cleaned_data['password']
            password2 = self.cleaned_data['password2']
            if password == password2:
                return password
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


class ContactsForm(ModelForm):
    def __init__(self, company, *args, **kwargs):
        super(ContactsForm, self).__init__(*args, **kwargs)
        # limit selection list to just items for this account
        self.fields['contact_type'].queryset = ContactType.objects.filter(company=company)

    class Meta:
        model = Contact
        exclude = ('company')
        widgets = {
                'first_name': forms.TextInput(  attrs={'placeholder': 'Enter first name here',          'class': 'placeholder_fix_css'}),
                'last_name': forms.TextInput(   attrs={'placeholder': 'Enter last name here',           'class': 'placeholder_fix_css'}),
                'dear': forms.TextInput(        attrs={'placeholder': 'Enter the preferred short name', 'class': 'placeholder_fix_css'}),
                'city': forms.TextInput(        attrs={'placeholder': 'Enter the city here',            'class': 'placeholder_fix_css'}),
                'state': forms.TextInput(       attrs={'placeholder': 'Enter the state here',           'class': 'placeholder_fix_css'}),
                'postcode': forms.TextInput(    attrs={'placeholder': 'Enter the zip code here',        'class': 'placeholder_fix_css'}),
                'company_name': forms.TextInput(attrs={'placeholder': 'Add a company',                  'class': 'placeholder_fix_css'}),
                'position': forms.TextInput(    attrs={'placeholder': 'Add a position',                 'class': 'placeholder_fix_css'}),
                'work_phone': forms.TextInput(  attrs={'placeholder': 'Add a work phone',               'class': 'placeholder_fix_css'}),
                'home_phone': forms.TextInput(  attrs={'placeholder': 'Add a home phone',               'class': 'placeholder_fix_css'}),
                'mobile_phone': forms.TextInput(attrs={'placeholder': 'Add a cell phone',               'class': 'placeholder_fix_css'}),
                'fax_number': forms.TextInput(  attrs={'placeholder': 'Add a fax number',               'class': 'placeholder_fix_css'}),
                'email': forms.TextInput(       attrs={'placeholder': 'Add an email',                   'class': 'placeholder_fix_css'}),
                'birth_date': forms.DateInput(  attrs={'placeholder': 'Add the day of birth', 'id': 'datepicker', 'class': 'placeholder_fix_css'}, format='%d/%m/%Y'),
                'referred_by': forms.TextInput( attrs={'placeholder': '...was referred by?', 'class': 'placeholder_fix_css'}),
                'spouse_first_name': forms.TextInput(attrs={'placeholder': 'What is the spouse\'s name?', 'class': 'placeholder_fix_css'}),
                'children_names': forms.TextInput(attrs={'placeholder': 'What are the children names?', 'class': 'placeholder_fix_css'}),
                'home_town': forms.TextInput(   attrs={'placeholder': 'Enter the home town',            'class': 'placeholder_fix_css'}),
                'address': forms.Textarea(      attrs={'rows':4, 'placeholder': 'Add an address',       'class': 'placeholder_fix_css'}),
                'contact_notes': forms.Textarea(attrs={'rows':4, 'placeholder': 'What is the personality like?'}),
                'contacts_interests': forms.Textarea(attrs={'rows':4, 'placeholder': 'Any particular interests?'}),
                'spouses_interests': forms.Textarea(attrs={'rows':4, 'placeholder': 'Does the spouse have any particular interest?'}),
                'prev_meeting_places': forms.Textarea(attrs={'rows':4, 'placeholder': 'Where did you meet so far?'})                       
            }

class CallsForm(ModelForm):   
    
    class Meta:
        model = Conversation
        exclude = ('company', 'contact')
        widgets = {
                    'contact_date': forms.DateInput(attrs={'placeholder': 'Add the date...', 'id': 'datepicker', 'class': 'placeholder_fix_css'}, format='%d/%m/%Y'),
                    'contact_time': forms.TimeInput(attrs={'placeholder': 'Add the time...',                     'class': 'placeholder_fix_css'}),
                    'subject': forms.TextInput(attrs={'placeholder': '',                                         'class': 'placeholder_fix_css'}),
                    'notes': forms.Textarea(attrs={'placeholder': 'Add relevant notes...'}),
                   }



class CountryForm(ModelForm):
    class Meta:
        model = Country


class MaritalStatusForm(ModelForm):
    class Meta:
        model = MaritalStatus

class ContactTypeForm(ModelForm):
    class Meta:
        model = ContactType
        exclude = ('company')


