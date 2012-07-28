__author__ = 'houman'
from django.forms.widgets import TextInput
from django.utils.formats import get_format
from django import forms
import re
import operator
import collections
from django.contrib.auth.models import User
from django.forms import ModelForm
from chasebot_app.models import UserProfile, Contact, ContactType, Country, MaritalStatus, Conversation, SalesItem, Deal, SalesTerm,\
    DealStatus, Conversation_Deal
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
        #self.fields['contact_type'].queryset = ContactType.objects.filter(company=company)

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
#    status_1    =   forms.ModelChoiceField()
    
    def __init__(self, company, *args, **kwargs):
        super(CallsForm, self).__init__(*args, **kwargs)                                        
        self.fields['deal_1'].queryset = self.get_non_duplicate_deals(self.instance, company)            
        #self.fields['status_1'].queryset = DealStatus.objects.all()
        self.fields['deal_2'].queryset = self.get_non_duplicate_deals(self.instance, company)       
        #self.fields['status_2'].queryset = DealStatus.objects.all()
        self.fields['deal_3'].queryset = self.get_non_duplicate_deals(self.instance, company)
        #self.fields['status_3'].queryset = DealStatus.objects.all()
        self.fields['deal_4'].queryset = self.get_non_duplicate_deals(self.instance, company)
        #self.fields['status_4'].queryset = DealStatus.objects.all()
        self.fields['deal_5'].queryset = self.get_non_duplicate_deals(self.instance, company)
        #self.fields['status_5'].queryset = DealStatus.objects.all()
        self.fields['deal_6'].queryset = self.get_non_duplicate_deals(self.instance, company)
        #self.fields['status_6'].queryset = DealStatus.objects.all()
    
        
    deal_1      =   forms.ModelChoiceField(required=False, queryset = '')#, widget=forms.Select(attrs={'class':'hidden_cb'}))   
    #status_1    =   forms.ModelChoiceField(required=False, queryset = '', widget=forms.Select(attrs={'class':'hidden_cb'})) 
    deal_2      =   forms.ModelChoiceField(required=False, queryset = '')#, widget=forms.Select(attrs={'class':'hidden_cb2'}))   
    #status_2    =   forms.ModelChoiceField(required=False, queryset = '', widget=forms.Select(attrs={'class':'hidden_cb'}))
    deal_3      =   forms.ModelChoiceField(required=False, queryset = '')#, widget=forms.Select(attrs={'class':'hidden_cb'}))   
    #status_3    =   forms.ModelChoiceField(required=False, queryset = '', widget=forms.Select(attrs={'class':'hidden_cb'}))
    deal_4      =   forms.ModelChoiceField(required=False, queryset = '')#, widget=forms.Select(attrs={'class':'hidden_cb'}))   
    #status_4    =   forms.ModelChoiceField(required=False, queryset = '', widget=forms.Select(attrs={'class':'hidden_cb'}))
    deal_5      =   forms.ModelChoiceField(required=False, queryset = '')#, widget=forms.Select(attrs={'class':'hidden_cb'}))   
    #status_5    =   forms.ModelChoiceField(required=False, queryset = '', widget=forms.Select(attrs={'class':'hidden_cb'}))
    deal_6      =   forms.ModelChoiceField(required=False, queryset = '')#, widget=forms.Select(attrs={'class':'hidden_cb'}))   
    #status_6    =   forms.ModelChoiceField(required=False, queryset = '', widget=forms.Select(attrs={'class':'hidden_cb'}))
    
    deal_show_row_1   = forms.BooleanField(required=False, initial=False)
    deal_show_row_2   = forms.BooleanField(required=False, initial=False)
    deal_show_row_3   = forms.BooleanField(required=False, initial=False)
    deal_show_row_4   = forms.BooleanField(required=False, initial=False)
    deal_show_row_5   = forms.BooleanField(required=False, initial=False)
    deal_show_row_6   = forms.BooleanField(required=False, initial=False)
    
    class Meta:
        model = Conversation
        exclude = ('company', 'contact')
        widgets = {
                    'contact_date': forms.DateInput(attrs={'placeholder': 'Add the date...', 'id': 'datepicker', 'class': 'placeholder_fix_css'}, format='%m/%d/%Y'),
                    'contact_time': forms.TimeInput(attrs={'placeholder': 'Add the time...',                     'class': 'placeholder_fix_css'}),
                    'subject': forms.TextInput(attrs={'placeholder': '',                                         'class': 'placeholder_fix_css'}),
                    'notes': forms.Textarea(attrs={'placeholder': 'Add relevant notes...'}),                                      
                   }
    
    def clean(self):
        cleaned_data = super(CallsForm, self).clean()
        deal_1 = cleaned_data.get('deal_1')
        deal_2 = cleaned_data.get('deal_2')
        deal_3 = cleaned_data.get('deal_3')
        deal_4 = cleaned_data.get('deal_4')
        deal_5 = cleaned_data.get('deal_5')
        deal_6 = cleaned_data.get('deal_6')
        
        deal_show_row_1 = cleaned_data.get('deal_show_row_1')
        deal_show_row_2 = cleaned_data.get('deal_show_row_2')
        deal_show_row_3 = cleaned_data.get('deal_show_row_3')
        deal_show_row_4 = cleaned_data.get('deal_show_row_4')
        deal_show_row_5 = cleaned_data.get('deal_show_row_5')
        deal_show_row_6 = cleaned_data.get('deal_show_row_6')
        
