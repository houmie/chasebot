__author__ = 'houman'
from django.forms.forms import Form
from chasebot_app.widgets import cb_DateInput
from django.utils import timezone
import pytz
from django import forms
import re
from django.contrib.auth.models import User
from django.forms import ModelForm
from chasebot_app.models import UserProfile, Contact, ContactType, Country, MaritalStatus, Conversation, SalesItem, DealTemplate, SalesTerm, Deal
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
        raise forms.ValidationError(_(u'Passwords do not match.'))

    def clean_username(self):
        username = self.cleaned_data['username']
        if not re.search(r'^\w+$', username):
            raise forms.ValidationError(_(u'Username can only contain alphanumeric characters and the underscore.'))
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(_(u'Username is already taken.'))

    def clean_email(self):
        email = self.cleaned_data['email']
        users = User.objects.filter(email=email)
        if users.count() > 0:
            raise forms.ValidationError(_(u"That email is already taken, please select another."))
        return email


class FilterContactsForm(Form):
    last_name     = forms.CharField(widget= forms.TextInput(attrs={'placeholder': _(u'Filter here...'), 'class': 'placeholder_fix_css input-small search-query typeahead_contacts_last_name', 'autocomplete': 'off', 'data-provide': 'typeahead'}), max_length=50)
    first_name    = forms.CharField(widget= forms.TextInput(attrs={'placeholder': _(u'Filter here...'), 'class': 'placeholder_fix_css input-small search-query typeahead_contacts_first_name', 'autocomplete': 'off', 'data-provide': 'typeahead'}), max_length=30)
    company       = forms.CharField(widget= forms.TextInput(attrs={'placeholder': _(u'Filter here...'), 'class': 'placeholder_fix_css input-small search-query typeahead_contacts_company', 'autocomplete': 'off', 'data-provide': 'typeahead'}), max_length=30)
    email         = forms.EmailField(widget= forms.TextInput(attrs={'placeholder': _(u'Filter here...'), 'class': 'placeholder_fix_css input-small search-query typeahead_contacts_email', 'autocomplete': 'off', 'data-provide': 'typeahead'}))

