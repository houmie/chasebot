__author__ = 'houman'

from django.forms.forms import Form
from chasebot_app.widgets import cb_DateInput
from django.utils import timezone
import pytz
from django import forms
import re
from django.contrib.auth.models import User
from django.forms import ModelForm
from chasebot_app.models import Contact, MaritalStatus, Conversation, SalesItem, DealTemplate, SalesTerm, Deal,\
    Invitation, Task, Event, DealStatus
from django.forms.models import BaseModelFormSet
from django.utils.translation import ugettext_lazy as _
import datetime

   
    
class UserRegistrationForm(Form):
    username        = forms.CharField(widget=forms.TextInput(attrs={'placeholder': _(u'Enter a memorable username...')}), label = _(u'Username'), max_length=30)
    email           = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': _(u'Enter your email address...')}), label= _(u'Email'))
    password        = forms.CharField(label = _(u'Password'), widget=forms.PasswordInput(render_value=False,attrs={'placeholder': _(u'Enter a memorable password...')}))
    password2       = forms.CharField(label = _(u'Password (retype)'), widget=forms.PasswordInput(render_value=False, attrs={'placeholder': _(u'Retype your password...')}))    
    timezone        = forms.ChoiceField(choices=[(x, x) for x in pytz.common_timezones], initial='US/Eastern')

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
            raise forms.ValidationError(_(u"The email is already taken, please select another."))
        return email

class RegistrationForm(UserRegistrationForm):
    def __init__(self, *args, **kwargs):
        company_name = kwargs.pop('_company_name', None)
        company_email = kwargs.pop('_company_email', None)
        email = kwargs.pop('_email', None)
        is_accept_invite = kwargs.pop('is_accept_invite', None)
        super(RegistrationForm, self).__init__(*args, **kwargs)
        if is_accept_invite:                        
            self.fields['company_name'].required = False;
            self.fields['company_email'].required = False;
            self.fields['company_name'].widget.attrs['readonly'] = True
            self.fields['company_email'].widget.attrs['readonly'] = True
            self.fields['company_name'].initial = company_name
            self.fields['company_email'].initial = company_email
            self.fields['email'].initial = email
        
    company_name    = forms.CharField(label = _(u'Company'), max_length=50)
    company_email   = forms.EmailField(label= _(u'Company Email'))    

class FilterContactsForm(Form):
    last_name     = forms.CharField(widget= forms.TextInput(attrs={'placeholder': _(u'Filter here...'), 'class': 'placeholder_fix_css input-small search-query typeahead_contacts_last_name', 'autocomplete': 'off', 'data-provide': 'typeahead'}), max_length=50)
    first_name    = forms.CharField(widget= forms.TextInput(attrs={'placeholder': _(u'Filter here...'), 'class': 'placeholder_fix_css input-small search-query typeahead_contacts_first_name', 'autocomplete': 'off', 'data-provide': 'typeahead'}), max_length=30)
    company       = forms.CharField(widget= forms.TextInput(attrs={'placeholder': _(u'Filter here...'), 'class': 'placeholder_fix_css input-small search-query typeahead_contacts_company', 'autocomplete': 'off', 'data-provide': 'typeahead'}), max_length=30)
    email         = forms.EmailField(widget= forms.TextInput(attrs={'placeholder': _(u'Filter here...'), 'class': 'placeholder_fix_css input-small search-query typeahead_contacts_email', 'autocomplete': 'off', 'data-provide': 'typeahead'}))

