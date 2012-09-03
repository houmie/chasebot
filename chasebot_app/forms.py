from django.forms.forms import Form
from chasebot_app.widgets import cb_DateInput
from django.utils import timezone
import pytz
__author__ = 'houman'
from django.utils.datetime_safe import strftime
from django.contrib.localflavor.generic.forms import DateField
from django.forms.widgets import TextInput
from django.utils.formats import get_format
from django import forms
import re
import operator
import collections
from django.contrib.auth.models import User
from django.forms import ModelForm
from chasebot_app.models import UserProfile, Contact, ContactType, Country, MaritalStatus, Conversation, SalesItem, DealType, SalesTerm,\
    DealStatus, Deal
from django.forms.models import BaseModelFormSet
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


class FilterContactsForm(Form):
    last_name     = forms.CharField(widget= forms.TextInput(attrs={'placeholder': 'Filter here...', 'class': 'placeholder_fix_css input-small search-query'}), max_length=50)
    first_name    = forms.CharField(widget= forms.TextInput(attrs={'placeholder': 'Filter here...', 'class': 'placeholder_fix_css input-small search-query'}), max_length=30)
    company       = forms.CharField(widget= forms.TextInput(attrs={'placeholder': 'Filter here...', 'class': 'placeholder_fix_css input-small search-query'}), max_length=30)
    email         = forms.EmailField(widget= forms.TextInput(attrs={'placeholder': 'Filter here...', 'class': 'placeholder_fix_css input-small search-query'}))

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
                'birth_date': forms.DateInput(  attrs={'placeholder': 'Add the day of birth',           'class': 'placeholder_fix_css datepicker'}),
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




class FilterCallsForm(Form):            
    from_date   = forms.DateField(localize=True, widget=cb_DateInput(attrs={'placeholder': 'From Date...', 'class': 'placeholder_fix_css datepicker input-small search-query', }))
    to_date     = forms.DateField(localize=True, widget=cb_DateInput(attrs={'placeholder': 'To Date...', 'class': 'placeholder_fix_css datepicker input-small search-query'}))
    subject     = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Filter here...', 'class': 'placeholder_fix_css input-small search-query'}), max_length=50)
    
    
    