class ContactsForm(ModelForm):
    def __init__(self, company, *args, **kwargs):
        super(ContactsForm, self).__init__(*args, **kwargs)
        # limit selection list to just items for this account
        #self.fields['contact_type'].queryset = ContactType.objects.filter(company=company)

    class Meta:
        model = Contact
        exclude = ('company')
        widgets = {
                'first_name': forms.TextInput(  attrs={'placeholder': _(u'Enter first name here'),      'class': 'placeholder_fix_css', 'autocomplete': 'off'}),
                'last_name': forms.TextInput(   attrs={'placeholder': _(u'Enter last name here'),       'class': 'placeholder_fix_css', 'autocomplete': 'off'}),
                'dear_name': forms.TextInput(   attrs={'placeholder': _(u'Enter preferred short name'), 'class': 'placeholder_fix_css', 'autocomplete': 'off'}),
                'city': forms.TextInput(        attrs={'placeholder': _(u'Enter the city here'),        'class': 'placeholder_fix_css', 'autocomplete': 'off'}),
                'state': forms.TextInput(       attrs={'placeholder': _(u'Enter the state here'),       'class': 'placeholder_fix_css', 'autocomplete': 'off'}),
                'postcode': forms.TextInput(    attrs={'placeholder': _(u'Enter the zip code here'),    'class': 'placeholder_fix_css', 'autocomplete': 'off'}),
                'company_name': forms.TextInput(attrs={'placeholder': _(u'Add a company'),              'class': 'placeholder_fix_css', 'autocomplete': 'off'}),
                'position': forms.TextInput(    attrs={'placeholder': _(u'Add a position'),             'class': 'placeholder_fix_css', 'autocomplete': 'off'}),
                'work_phone': forms.TextInput(  attrs={'placeholder': _(u'Add a work phone'),           'class': 'placeholder_fix_css', 'autocomplete': 'off'}),
                'home_phone': forms.TextInput(  attrs={'placeholder': _(u'Add a home phone'),           'class': 'placeholder_fix_css', 'autocomplete': 'off'}),
                'mobile_phone': forms.TextInput(attrs={'placeholder': _(u'Add a cell phone'),           'class': 'placeholder_fix_css', 'autocomplete': 'off'}),
                'fax_number': forms.TextInput(  attrs={'placeholder': _(u'Add a fax number'),           'class': 'placeholder_fix_css', 'autocomplete': 'off'}),
                'email': forms.TextInput(       attrs={'placeholder': _(u'Add an email'),               'class': 'placeholder_fix_css', 'autocomplete': 'off'}),
                'birth_date': forms.DateInput(  attrs={'placeholder': _(u'Add the birthday'),           'class': 'placeholder_fix_css datepicker'}),
                'referred_by': forms.TextInput( attrs={'placeholder': _(u'...was referred by?'),        'class': 'placeholder_fix_css', 'autocomplete': 'off'}),
                'spouse_first_name': forms.TextInput(attrs={'placeholder': _(u'What is the spouse\'s name?'), 'class': 'placeholder_fix_css', 'autocomplete': 'off'}),
                'children_names': forms.TextInput(attrs={'placeholder': _(u'What are the children names?'), 'class': 'placeholder_fix_css', 'autocomplete': 'off'}),
                'home_town': forms.TextInput(   attrs={'placeholder': _(u'Enter the home town'),            'class': 'placeholder_fix_css', 'autocomplete': 'off'}),
                'address': forms.Textarea(      attrs={'rows':4, 'placeholder': _(u'Add an address'),       'class': 'placeholder_fix_css'}),
                'contact_notes': forms.Textarea(attrs={'rows':4, 'placeholder': _(u'What is the personality like?')}),
                'contacts_interests': forms.Textarea(attrs={'rows':4, 'placeholder': _(u'Any particular interests?')}),
                'spouses_interests': forms.Textarea(attrs={'rows':4, 'placeholder': _(u'Does the spouse have any particular interest?')}),
                'prev_meeting_places': forms.Textarea(attrs={'rows':4, 'placeholder': _(u'Where did you meet so far?')})                       
            }




class FilterConversationForm(Form):            
    from_date   = forms.DateField(localize=True, widget=cb_DateInput(attrs={'placeholder': _(u'From Date...'), 'class': 'placeholder_fix_css datepicker input-small search-query'}))
    to_date     = forms.DateField(localize=True, widget=cb_DateInput(attrs={'placeholder': _(u'To Date...'), 'class': 'placeholder_fix_css datepicker input-small search-query'}))
    subject     = forms.CharField(widget=forms.TextInput(attrs={'placeholder': _(u'Filter here...'), 'class': 'placeholder_fix_css input-small search-query typeahead_conversation_subject', 'autocomplete': 'off', 'data-provide': 'typeahead'}), max_length=50)
    
    
    
class ConversationForm(ModelForm):       
    conversation_date = forms.DateField(localize=True, widget=forms.DateInput(attrs={'placeholder': _(u'Add the date for this conversation'), 'class': 'placeholder_fix_css datepicker'}))
    conversation_time = forms.TimeField(localize=True, widget=forms.TimeInput(attrs={'placeholder': _(u'Add the time for this conversation'), 'class': 'placeholder_fix_css'}))
    
    def __init__(self, company, *args, **kwargs):
        super(ConversationForm, self).__init__(*args, **kwargs)        
        local_tz = timezone.get_current_timezone()
        self.fields['conversation_date'].initial = self.instance.conversation_datetime.replace(tzinfo=pytz.utc).astimezone(local_tz).date()
        self.fields['conversation_time'].initial = self.instance.conversation_datetime.replace(tzinfo=pytz.utc).astimezone(local_tz).time()    
    
    class Meta:
        model = Conversation
        exclude = ('company', 'contact', 'conversation_datetime')
        widgets = {                    
                    'subject': forms.TextInput(attrs={'placeholder': '', 'class': 'placeholder_fix_css', 'autocomplete': 'off'}),
                    'notes': forms.Textarea(attrs={'placeholder': _(u'Add relevant notes...')}),                                      
                   }
    
    def get_non_open_deals(self, call, company):
        open_deals = call.contact.get_open_deals()
        open_deal_list = []
        if open_deals:
            for item in open_deals:
                open_deal_list.append(item.deal_template.pk)
        deal_templates = DealTemplate.objects.filter(company=company)            
        return deal_templates.exclude(pk__in=open_deal_list)