class ContactsForm(ModelForm): 
    def clean(self):
        cleaned_data = super(ContactsForm, self).clean()
        company_name = self.cleaned_data['company_name']
        last_name = self.cleaned_data['last_name']
        
        if not company_name and not last_name:
            msg = _(u'Either the last name OR the company name are required.')
            self._errors["company_name"] = self.error_class([msg])
            self._errors["last_name"] = self.error_class([msg])
            del cleaned_data['company_name']
            del cleaned_data['last_name']
        
        return cleaned_data
      
    class Meta:
        model = Contact
        exclude = ('company')
        widgets = {
                'first_name': forms.TextInput(  attrs={'placeholder': _(u'Enter first name here'),      'class': 'placeholder_fix_css', 'autocomplete': 'off'}),
                'last_name': forms.TextInput(   attrs={'placeholder': _(u'Enter last name here'),       'class': 'placeholder_fix_css fillone', 'autocomplete': 'off'}),
                'dear_name': forms.TextInput(   attrs={'placeholder': _(u'Enter preferred short name'), 'class': 'placeholder_fix_css', 'autocomplete': 'off'}),
                'city': forms.TextInput(        attrs={'placeholder': _(u'Enter the city here'),        'class': 'placeholder_fix_css', 'autocomplete': 'off'}),
                'state': forms.TextInput(       attrs={'placeholder': _(u'Enter the state here'),       'class': 'placeholder_fix_css', 'autocomplete': 'off'}),
                'postcode': forms.TextInput(    attrs={'placeholder': _(u'Enter the zip code here'),    'class': 'placeholder_fix_css', 'autocomplete': 'off'}),
                'company_name': forms.TextInput(attrs={'placeholder': _(u'Add a company'),              'class': 'placeholder_fix_css fillone', 'autocomplete': 'off'}),
                'position': forms.TextInput(    attrs={'placeholder': _(u'Add a position'),             'class': 'placeholder_fix_css', 'autocomplete': 'off'}),
                'phone': forms.TextInput(       attrs={'placeholder': _(u'Add a phone number'),         'class': 'placeholder_fix_css', 'autocomplete': 'off'}),
                'mobile_phone': forms.TextInput(attrs={'placeholder': _(u'Add a cell phone number'),    'class': 'placeholder_fix_css', 'autocomplete': 'off'}),
                'fax_number': forms.TextInput(  attrs={'placeholder': _(u'Add a fax number'),           'class': 'placeholder_fix_css', 'autocomplete': 'off'}),
                'email': forms.TextInput(       attrs={'placeholder': _(u'Add an email'),               'class': 'placeholder_fix_css email', 'autocomplete': 'off'}),
                'birth_date': forms.DateInput(  attrs={'placeholder': _(u'Add the birthday'),           'class': 'placeholder_fix_css date_picker'}),
                'referred_by': forms.TextInput( attrs={'placeholder': _(u'...was referred by?'),        'class': 'placeholder_fix_css', 'autocomplete': 'off'}),
                'spouse_first_name': forms.TextInput(attrs={'placeholder': _(u'What is the spouse\'s name?'), 'class': 'placeholder_fix_css', 'autocomplete': 'off'}),
                'children_names': forms.TextInput(attrs={'placeholder': _(u'What are the children names?'), 'class': 'placeholder_fix_css', 'autocomplete': 'off'}),
                'home_town': forms.TextInput(   attrs={'placeholder': _(u'Enter the home town'),            'class': 'placeholder_fix_css', 'autocomplete': 'off'}),
                'address': forms.Textarea(      attrs={'rows':4, 'placeholder': _(u'Add an address'),       'class': 'placeholder_fix_css textarea_15_5em'}),
                'contact_notes': forms.Textarea(attrs={'rows': 4, 'cols': 50, 'placeholder': _(u'What is the personality like?')}),
                'contacts_interests': forms.Textarea(attrs={'rows':4, 'class':'textarea_15em', 'placeholder': _(u'Any particular interests?')}),
                'pet_names': forms.TextInput( attrs={'placeholder': _(u'Has any pets?'),        'class': 'placeholder_fix_css', 'autocomplete': 'off'}),
                'spouses_interests': forms.Textarea(attrs={'rows':4, 'class':'textarea_15em', 'placeholder': _(u'Does the spouse have any particular interest?')}),
                'prev_meeting_places': forms.Textarea(attrs={'rows':4, 'class':'textarea_15em', 'placeholder': _(u'Where did you meet so far?')}), 
                'important_client': forms.RadioSelect()
            }
        
        

        




class FilterConversationForm(Form):            
    from_date   = forms.DateField(localize=True, widget=cb_DateInput(attrs={'placeholder': _(u'From Date...'), 'class': 'placeholder_fix_css date_picker input-small search-query'}))
    to_date     = forms.DateField(localize=True, widget=cb_DateInput(attrs={'placeholder': _(u'To Date...'), 'class': 'placeholder_fix_css date_picker input-small search-query'}))

    
    
    