#        selection = [deal_show_row_1, deal_show_row_2, deal_show_row_3, deal_show_row_4, deal_show_row_5]
#        c = collections.Counter(selection)
#        duplicates = [i for i in c if c[i] > 1]

        duplicates = {}
        
        
        if deal_show_row_1:
            if deal_1:
                duplicates[deal_1.pk] = duplicates.get(deal_1.pk, 0) + 1
        if deal_show_row_2:
            if deal_2:
                duplicates[deal_2.pk] = duplicates.get(deal_2.pk, 0) + 1
        if deal_show_row_3:
            if deal_3:
                duplicates[deal_3.pk] = duplicates.get(deal_3.pk, 0) + 1
        if deal_show_row_4:
            if deal_4:
                duplicates[deal_4.pk] = duplicates.get(deal_4.pk, 0) + 1
        if deal_show_row_5:
            if deal_5:
                duplicates[deal_5.pk] = duplicates.get(deal_5.pk, 0) + 1
        if deal_show_row_6:
            if deal_6:
                duplicates[deal_6.pk] = duplicates.get(deal_6.pk, 0) + 1      
        
        #sorted_duplicates = sorted(duplicates.iteritems(), key=operator.itemgetter(1), reserve=True)
        
        msg_required = _(u'Please select a deal to add or remove it')
        msg_duplication = _(u'This deal has been selected more than once')
        
        if deal_show_row_1:
            if not deal_1:
                self._errors['deal_1'] = self.error_class([msg_required])
            else:
                if duplicates[deal_1.pk] > 1:
                    self._errors['deal_1'] = self.error_class([msg_duplication])
                                                    
        if deal_show_row_2:
            if not deal_2:
                self._errors['deal_2'] = self.error_class([msg_required])
            else:
                if duplicates[deal_2.pk] > 1:
                    self._errors['deal_2'] = self.error_class([msg_duplication])
        if deal_show_row_3:
            if not deal_3:
                self._errors['deal_3'] = self.error_class([msg_required])
            else:
                if duplicates[deal_3.pk] > 1:
                    self._errors['deal_3'] = self.error_class([msg_duplication])
                    
        if deal_show_row_4:
            if not deal_4:
                self._errors['deal_4'] = self.error_class([msg_required])
            else:
                if duplicates[deal_4.pk] > 1:
                    self._errors['deal_4'] = self.error_class([msg_duplication])
                    
        if deal_show_row_5:
            if not deal_5:
                self._errors['deal_5'] = self.error_class([msg_required])
            else:
                if duplicates[deal_5.pk] > 1:
                    self._errors['deal_5'] = self.error_class([msg_duplication])
                    
        if deal_show_row_6:
            if not deal_6:
                self._errors['deal_6'] = self.error_class([msg_required])
            else:
                if duplicates[deal_6.pk] > 1:
                    self._errors['deal_6'] = self.error_class([msg_duplication])
        return cleaned_data;
    
    
    
    def get_non_duplicate_deals(self, company, call):
        deals = Deal.objects.filter(company=company)
        duplicate_deals_pk = []
        for deal in deals:
            temp = Conversation_Deal.objects.filter(conversation=call, deal=deal)
            if temp:
                duplicate_deals_pk.append(temp[0].deal.pk)
        return deals.exclude(pk__in=duplicate_deals_pk)
            
        

class Conversation_DealForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(Conversation_DealForm, self).__init__(*args, **kwargs)
        
        class Meta:
            model = Conversation_Deal
        

class DealForm(ModelForm):
    #status2 = forms.TextInput()
    
    def __init__(self, *args, **kwargs):
        super(DealForm, self).__init__(*args, **kwargs)
#        instance = getattr(self, 'instance', None)
#        if instance and instance.pk:
        #self.fields['status'].widget.attrs['readonly'] = True
        #self.fields['status2'] = 'Hello'
        #self.fields['status'].widget = forms.TextInput(attrs={'readonly':'readonly'})
        
    
    def clean_status(self):
        return self.instance.status
        
            
    
    class Meta:
        model = Deal
        exclude = ('company', 'status')
        
        widgets = {
                    'deal_name': forms.TextInput(attrs={'placeholder': 'Name the deal', 'class': 'placeholder_fix_css'}),
                    'deal_description': forms.Textarea(attrs={'placeholder': 'Describe the deal'}),
#                    'sales_item': forms.TextInput(attrs={'placeholder': 'What are you buying or selling?', 'class': 'placeholder_fix_css'}),
                    'price': forms.TextInput(attrs={'placeholder': 'How much is proposed?', 'class': 'placeholder_fix_css'}),                    
#                    'sales_term': forms.TextInput(attrs={'placeholder': 'Is it fixed or recurring?', 'class': 'placeholder_fix_css'}),
                    'quantity': forms.TextInput(attrs={'placeholder': 'How many items?', 'class': 'placeholder_fix_css'}),
                    #'status': forms.TextInput(attrs={'placeholder': 'How is the progress?', 'class': 'placeholder_fix_css'}),    
                              
                   }


class SalesItemForm(ModelForm):
    class Meta:
        model = SalesItem
        exclude = ('company')

class CountryForm(ModelForm):
    class Meta:
        model = Country


class MaritalStatusForm(ModelForm):
    class Meta:
        model = MaritalStatus

class SalesTermForm(ModelForm):
    class Meta:
        model = SalesTerm

class ContactTypeForm(ModelForm):
    class Meta:
        model = ContactType
        #exclude = ('company')