class DealsAddForm(Form):
    def __init__(self, company, call, contact, *args, **kwargs):
        super(DealsAddForm, self).__init__(*args, **kwargs)        
        exclude_list = []
        # The following are all deals attached to this calls.
        attached_deals_to_call_query = call.deal_set.all()
        opendeals_query = get_open_deals_query(contact) 
        #The dropdown should not show templates, whos instances are still open but not yet attached. Only negotiate a new deal, if the existing deals are closed.  
        for deal in opendeals_query:
            exclude_list.append(deal.deal_template.pk)
        #The dropdown should also not show templates, whos instances are attached to this call.
        for deal in attached_deals_to_call_query:
            exclude_list.append(deal.deal_template.pk)
        self.fields['deal_template'].queryset = company.dealtemplate_set.exclude(id__in=exclude_list)
        self.fields['deal_template'].required = False
 
    deal_template       = forms.ModelChoiceField(queryset='', label=_(u'Negotiate a New Deal'))


def get_open_deals_query(contact):
    raw = contact.get_open_deals() # The following are all open deals (not status 5 or 6) that are attached to the whole contact
    opendeals_query = contact.deal_set.filter(id__in=[item.id for item in raw])
    return opendeals_query



class OpenDealsAddForm(Form):
    def __init__(self, company, call, contact, *args, **kwargs):
        super(OpenDealsAddForm, self).__init__(*args, **kwargs)
        exclude_attached_opendeals = []
        # The following are all deals attached to this calls.
        attached_deals_to_call_query = call.deal_set.all()
        opendeals_query = get_open_deals_query(contact) 
        for attached_deal in attached_deals_to_call_query:
            # Now we search if any open deals is already attached to this call, if so it shall be excluded
            # in the open deal drop down for this call.
            for open_deal in opendeals_query:
                if attached_deal.deal_id == open_deal.deal_id:
                    exclude_attached_opendeals.append(open_deal.deal_id)                            
        self.fields['open_deal_template'].queryset = opendeals_query.exclude(deal_id__in=exclude_attached_opendeals)
        self.fields['open_deal_template'].required = False
 
    open_deal_template = forms.ModelChoiceField(queryset='', label=_(u'Continue with a Deal in Progress'))

    
    


class FilterDealsForm(Form):
    def __init__(self, company, *args, **kwargs):
        super(FilterDealsForm, self).__init__(*args, **kwargs)
        self.fields['sales_item'].queryset = SalesItem.objects.filter(company=company)
            
    deal_name           = forms.CharField(widget = forms.TextInput(attrs={'placeholder': _(u'Filter here...'), 'class': 'placeholder_fix_css input-small search-query typeahead_deals_deal_name', 'autocomplete': 'off', 'data-provide': 'typeahead'}), max_length=40)    
    sales_item          = forms.ModelMultipleChoiceField(queryset='', widget = forms.TextInput(attrs={'placeholder': _(u'Filter here...'), 'class': 'placeholder_fix_css input-small search-query typeahead_deals_sales_item', 'autocomplete': 'off', 'data-provide': 'typeahead'}))    
    price               = forms.DecimalField(widget = forms.TextInput(attrs={'placeholder': _(u'Filter here...'), 'class': 'placeholder_fix_css input-small search-query typeahead_deals_price', 'autocomplete': 'off', 'data-provide': 'typeahead'}))
    sales_term          = forms.ModelChoiceField(queryset=SalesTerm.objects.all(), widget = forms.TextInput(attrs={'placeholder': _(u'Filter here...'), 'class': 'placeholder_fix_css input-small search-query typeahead_deals_sales_term', 'autocomplete': 'off', 'data-provide': 'typeahead'}))
    quantity            = forms.IntegerField(widget = forms.TextInput(attrs={'placeholder': _(u'Filter here...'), 'class': 'placeholder_fix_css input-small search-query typeahead_deals_quantity', 'autocomplete': 'off', 'data-provide': 'typeahead'})) 