class ConversationForm(ModelForm):       
    conversation_date = forms.DateField(label='Date', localize=True, widget=forms.DateInput(attrs={'placeholder': _(u'Add the date for this conversation'), 'class': 'placeholder_fix_css date_picker cb_date_maxwidth'}))
    conversation_time = forms.TimeField(label='Time', localize=True, widget=forms.TimeInput(attrs={'placeholder': _(u'Add the time for this conversation'), 'class': 'placeholder_fix_css cb_time_maxwidth'}))
    
    def __init__(self, company, *args, **kwargs):
        super(ConversationForm, self).__init__(*args, **kwargs)        
        local_tz = timezone.get_current_timezone()
        self.fields['conversation_date'].initial = self.instance.conversation_datetime.replace(tzinfo=pytz.utc).astimezone(local_tz).date()
        self.fields['conversation_time'].initial = self.instance.conversation_datetime.replace(tzinfo=pytz.utc).astimezone(local_tz).time()    
    
    class Meta:
        model = Conversation
        exclude = ('company', 'contact', 'conversation_datetime')
        widgets = {                    
                    'notes': forms.Textarea(attrs={'placeholder': _(u'Add relevant notes...'), 'class' : 'cb_notes_maxwidth'}),                                      
                   }

    def clean(self):
        cleaned_data = super(ConversationForm, self).clean()
        if 'conversation_date' in self.cleaned_data and 'conversation_time' in self.cleaned_data:
            call_date = self.cleaned_data['conversation_date']
            call_time = self.cleaned_data['conversation_time']
    
            current_tz = timezone.get_current_timezone() 
            date_time = current_tz.localize(datetime.datetime(call_date.year, call_date.month, call_date.day, call_time.hour, call_time.minute))
            if date_time.date() > timezone.now().replace(tzinfo=pytz.utc).astimezone(current_tz).date():            
                self._errors["conversation_date"] = self.error_class([_(u'A conversation date can not take place in future.')])
                del cleaned_data['conversation_date']
            if date_time.time() > timezone.now().replace(tzinfo=pytz.utc).astimezone(current_tz).time():
                self._errors["conversation_time"] = self.error_class([_(u'A conversation time can not take place in future.')])            
                del cleaned_data['conversation_time']        
        return cleaned_data
    
    def get_non_open_deals(self, call, company):
        open_deals = call.contact.get_raw_open_deals()
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
        opendeals_query = contact.get_open_deals_query() 
        #The dropdown should not show templates, whos instances are still open but not yet attached. Only negotiate a new deal, if the existing deals are closed.  
        for deal in opendeals_query:
            if deal.deal_template:
                exclude_list.append(deal.deal_template.pk)
        #The dropdown should also not show templates, whos instances are attached to this call.
        for deal in attached_deals_to_call_query:
            if deal.deal_template:
                exclude_list.append(deal.deal_template.pk)
        self.fields['deal_template'].queryset = company.dealtemplate_set.exclude(id__in=exclude_list)
        self.fields['deal_template'].required = False
 
    deal_template       = forms.ModelChoiceField(queryset='', label=_(u'Add new from template'), widget = forms.Select(attrs={'class': 'pre_defined_deal_dropdown'}))






class OpenDealsAddForm(Form):
    def __init__(self, company, call, contact, *args, **kwargs):
        super(OpenDealsAddForm, self).__init__(*args, **kwargs)
        exclude_attached_opendeals = []
        # The following are all deals attached to this calls.
        attached_deals_to_call_query = call.deal_set.all()
        opendeals_query = contact.get_open_deals_query() 
        for attached_deal in attached_deals_to_call_query:
            # Now we search if any open deals is already attached to this call, if so it shall be excluded
            # in the open deal drop down for this call.
            for open_deal in opendeals_query:
                if attached_deal.deal_id == open_deal.deal_id:
                    exclude_attached_opendeals.append(open_deal.deal_id)                            
        self.fields['open_deal_template'].queryset = opendeals_query.exclude(deal_id__in=exclude_attached_opendeals)
        self.fields['open_deal_template'].required = False
 
    open_deal_template = forms.ModelChoiceField(queryset='', label=_(u'Continue with a deal in progress'))