class CallsForm(ModelForm):       
    conversation_date = forms.DateField(localize=True, widget=forms.DateInput(attrs={'placeholder': 'Add the date for this conversation', 'class': 'placeholder_fix_css datepicker'}))
    conversation_time = forms.TimeField(localize=True, widget=forms.TimeInput(attrs={'placeholder': 'Add the time for this conversation', 'class': 'placeholder_fix_css'}))
    
    def __init__(self, company, *args, **kwargs):
        super(CallsForm, self).__init__(*args, **kwargs)                                        
        self.fields['deal_1'].queryset = self.get_non_open_deals(self.instance, company)        
        self.fields['deal_2'].queryset = self.get_non_open_deals(self.instance, company)
        self.fields['deal_3'].queryset = self.get_non_open_deals(self.instance, company)        
        self.fields['deal_4'].queryset = self.get_non_open_deals(self.instance, company)        
        self.fields['deal_5'].queryset = self.get_non_open_deals(self.instance, company)        
        self.fields['deal_6'].queryset = self.get_non_open_deals(self.instance, company)
        local_tz = timezone.get_current_timezone()
        self.fields['conversation_date'].initial = self.instance.conversation_datetime.replace(tzinfo=pytz.utc).astimezone(local_tz).date()
        self.fields['conversation_time'].initial = self.instance.conversation_datetime.replace(tzinfo=pytz.utc).astimezone(local_tz).time()         
    
        
    deal_1      =   forms.ModelChoiceField(required=False, queryset = '')     
    deal_2      =   forms.ModelChoiceField(required=False, queryset = '')    
    deal_3      =   forms.ModelChoiceField(required=False, queryset = '')    
    deal_4      =   forms.ModelChoiceField(required=False, queryset = '')    
    deal_5      =   forms.ModelChoiceField(required=False, queryset = '')    
    deal_6      =   forms.ModelChoiceField(required=False, queryset = '')   
    
    deal_show_row_1   = forms.BooleanField(required=False, initial=False)
    deal_show_row_2   = forms.BooleanField(required=False, initial=False)
    deal_show_row_3   = forms.BooleanField(required=False, initial=False)
    deal_show_row_4   = forms.BooleanField(required=False, initial=False)
    deal_show_row_5   = forms.BooleanField(required=False, initial=False)
    deal_show_row_6   = forms.BooleanField(required=False, initial=False)
    
    class Meta:
        model = Conversation
        exclude = ('company', 'contact', 'conversation_datetime')
        widgets = {                    
                    'subject': forms.TextInput(attrs={'placeholder': '', 'class': 'placeholder_fix_css'}),
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
    
    
    
    def get_non_open_deals(self, call, company):
#        all_deals = Deal.objects.filter(contact=call.contact)            
#        closed_deals = all_deals.filter(status__in=[5, 6])
#        closed_deal_list = []
#        if closed_deals:
#            for item in closed_deals:
#                closed_deal_list.append(item.deal_id)        
#        open_deals = all_deals.exclude(deal_id__in=closed_deal_list)#.latest('time_stamp')
        open_deals = call.contact.get_open_deals()
        open_deal_list = []
        if open_deals:
            for item in open_deals:
                open_deal_list.append(item.deal_type.pk)
        deal_types = DealType.objects.filter(company=company)            
        return deal_types.exclude(pk__in=open_deal_list)
            

class FilterDealsForm(Form):
    def __init__(self, company, *args, **kwargs):
        super(FilterDealsForm, self).__init__(*args, **kwargs)
        self.fields['sales_item'].queryset = SalesItem.objects.filter(company=company)
            
    deal_name           = forms.CharField(widget = forms.TextInput(attrs={'placeholder': 'Filter here...', 'class': 'placeholder_fix_css input-small search-query'}), max_length=40)    
    sales_item          = forms.ModelMultipleChoiceField(queryset='', widget = forms.TextInput(attrs={'placeholder': 'Filter here...', 'class': 'placeholder_fix_css input-small search-query'}))    
    price               = forms.DecimalField(widget = forms.TextInput(attrs={'placeholder': 'Filter here...', 'class': 'placeholder_fix_css input-small search-query'}))
    sales_term          = forms.ModelChoiceField(queryset=SalesTerm.objects.all(), widget = forms.TextInput(attrs={'placeholder': 'Filter here...', 'class': 'placeholder_fix_css input-small search-query'}))
    quantity            = forms.IntegerField(widget = forms.TextInput(attrs={'placeholder': 'Filter here...', 'class': 'placeholder_fix_css input-small search-query'})) 



class DealTypeForm(ModelForm):    
    def __init__(self, *args, **kwargs):
        super(DealTypeForm, self).__init__(*args, **kwargs)
        self.fields['sales_item'].queryset = SalesItem.objects.filter(company=self.instance.company)                
    
    class Meta:
        model = DealType
        exclude = ('company', 'status')
        
        widgets = {
                    'deal_name': forms.TextInput(attrs={'placeholder': 'Name the deal', 'class': 'placeholder_fix_css'}),
                    'deal_description': forms.Textarea(attrs={'placeholder': 'Describe the deal'}),
                    'sales_item': forms.SelectMultiple(attrs={'data-placeholder': 'What are you buying or selling?'}),
                    #'sales_item': ChosenSelectMultiple(), #(attrs={'data-placeholder': 'What are you buying or selling?'}),
                    'price': forms.TextInput(attrs={'placeholder': 'How much is proposed?', 'class': 'placeholder_fix_css'}),                    
#                    'sales_term': forms.TextInput(attrs={'placeholder': 'Is it fixed or recurring?', 'class': 'placeholder_fix_css'}),
                    'quantity': forms.TextInput(attrs={'placeholder': 'How many items?', 'class': 'placeholder_fix_css'}),
                    #'status': forms.TextInput(attrs={'placeholder': 'How is the progress?', 'class': 'placeholder_fix_css'}),                              
                   }

class DealForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(DealForm, self).__init__(*args, **kwargs)            
        self.fields['status'].widget.attrs['class'] = 'select select_status'
        
    class Meta:
        model = Deal
        fields = {'deal_type', 'status'}
    
    def clean_status(self):
        status = self.cleaned_data['status']
        if status.pk == 5 or status.pk == 6:                
            #deal = self.save(commit=False)
            latest_deal = self.instance.contact.deal_set.filter(deal_id = self.instance.deal_id).latest('time_stamp')
            if self.instance.pk != latest_deal.pk:
                raise forms.ValidationError(_(u'You cannot set a past deal to Win/Lost, as there is already a "%s" deal status recorded on ' % latest_deal.status)  + str(latest_deal.conversation.conversation_datetime))
        return status
        
class DealCForm(ModelForm):
    attach_deal_conversation  = forms.BooleanField(required=False, initial=False)
    
    def __init__(self, *args, **kwargs):
        super(DealCForm, self).__init__(*args, **kwargs)           
        self.fields['deal_instance_name'].widget.attrs['readonly'] = 'True'
        self.fields['status'].widget.attrs['class'] = 'select select_status'
    
    class Meta:
        model = Deal
        fields = {'deal_instance_name', 'status', 'attach_deal_conversation'}
    

class FilterSalesItemForm(Form):
    def __init__(self, *args, **kwargs):
        super(FilterSalesItemForm, self).__init__(*args, **kwargs)          
    
    item_description    = forms.CharField(widget = forms.TextInput(attrs={'placeholder': 'Filter here...', 'class': 'placeholder_fix_css input-small search-query filter_add_button'}), max_length=40)

class SalesItemForm(ModelForm):
    class Meta:
        model = SalesItem
        exclude = ('company')
        widgets = {
                   'item_description': forms.TextInput(attrs={'class': 'item_description'}),
                   }
        
    


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

class BaseDealFormSet(BaseModelFormSet):    
    def clean(self):
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return
        deal_types = []
        for form in self.forms:
            
            deal_type = form.cleaned_data['deal_type']
            if deal_type in deal_types:
                raise forms.ValidationError(_(u'Please correct the duplicated deal types attached to this conversation.'))
            deal_types.append(deal_type)
            
            
                
            
        
   
  