class DealTemplateForm(ModelForm):    
    def __init__(self, *args, **kwargs):
        super(DealTemplateForm, self).__init__(*args, **kwargs)
        self.fields['sales_item'].queryset = SalesItem.objects.filter(company=self.instance.company)                
        self.fields['sales_item'].widget.attrs['class'] = 'sales_item'
    
    def clean_quantity(self):
        if 'quantity' in self.cleaned_data:
            quantity = self.cleaned_data['quantity']            
            if quantity > 0:
                return quantity
        raise forms.ValidationError(_(u'Ensure this value is greater than %(number)s.') % {'number': 0})
    
    class Meta:
        model = DealTemplate
        exclude = ('company', 'status')
        
        widgets = {
                    'deal_name': forms.TextInput(attrs={'placeholder': _(u'Name the deal'), 'class': 'placeholder_fix_css', 'autocomplete': 'off'}),
                    'deal_description': forms.Textarea(attrs={'placeholder': _(u'Describe the deal')}),
                    'sales_item': forms.SelectMultiple(attrs={'data-placeholder': _(u'What are you buying or selling?')}),
                    #'sales_item': ChosenSelectMultiple(), #(attrs={'data-placeholder': _(u'What are you buying or selling?')}),
                    'price': forms.TextInput(attrs={'placeholder': _(u'How much is proposed?'), 'class': 'placeholder_fix_css', 'autocomplete': 'off'}),                    
#                    'sales_term': forms.TextInput(attrs={'placeholder': _(u'Is it fixed or recurring?'), 'class': 'placeholder_fix_css'}),
                    'quantity': forms.TextInput(attrs={'placeholder': _(u'How many items?'), 'class': 'placeholder_fix_css', 'autocomplete': 'off'}),
                    #'status': forms.TextInput(attrs={'placeholder': _(u'How is the progress?'), 'class': 'placeholder_fix_css'}),                              
                   }
        
class DealForm(ModelForm):
    attached_open_deal_id  = forms.IntegerField(required=False)    
    is_last_active_tab = forms.BooleanField(required=False)    
    
    def __init__(self, *args, **kwargs):
        super(DealForm, self).__init__(*args, **kwargs)                       
        self.fields['status'].widget.attrs['class'] = 'select select_status'        
        self.fields['deal_instance_name'].widget.attrs['readonly'] = 'True'
        self.fields['deal_template_name'].widget.attrs.update({'readonly' : 'True'})
        self.fields['deal_template'].widget.attrs['class'] = 'hidden'
        self.fields['is_last_active_tab'].widget.attrs['class'] = 'last_active_tab'
    
    class Meta:
        model = Deal
        fields = {'deal_template', 'deal_template_name', 'deal_instance_name', 'status', 
                  'deal_description', 'sales_item', 'price', 'sales_term', 'quantity', 
                  'is_last_active_tab'}
        

    

class FilterSalesItemForm(Form):
    def __init__(self, *args, **kwargs):
        super(FilterSalesItemForm, self).__init__(*args, **kwargs)          
    
    item_name    = forms.CharField(widget = forms.TextInput(attrs={'placeholder': _(u'Filter here...'), 'class': 'placeholder_fix_css input-small search-query filter_add_button typeahead_sales_items', 'autocomplete': 'off', 'data-provide': 'typeahead'}), max_length=40)

class SalesItemForm(ModelForm):
    class Meta:
        model = SalesItem
        exclude = ('company')
        widgets = {
                   'item_name': forms.TextInput(attrs={'class': 'item_name', 'autocomplete': 'off'}),
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
        deal_templates = []
        for form in self.forms:
            
            deal_template = form.cleaned_data['deal_template']
            if deal_template in deal_templates:
                raise forms.ValidationError(_(u'Please correct the duplicated deal types attached to this conversation.'))
            deal_templates.append(deal_template)
            
            
                
            
        
   
  