class OpenDealTaskForm(Form):
    def __init__(self, contact, dealid, *args, **kwargs):
        super(OpenDealTaskForm, self).__init__(*args, **kwargs)        
        if contact:
            self.fields['open_deal_task'].queryset = contact.get_open_deals_query()
            if dealid:
                try:
                    self.fields['open_deal_task'].initial = self.fields['open_deal_task'].queryset.get(deal_id = dealid)
                except Deal.DoesNotExist:
                    pass
        else:
            self.fields['open_deal_task'].widget.attrs['disabled'] = True
        self.fields['open_deal_task'].required = False        
 
    open_deal_task = forms.ModelChoiceField(queryset='', label=_(u'Task about an existing deal?'))    


class FilterOpenDealForm(Form):            
    deal_instance_name = forms.CharField(widget = forms.TextInput(attrs={'placeholder': _(u'Filter here...'), 'class': 'placeholder_fix_css input-small search-query typeahead_opendeal_deal_name', 'autocomplete': 'off', 'data-provide': 'typeahead'}), max_length=40)    
    status          = forms.ModelChoiceField(queryset=DealStatus.objects.all(), widget = forms.TextInput(attrs={'placeholder': _(u'Filter here...'), 'class': 'placeholder_fix_css input-small search-query typeahead_opendeal_status', 'autocomplete': 'off', 'data-provide': 'typeahead'}))    
    last_contacted  = forms.DateField(widget = forms.DateInput(attrs={'placeholder': _(u'Filter here...'), 'class': 'placeholder_fix_css input-small search-query typeahead_opendeal_last_contacted', 'autocomplete': 'off', 'data-provide': 'typeahead'}))
    total_value     = forms.DecimalField(widget = forms.TextInput(attrs={'placeholder': _(u'Filter here...'), 'class': 'placeholder_fix_css input-small search-query typeahead_opendeal_total_price', 'autocomplete': 'off', 'data-provide': 'typeahead'}))



class FilterDealTemplateForm(Form):
    def __init__(self, company, *args, **kwargs):
        super(FilterDealTemplateForm, self).__init__(*args, **kwargs)
        self.fields['sales_item'].queryset = SalesItem.objects.filter(company=company)
            
    deal_name           = forms.CharField(widget = forms.TextInput(attrs={'placeholder': _(u'Filter here...'), 'class': 'placeholder_fix_css input-small search-query typeahead_deals_deal_name', 'autocomplete': 'off', 'data-provide': 'typeahead'}), max_length=40)    
    sales_item          = forms.ModelMultipleChoiceField(queryset='', widget = forms.TextInput(attrs={'placeholder': _(u'Filter here...'), 'class': 'placeholder_fix_css input-small search-query typeahead_deals_sales_item', 'autocomplete': 'off', 'data-provide': 'typeahead'}))    
    price               = forms.DecimalField(widget = forms.TextInput(attrs={'placeholder': _(u'Filter here...'), 'class': 'placeholder_fix_css input-small search-query typeahead_deals_price', 'autocomplete': 'off', 'data-provide': 'typeahead'}))
    sales_term          = forms.ModelChoiceField(queryset=SalesTerm.objects.all(), widget = forms.TextInput(attrs={'placeholder': _(u'Filter here...'), 'class': 'placeholder_fix_css input-small search-query typeahead_deals_sales_term', 'autocomplete': 'off', 'data-provide': 'typeahead'}))
    quantity            = forms.IntegerField(widget = forms.TextInput(attrs={'placeholder': _(u'Filter here...'), 'class': 'placeholder_fix_css input-small search-query typeahead_deals_quantity', 'autocomplete': 'off', 'data-provide': 'typeahead'})) 
    total_price         = forms.DecimalField(widget = forms.TextInput(attrs={'placeholder': _(u'Filter here...'), 'class': 'placeholder_fix_css input-small search-query typeahead_deals_price', 'autocomplete': 'off', 'data-provide': 'typeahead'}))


class DealTemplateForm(ModelForm):    
    def __init__(self, *args, **kwargs):
        super(DealTemplateForm, self).__init__(*args, **kwargs)
        self.fields['sales_item'].queryset = SalesItem.objects.filter(company=self.instance.company)                
        self.fields['sales_term'].widget.attrs['class'] = 'mandatory'        
        self.fields['currency'].widget.attrs['class'] = 'mandatory'
    
    def clean_quantity(self):
        if 'quantity' in self.cleaned_data:
            quantity = self.cleaned_data['quantity']            
            if quantity > 0:
                return quantity
        raise forms.ValidationError(_(u'Ensure this value is greater than %(number)s.') % {'number': 0})
    
    class Meta:
        model = DealTemplate
        exclude = ('company')
        
        widgets = {
                    'deal_name': forms.TextInput(attrs={'placeholder': _(u'Name the deal'), 'class': 'placeholder_fix_css input_mandatory', 'autocomplete': 'off'}),
                    'deal_description': forms.Textarea(attrs={'placeholder': _(u'Describe the deal')}),
                    'sales_item': forms.SelectMultiple(attrs={'data-placeholder': _(u'What are you selling?'), 'class': 'sales_item multi_select_mandatory'}),                    
                    'price': forms.TextInput(attrs={'placeholder': _(u'How much is proposed?'), 'class': 'placeholder_fix_css price', 'autocomplete': 'off'}),                   
                    'quantity': forms.TextInput(attrs={'placeholder': _(u'How many items?'), 'class': 'placeholder_fix_css quantity', 'autocomplete': 'off'}),                                                  
                   }

class DealForm(ModelForm):
    attached_open_deal_id  = forms.IntegerField(required=False)    
    
    def __init__(self, *args, **kwargs):
        super(DealForm, self).__init__(*args, **kwargs)                       
        self.fields['status'].widget.attrs['class'] = 'boxes_8em mandatory deal_status'
        self.fields['price'].widget.attrs['class'] = 'boxes_7em price'
        self.fields['quantity'].widget.attrs['class'] = 'boxes_7em quantity'
        self.fields['sales_term'].widget.attrs['class'] = 'boxes_8em mandatory'
        self.fields['sales_item'].widget.attrs['class'] = 'multi_select_mandatory'
        self.fields['currency'].widget.attrs['class'] = 'boxes_8em mandatory'

        self.fields['deal_instance_name'].widget.attrs['placeholder'] = _(u'Define an deal name')
        self.fields['deal_instance_name'].widget.attrs['class'] = 'input_mandatory'
        self.fields['deal_template_name'].widget.attrs.update({'readonly' : 'True'})
        self.fields['deal_template'].widget.attrs['class'] = 'hidden'        
        self.fields['deal_description'].widget.attrs['class'] = 'cb_deal_description'
        self.fields['total_price'].widget.attrs['class'] = 'boxes_7em total_price'
        self.fields['total_price'].widget.attrs['readonly'] = 'True'
        
    
    class Meta:
        model = Deal
        fields = {'deal_template', 'deal_template_name', 'deal_instance_name', 'status', 
                  'deal_description', 'sales_item', 'price', 'currency', 'sales_term', 'quantity', 'total_price'}
        
class DealNegotiateForm(DealForm):
    call_notes = forms.CharField(widget = forms.Textarea(attrs={'placeholder': _(u'What did you discuss with the customer?'), 'class' : 'cb_notes_maxwidth textarea_mandatory'}))
    
    def __init__(self, *args, **kwargs):
        super(DealNegotiateForm, self).__init__(*args, **kwargs)                       
        #self.fields['call_notes'].widget.attrs['class'] = 'cb_deal_description'
    
        

class FilterSalesItemForm(Form):
    def __init__(self, *args, **kwargs):
        super(FilterSalesItemForm, self).__init__(*args, **kwargs)          
    
    item_name    = forms.CharField(widget = forms.TextInput(attrs={'placeholder': _(u'Filter here...'), 'class': 'placeholder_fix_css input-small search-query filter_add_button typeahead_sales_items', 'autocomplete': 'off', 'data-provide': 'typeahead'}), max_length=40)

class SalesItemForm(ModelForm):
    class Meta:
        model = SalesItem
        exclude = ('company')
        widgets = {
                   'item_name': forms.TextInput(attrs={'autocomplete': 'off', 'class':'item_name'}),
                   }
        
    


class MaritalStatusForm(ModelForm):
    class Meta:
        model = MaritalStatus

class SalesTermForm(ModelForm):
    class Meta:
        model = SalesTerm

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
            
            
class ColleagueInviteForm(ModelForm):
    class Meta:
        model = Invitation
        fields = {'name', 'email'}
            

class TaskForm(ModelForm):
    due_time  = forms.TimeField(localize=True)
    contact_text  = forms.CharField(max_length=81, label = _(u'Contact person'), required= False) 
    

    def round_time_to_nearest_quarter(self):
        #form is in Add mode., hence we just pick the currenct date_time as base.
        time_close_to_quarter = timezone.now()
        # Time difference to 15 min round 
        time_discard = datetime.timedelta(minutes=time_close_to_quarter.time().minute % 15, seconds=time_close_to_quarter.second) 
        # Deduct that difference from the current time to round it down to nearest quarter.
        time_close_to_quarter -= time_discard
        return time_close_to_quarter

    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        self.fields['due_time'].widget.attrs['class'] = 'timepicker-default input-small' 
        self.fields['due_time'].widget.attrs['placeholder'] = _(u'What time?')
        self.fields['due_time'].widget.attrs['autocomplete'] = 'off'
        #If the date_time is set, it means the form is in edit mode, and we edit the existing time value 
        if self.instance.due_date_time:
            local_tz = timezone.get_current_timezone()
            #Convert the UTC date_time into currenct time zone
            self.fields['due_time'].initial = self.instance.due_date_time.replace(tzinfo=pytz.utc).astimezone(local_tz).time()  
        else:            
            self.fields['due_time'].initial = (self.round_time_to_nearest_quarter() +  datetime.timedelta(minutes=30)).time() 

        self.fields['contact_text'].initial = u'{0} {1}'.format(self.instance.contact.first_name, self.instance.contact.last_name)
        self.fields['contact_text'].widget.attrs['readonly'] = True
    
    def clean_due_time(self):
        due_time = self.cleaned_data['due_time']
        due_date_time = timezone.now()
        current_tz = timezone.get_current_timezone()  
        selected_due_date_time = current_tz.localize(datetime.datetime(due_date_time.year, due_date_time.month, due_date_time.day, due_time.hour, due_time.minute))        
        
        # time_close_to_quarter is always rounded down by max 15 min. Hence if the selected due date time is less than equal full 15 min in future, then
        # there won't be enough time for the system to remind the user, hence it will be rejected. 
        if selected_due_date_time <= self.round_time_to_nearest_quarter() + datetime.timedelta(minutes=15):
            raise forms.ValidationError(_(u"The due time of a task has to be set at least 15 minutes in the future."))
        return due_time
    
    def save(self, commit=True):
        instance = super(TaskForm, self).save(commit=False)
        # Always localize the entered date by user into his timezone before saving it to database
        if 'due_date_time' in self.cleaned_data and 'due_time' in self.cleaned_data:
            due_date_time = self.cleaned_data['due_date_time']
            due_time = self.cleaned_data['due_time']
            current_tz = timezone.get_current_timezone()            
            instance.due_date_time = current_tz.localize(datetime.datetime(due_date_time.year, due_date_time.month, due_date_time.day, due_time.hour, due_time.minute))
        if commit:
            instance.save()
        return instance
    
    
    class Meta:
        model = Task
        exclude = {'reminder_date_time', 'company', 'contact', 'user'}
        widgets={                    
                    'title' : forms.TextInput(attrs={'placeholder': _(u'What is this task about?'), 'class':'placeholder_fix_css', 'autocomplete':'off'}),
                    'due_date_time': forms.DateInput(attrs={'placeholder': _(u'When is this task due?'), 'class':'placeholder_fix_css date_picker', 'autocomplete':'off'}),                    
                }
        
        
class EventForm(ModelForm):    
    due_time  = forms.TimeField(localize=True)    
    due_datetime = forms.DateField(label='Date', localize=True, widget=forms.DateInput(attrs={'placeholder': _(u'When is this event due?'), 'class':'placeholder_fix_css date_picker event_date', 'autocomplete':'off'}))        
    contact_text  = forms.CharField(max_length=81, label = _(u'Contact person'), required= False) 
    

    def round_time_to_nearest_quarter(self):
        #form is in Add mode., hence we just pick the currenct date_time as base.
        time_close_to_quarter = timezone.now()
        # Time difference to 15 min round 
        time_discard = datetime.timedelta(minutes=time_close_to_quarter.time().minute % 15, seconds=time_close_to_quarter.second, microseconds=time_close_to_quarter.microsecond) 
        # Deduct that difference from the current time to round it down to nearest quarter.
        time_close_to_quarter -= time_discard
        return time_close_to_quarter

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.fields['due_time'].widget.attrs['class'] = 'timepicker-default input-small' 
        self.fields['due_time'].widget.attrs['placeholder'] = _(u'What time?')
        self.fields['due_time'].widget.attrs['autocomplete'] = 'off'
        #If the date_time is set, it means the form is in edit mode, and we edit the existing time value 
        local_tz = timezone.get_current_timezone()
        if self.instance.due_date_time:            
            #Convert the UTC date_time into currenct time zone
            self.fields['due_time'].initial = self.instance.due_date_time.replace(tzinfo=pytz.utc).astimezone(local_tz).time()  
        else:            
            self.fields['due_time'].initial = (self.round_time_to_nearest_quarter() +  datetime.timedelta(minutes=135)).time() 
        #Todo: refactor
        deal = Deal.objects.filter(deal_id = self.instance.deal_id)[0]        
        self.fields['contact_text'].initial = u'{0} {1}'.format(deal.contact.first_name, deal.contact.last_name)
        self.fields['contact_text'].widget.attrs['readonly'] = True       
        if self.instance.pk: 
            self.fields['due_datetime'].initial = self.instance.due_date_time.replace(tzinfo=pytz.utc).astimezone(local_tz).date()
        #self.fields['due_date_time'].localize=True
        #self.fields['due_date_time'].widget.is_localized = True
    
    def clean_due_time(self):            
        due_time = self.cleaned_data['due_time']
        
        if self.instance.pk:
            return due_time
        
        if 'due_datetime' in self.cleaned_data:
            due_date_time = self.cleaned_data['due_datetime']
        else:
            return due_time
        
        current_tz = timezone.get_current_timezone()  
        selected_due_date_time = current_tz.localize(datetime.datetime(due_date_time.year, due_date_time.month, due_date_time.day, due_time.hour, due_time.minute, 0, 0))        
        
        # time_close_to_quarter is always rounded down by max 15 min. Hence if the selected due date time is less than equal full 15 min in future, then
        # there won't be enough time for the system to remind the user, hence it will be rejected. 
        if selected_due_date_time < self.round_time_to_nearest_quarter() + datetime.timedelta(minutes=135):
            raise forms.ValidationError(_(u"The due time of an event has to be set at least 2 hours in the future."))
        return due_time
    
    def save(self, commit=True):
        instance = super(EventForm, self).save(commit=False)
        # Always localize the entered date by user into his timezone before saving it to database
        if 'due_datetime' in self.cleaned_data and 'due_time' in self.cleaned_data:
            due_date_time = self.cleaned_data['due_datetime']
            due_time = self.cleaned_data['due_time']
            current_tz = timezone.get_current_timezone()            
            instance.due_date_time = current_tz.localize(datetime.datetime(due_date_time.year, due_date_time.month, due_date_time.day, due_time.hour, due_time.minute, 0, 0))
        if commit:
            instance.save()
        return instance
    
    def clean(self):
        cleaned_data = super(EventForm, self).clean()
        if 'due_datetime' in self.cleaned_data and 'due_time' in self.cleaned_data:
            due_date_time = self.cleaned_data['due_datetime']        
            due_time = self.cleaned_data['due_time']
            current_tz = timezone.get_current_timezone() 
            date_time = current_tz.localize(datetime.datetime(due_date_time.year, due_date_time.month, due_date_time.day, due_time.hour, due_time.minute))
            if date_time.date() < timezone.now().replace(tzinfo=pytz.utc).astimezone(current_tz).date():            
                self._errors["due_datetime"] = self.error_class([_(u'An event date can not take place in the past.')])
                del cleaned_data['due_datetime']
            if date_time.time() < timezone.now().replace(tzinfo=pytz.utc).astimezone(current_tz).time():            
                self._errors["due_time"] = self.error_class([_(u'An event time can not take place in the past.')])
                del cleaned_data['due_time']
        return cleaned_data
    
    class Meta:
        model = Event
        exclude = {'reminder_date_time', 'company', 'user', 'due_date_time'}
        widgets={                    
                    'reminder' : forms.Select(attrs={'class':'placeholder_fix_css event_reminder'}),
                    
                    'notes': forms.Textarea(attrs={'placeholder': _(u'What do you have to do to win this deal?'), 'class':'placeholder_fix_css textarea_15em', 'autocomplete':'off'}),                    
                }
  