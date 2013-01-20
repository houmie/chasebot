import datetime
from datetime import datetime as dt 
from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from chasebot_app.forms import RegistrationForm, ContactsForm, ConversationForm, SalesItemForm, DealTemplateForm,\
     DealForm, FilterContactsForm, FilterConversationForm, FilterDealTemplateForm, FilterSalesItemForm,\
    DealsAddForm, OpenDealsAddForm, ColleagueInviteForm, OpenDealTaskForm,\
    TaskForm, EventForm, DealNegotiateForm, FilterOpenDealForm
from chasebot_app.models import Company, Contact, Conversation, SalesItem, DealTemplate, Deal, SalesTerm,\
    Invitation, LicenseTemplate, MaritalStatus, \
    Currency, Task, Event
from chasebot_app.models import UserProfile 
from django.utils.translation import ugettext as _, ungettext
from django.utils import timezone, simplejson
from django.forms.models import modelformset_factory
import uuid
from django.db.models.aggregates import Max
import time
from django.core.paginator import Paginator, InvalidPage
import pytz
from django.shortcuts import redirect, render
from chasebot.formats.en import formats as formats_en
from chasebot.formats.en_GB import formats as formats_en_GB
import operator
from django.db.models.query_utils import Q
from chasebot_app.json_extension import toJSON
from django.forms.formsets import formset_factory
from django.contrib import messages
from random import choice
from string import ascii_lowercase, digits
import random
from django.contrib.auth import authenticate, login
from django.template.loader_tags import register
import json
from django.core import serializers
from django.utils.timezone import utc
from django.utils.datetime_safe import date



ITEMS_PER_PAGE = 10

@login_required
def set_timezone(request):
    if request.method == 'POST':
        request.session['django_timezone'] = pytz.timezone(request.POST['timezone'])
        profile = request.user.get_profile()
        profile.timezone = request.POST['timezone']
        profile.save()
        return redirect(request.path)
    else:
        return redirect('/')

def get_current_date_input_format(request):
    if request.LANGUAGE_CODE == 'en-gb':
        return formats_en_GB.DATE_INPUT_FORMATS[0]
    elif request.LANGUAGE_CODE == 'en':        
        return formats_en.DATE_INPUT_FORMATS[0]

def create_date_from_javascript_date(request, date, to_date_format = None):
    current_tz = timezone.get_current_timezone()    
    date_time_unaware = dt.strptime(date, get_current_date_input_format(request))
    if to_date_format:    
        date_time_unaware = date_time_unaware.replace(hour=23, minute=59, second=59)
    date_time = current_tz.localize(date_time_unaware)            
    return date_time


def get_raw_all_open_deals():
    query = 'SELECT id, contact_id, l1.deal_id \
             FROM chasebot_app_deal AS l1 \
             INNER JOIN ( \
                 SELECT deal_id, MAX(deal_datetime) AS time_stamp_max \
                 FROM chasebot_app_deal \
                 GROUP BY deal_id \
            ) AS l2 \
            ON \
            l1.deal_id     = l2.deal_id AND \
            l1.deal_datetime = l2.time_stamp_max \
            INNER JOIN ( \
                 SELECT deal_id, deal_datetime, MAX(id) AS trans_max \
                 FROM chasebot_app_deal \
                 GROUP BY deal_id, deal_datetime \
                 ) AS l3 \
            ON \
            l1.deal_id     = l3.deal_id AND l1.deal_datetime = l3.deal_datetime AND l1.id   = l3.trans_max \
            WHERE l1.deal_id not in (select deal_id from chasebot_app_deal where status_id in (5, 6))' 
    return Deal.objects.raw(query)


@login_required
def all_open_deals(request, company):    
    raw = get_raw_all_open_deals() 
    deals_query = company.deal_set.filter(id__in=[item.id for item in raw])        
    return deals_query
    

@login_required
def contacts_with_open_deals(request, company):    
    raw = get_raw_all_open_deals() 
    contacts_query = company.contact_set.filter(id__in=[item.contact_id for item in raw])        
    return contacts_query

@login_required
def conversations_with_open_deals(request, contact):    
    raw = get_raw_all_open_deals() 
    deals_query = contact.deal_set.filter(deal_id__in=[item.deal_id for item in raw])
    conversations_query = contact.conversation_set.filter(id__in=[item.conversation.id for item in deals_query])        
    return conversations_query
   

@login_required
def index_display(request):
    profile = request.user.get_profile()
    if not 'django_timezone' in request.session: 
        request.session['django_timezone'] = pytz.timezone(profile.timezone)
    company_name = profile.company.company_name
    variables = {'company_name': company_name}
    variables = merge_with_localized_variables(request, variables)
    return render(request, 'index.html', variables)        


@login_required
def open_deals_display(request):
    profile = request.user.get_profile()
    
    ajax = False    
    if 'ajax' in request.GET:
        ajax = True
        deals_query = all_open_deals(request, profile.company)
        
        if 'deal_instance_name' in request.GET:    
            deal_instance_name = request.GET['deal_instance_name']
            deals_query = deals_query.filter(deal_instance_name__icontains=deal_instance_name).order_by('deal_instance_name')
        if 'status' in request.GET:    
            status = request.GET['status']
            deals_query = deals_query.filter(status__icontains=status).order_by('status')
        if 'last_contacted' in request.GET:    
            last_contacted = request.GET['last_contacted']
            deals_query = deals_query.filter(last_contacted__icontains=last_contacted).order_by('last_contacted')
        if 'total_value' in request.GET:    
            total_value = request.GET['total_value']
            deals_query = deals_query.filter(total_value__icontains=total_value).order_by('total_value')
    else:
        deals_query = all_open_deals(request, profile.company)
    
    deals, paginator, page, page_number = makePaginator(request, ITEMS_PER_PAGE, deals_query)  
    variables = {'deals': deals}
    variables = merge_with_additional_variables(request, paginator, page, page_number, variables)
    if ajax:
        return render(request, 'open_deals_list.html', variables)
    else:
        return render(request, 'open_deals.html', variables)

@login_required
def load_open_deals_variables(request, profile):
    deals_query = all_open_deals(request, profile.company)
    deals, paginator, page, page_number = makePaginator(request, ITEMS_PER_PAGE, deals_query)  
    variables = {'deals': deals}
    variables = merge_with_additional_variables(request, paginator, page, page_number, variables)     
    return variables

@login_required
def open_deal_conversations_display(request, deal_id):
    profile = request.user.get_profile()
    deal = get_object_or_404(profile.company.deal_set.all(), pk=deal_id)
    related_deals = Deal.objects.filter(deal_id = deal.deal_id).order_by('-deal_datetime')[:3]
    calls = Conversation.objects.filter(pk__in = [deal.conversation.pk for deal in related_deals]).order_by('-conversation_datetime')
    events = profile.company.event_set.filter(deal_id = deal.deal_id).order_by('due_date_time')
    variables = {'calls': calls, 'events' : events, 'deal_id':deal_id}
    return render(request, '_deal_conversations.html', variables)
    

@login_required
def negotiate_open_deal(request, deal_pk):
    profile = request.user.get_profile()
    actual_deal = get_object_or_404(profile.company.deal_set.all(), pk=deal_pk)
    validation_error_ajax = False

    if request.method == 'POST':        
        form = DealNegotiateForm(request.POST, instance=actual_deal)
        
        if form.is_valid():
            # Always localize the entered date by user into his timezone before saving it to database
            call = Conversation(contact=actual_deal.contact, conversation_datetime = timezone.now(), notes=form.cleaned_data['call_notes'])
            call.save()
            modified_deal = form.save(commit=False)            
            deal = Deal.objects.create(
                                deal_id =       actual_deal.deal_id,
                                deal_datetime = call.conversation_datetime, 
                                status =        modified_deal.status, 
                                contact =       call.contact, 
                                deal_template = modified_deal.deal_template,
                                deal_template_name = modified_deal.deal_template_name,  
                                conversation =  call,                                            
                                deal_instance_name = modified_deal.deal_instance_name,
                                deal_description = modified_deal.deal_description,
                                price =         modified_deal.price,        
                                currency =      modified_deal.currency,                
                                sales_term =    modified_deal.sales_term,
                                quantity =      modified_deal.quantity,
                                company =       profile.company                                            
                                )
            #Saving M2M 
            for item in form.cleaned_data['sales_item']:
                deal.sales_item.add(item)
            deal.save();
                        
            #In case the instance name was changed we change also all other instance names of the same set.
            adjust_deal_names_of_same_dealset(deal.contact, deal)                                
            
            variables = load_open_deals_variables(request, profile)
            return render(request, 'open_deals.html', variables)
            
        else:
            validation_error_ajax = True    
            
    else:
        form = DealNegotiateForm(instance=actual_deal)

    
    variables = {'fs':form, 'validation_error_ajax':validation_error_ajax, 'contact':actual_deal.contact }
    return render(request, '_deal_edit_item.html', variables)


@login_required
def contacts_display(request, contact_id=None):      
    profile = request.user.get_profile()
    company_name = profile.company.company_name
    
    if contact_id:
        contact = get_object_or_404(profile.company.contact_set.all(), pk=contact_id)
        variables = { 'contact' : contact }
        return render(request, 'business_card.html', variables)
        
    ajax = False    
    if 'ajax' in request.GET:
        ajax = True
        if 'show_only_open_deals' in request.GET:
            contacts_queryset = contacts_with_open_deals(request, profile.company)
        else:
            contacts_queryset = profile.company.contact_set.all().order_by('last_name')
        
        if 'last_name' in request.GET:    
            last_name = request.GET['last_name']
            contacts_queryset = contacts_queryset.filter(last_name__icontains=last_name).order_by('last_name')
        if 'first_name' in request.GET:    
            first_name = request.GET['first_name']
            contacts_queryset = contacts_queryset.filter(first_name__icontains=first_name).order_by('first_name')
        if 'company' in request.GET:    
            company = request.GET['company']
            contacts_queryset = contacts_queryset.filter(company_name__icontains=company).order_by('company_name')
        if 'email' in request.GET:    
            email = request.GET['email']
            contacts_queryset = contacts_queryset.filter(email__icontains=email).order_by('email')
    else:
        contacts_queryset = profile.company.contact_set.all().order_by('last_name')        
    
    filter_form = FilterContactsForm(request.GET)
    contacts, paginator, page, page_number = makePaginator(request, ITEMS_PER_PAGE, contacts_queryset)  
    source = '/contacts'  
    variables = {
                 'company_name': company_name, 'contacts' : contacts, 'filter_form' : filter_form, 'source' : source
                 }
    variables = merge_with_additional_variables(request, paginator, page, page_number, variables)
    if ajax:    
        return render(request, 'contact_list.html', variables)
    else:
        return render(request, 'contacts.html', variables)        



@login_required
def contact_add_edit(request, contact_id=None):    
    profile = request.user.get_profile()
    if contact_id is None:
        contact = Contact(company=profile.company)
        template_title = _(u'Add New Contact')
    else:
        contact = get_object_or_404(profile.company.contact_set.all(), pk=contact_id)
        template_title = _(u'Edit Contact')
    if request.method == 'POST':
        form = ContactsForm(request.POST, instance=contact)
        if form.is_valid():
            contact = form.save()
            contacts_queryset = profile.company.contact_set.all().order_by('last_name')
            contacts, paginator, page, page_number = makePaginator(request, ITEMS_PER_PAGE, contacts_queryset)  
            source = '/contacts'
            company_name = profile.company.company_name
            variables = {
                         'company_name': company_name, 'contacts' : contacts, 'source' : source
                         }
            variables = merge_with_additional_variables(request, paginator, page, page_number, variables)
            return render(request, 'contacts.html', variables)            
    else:
        form = ContactsForm(instance=contact)    
    variables = {'form':form, 'template_title': template_title, 'contact_id' : contact_id, }    
    return render(request, 'contact.html', variables)

@login_required
def contact_delete(request, contact_id):
    if contact_id is None:
        raise Http404(_(u'Contact not found'))
    else:
        profile = request.user.get_profile()
        contact = get_object_or_404(profile.company.contact_set.all(), pk=contact_id)
        contact.delete()        
        contacts_queryset = profile.company.contact_set.order_by('last_name')
        contacts, paginator, page, page_number = makePaginator(request, ITEMS_PER_PAGE, contacts_queryset)    
        variables = { 'contacts': contacts, }
        variables = merge_with_pagination_variables(paginator, page, page_number, variables, None)
    return render(request, 'contact_list.html', variables)     


@login_required
def conversation_display(request, contact_id):    
    profile = request.user.get_profile()
    contact = get_object_or_404(profile.company.contact_set.all(), pk=contact_id)
    show_only_open_deals = False
    calls_queryset = contact.conversation_set.all().order_by('-conversation_datetime')
    
    ajax = False    
    if 'ajax' in request.GET:
        ajax = True            
        if 'from_date' in request.GET:                        
            from_date = create_date_from_javascript_date(request, request.GET['from_date'])
            if 'to_date' in request.GET:
                to_date = create_date_from_javascript_date(request, request.GET['to_date'], True)                
            else:
                to_date = timezone.now()        
            calls_queryset = calls_queryset.filter(conversation_datetime__range=(from_date, to_date))
                  
    
    filter_form = FilterConversationForm(request.GET)
    calls, paginator, page, page_number = makePaginator(request, ITEMS_PER_PAGE, calls_queryset)
    
#    task_queryset = contact.task_set.order_by('-due_date_time')
#    tasks = []
#    if task_queryset:
#        tasks, paginator_t, page_t, page_number_t = makePaginator(request, 3, task_queryset)        
    source = u'{0}/{1}/{2}'.format('contact', contact.pk, 'calls')
    variables = {
                 'calls': calls, 'contact': contact, 'contact_id':contact.pk, 'filter_form' : filter_form, 'show_only_open_deals' : show_only_open_deals, 'source' : source
                 }
    variables = merge_with_additional_variables(request, paginator, page, page_number, variables)
#    if task_queryset:
#        variables = merge_with_pagination_variables(paginator_t, page_t, page_number_t, variables, 'task_')
    if ajax:    
        return render(request, 'conversation_list.html', variables)
    else:
        return render(request, 'conversations.html', variables)
    

@login_required
def single_conversation_display(request, contact_id, call_id):    
    profile = request.user.get_profile()
    contact = get_object_or_404(profile.company.contact_set.all(), pk=contact_id)
    call = contact.conversation_set.get(pk=call_id)            
    variables = {
                 'calls': [call], 'contact': contact, 
                 }    
    return render(request, 'conversation_list_item.html', variables)    

    
@login_required
def get_deal_template(request, deal_template_id):        
    profile = request.user.get_profile()        
    deal_template = profile.company.dealtemplate_set.get(pk=deal_template_id)
    return HttpResponse(toJSON(deal_template), mimetype='application/json')        
                
@login_required
def get_opendeal(request, deal_id, contact_id=None):        
    profile = request.user.get_profile() 
    contact = profile.company.contact_set.get(pk=contact_id)       
    deal = contact.deal_set.get(pk=deal_id)
    return HttpResponse(toJSON(deal), mimetype='application/json')  
        

def remove_redundant_future_deals(contact, deal):
    #we need to remove all later entries of this instance on later conversations, if it has been closed.
    #The deal date_time is always the same as the conversation datetime, hence when we delete all deal instances for later than this closed deal,
    #we would be removing those later deal instances from future conversations.
    if (deal.status.pk in [5, 6]):
        later_deals_to_be_removed = contact.deal_set.filter(deal_id = deal.deal_id).filter(deal_datetime__gt=deal.deal_datetime)
        for bad_deal in later_deals_to_be_removed:
            bad_deal.delete()    


def adjust_deal_names_of_same_dealset(contact, deal):
    set_of_same_deal = contact.deal_set.filter(deal_id=deal.deal_id)
    for sdeal in set_of_same_deal:
        if sdeal.pk != deal.pk:
            if sdeal.deal_instance_name != deal.deal_instance_name:
                sdeal.deal_instance_name = deal.deal_instance_name
                sdeal.save()


@login_required
def conversation_add_edit(request, contact_id, call_id=None):
    profile = request.user.get_profile()
    contact = get_object_or_404(profile.company.contact_set.all(), pk=contact_id)
    
    if call_id is None:
        call = Conversation(contact=contact, conversation_datetime = timezone.now()) 
        template_title = _(u'Add New Conversation')
    else:
        call = get_object_or_404(contact.conversation_set.all(), pk=call_id)
        template_title = _(u'Edit Conversation')
    
    #All kind of deals attached (open or new) will be defined here
    deals_formset_factory = modelformset_factory(Deal, form=DealForm, extra=0, can_delete=True, max_num=5)
    #This formset contains an empty template in order to be cloned with jquery later on and added to attached_deals for saving
    extra_deal_formset_factory = formset_factory(DealForm, extra=1, max_num=1, can_delete=True)    
    attached_deals_to_call_query = call.deal_set.all()    
    validation_error_ajax = False
    
    if request.method == 'POST':        
        attached_deals_formset = deals_formset_factory(request.POST, prefix='deals')                
        form = ConversationForm(profile.company, request.POST, instance=call, prefix='form')           
        deals_add_form = DealsAddForm(profile.company, call, contact, request.POST, prefix='deals_add_form')
        opendeals_add_form = OpenDealsAddForm(profile.company, call, contact, request.POST, prefix='opendeals_add_form')
        if form.is_valid() and attached_deals_formset.is_valid():                
            # Always localize the entered date by user into his timezone before saving it to database
            call = form.save(commit=False)            
            current_tz = timezone.get_current_timezone()            
            date = form.cleaned_data['conversation_date']
            time = form.cleaned_data['conversation_time']            
            date_time = current_tz.localize(datetime.datetime(date.year, date.month, date.day, time.hour, time.minute))                        
            call.conversation_datetime = date_time
            call.save()
            
            for fm in attached_deals_formset:
                to_delete = fm.cleaned_data['DELETE']
                if to_delete:
                    deal_to_delete = fm.save(commit=False)                    
                    deal_to_delete.delete()
                    continue
                if fm.has_changed():
                    # If the open_deal_id exists this is a open deal (continuation of an existing deal instance)
                    if fm.cleaned_data['attached_open_deal_id']: 
                        actual_deal = contact.deal_set.get(pk=fm.cleaned_data['attached_open_deal_id'])
                        modified_deal = fm.save(commit=False)
                        #when adding an Open deals, we create a new entry but keep the same deal_id (UUID) and same set number.
                        #Until this instance has been closed. Where from then on the instance won't appear in the open deals dropdown any more. 
                        deal = Deal.objects.create(
                                            deal_id=actual_deal.deal_id,
                                            deal_datetime=call.conversation_datetime, 
                                            status=modified_deal.status, 
                                            contact=call.contact, 
                                            deal_template=modified_deal.deal_template,
                                            deal_template_name=modified_deal.deal_template_name,  
                                            conversation=call,                                            
                                            deal_instance_name=modified_deal.deal_instance_name,
                                            deal_description = modified_deal.deal_description,
                                            price = modified_deal.price,        
                                            currency = modified_deal.currency,                
                                            sales_term = modified_deal.sales_term,
                                            quantity = modified_deal.quantity,
                                            company = profile.company                                            
                                            )
                        #Saving M2M 
                        for item in fm.cleaned_data['sales_item']:
                            deal.sales_item.add(item)
                        deal.save();
                        
                        #In case the instance name was changed we change also all other instance names of the same set.
                        adjust_deal_names_of_same_dealset(contact, deal)
                        
                        #If the open deal instance is closed, we need to remove all later entries of this instance on later conversations.
                        remove_redundant_future_deals(contact, deal)
                    else:
                        #At this point it is a change to an existing attached deal OR
                        #It is adding a new deal to this conversation
                        deal = fm.save(commit=False)                                                         
                        deal.contact = contact
                        deal.conversation = call
                        deal.company = profile.company
                        deal.deal_datetime=call.conversation_datetime
                        if deal.pk:                        
                            #In case the instance name was changed we change also all other instance names of the same set.
                            adjust_deal_names_of_same_dealset(contact, deal)                     
                        deal.save()
                        fm.save_m2m()
                        #If the attached or even new deal are closed, we need to remove all later entries of this instance on later conversations.
                        remove_redundant_future_deals(contact, deal)            
            return render(request, 'conversation_list_item.html', {'calls':[call], 'contact':contact})
        else:
            validation_error_ajax = True    
            
    else:
        #Deals_add_form contains only one dropdown to add new deals. It contains the logic for excluding open/attached deals accordingly 
        deals_add_form = DealsAddForm(profile.company, call, contact, prefix='deals_add_form')
        form = ConversationForm(profile.company, instance=call, prefix='form')                      
        attached_deals_formset = deals_formset_factory(queryset=attached_deals_to_call_query, prefix='deals')                       
        #opendeass_add_form contains only one dropdown to add open deals. It contains the logic for excluding open/attached deals accordingly
        opendeals_add_form = OpenDealsAddForm(profile.company, call, contact, prefix='opendeals_add_form')
    
    #The extra deal formset will always be independent of POST/GET since its hidden and remains empty as a starting point for cloning
    extra_deal_formset = extra_deal_formset_factory(prefix='extra_deal')
    variables = {'form':form, 'template_title':template_title, 'deals_add_form':deals_add_form, 'opendeals_add_form':opendeals_add_form, 'attached_deals_formset':attached_deals_formset, 'contact_id':contact.pk, 'call_id':call_id, 'extra_deal_formset':extra_deal_formset, 'validation_error_ajax':validation_error_ajax }    
    #if call_id:
    return render(request, '_conversation_edit.html', variables)      
    #return render(request, '_conversation.html', variables)


@login_required
def conversation_delete(request, contact_id, call_id):
    if contact_id is None:
        raise Http404(_(u'Contact not found'))
    elif call_id is None:
        raise Http404(_(u'Conversation not found'))
    else:
        profile = request.user.get_profile()
        contact = get_object_or_404(profile.company.contact_set.all(), pk=contact_id)
        call = get_object_or_404(contact.conversation_set.all(), pk=call_id)
        call.delete()
        call_queryset = contact.conversation_set.order_by('conversation_datetime')   
        calls, paginator, page, page_number = makePaginator(request, ITEMS_PER_PAGE, call_queryset)          
        variables = { 'calls': calls, 'contact':contact }
        variables = merge_with_additional_variables(request, paginator, page, page_number, variables)
    return render(request, 'conversation_list.html', variables)


#@login_required
#def task_display(request):    
#    profile = request.user.get_profile()
#    if request.GET.get('contact', None):
#        contact = get_object_or_404(profile.company.contact_set.all(), pk=request.GET['contact'])
#    if contact:
#        task_queryset = contact.task_set.order_by('-due_date_time')
#    else:
#        task_queryset = profile.company.task_set.order_by('-due_date_time')
#    tasks, paginator, page, page_number = makePaginator(request, 3, task_queryset)            
#    variables = {
#                 'tasks': tasks, 'contact_id':contact.pk
#                }
#    variables = merge_with_pagination_variables(paginator, page, page_number, variables, 'task_')
#    return render(request, 'task_list.html', variables)


#@login_required
#def task_add_edit(request, task_id=None):
#    profile = request.user.get_profile()
#        
#    if task_id is None:
#        task = Task(company=profile.company, user=request.user) 
#        template_title = _(u'Add New Task')
#    else:
#        task = get_object_or_404(profile.company.task_set.all(), pk=task_id)
#        template_title = _(u'Edit Task')
#    validation_error_ajax = False
#    
#    contact = None
#    if request.GET.get('contact', None):
#        contact = get_object_or_404(profile.company.contact_set.all(), pk=request.GET['contact'])    
#        task.contact = contact
#        
#    if request.method == 'POST':
#        opendeals_task_form = OpenDealTaskForm(contact, task.deal_id, request.POST, prefix='opendeals_task_form')
#        form = TaskForm(request.POST, instance=task, prefix='form', initial = {'contact' : contact.pk})
#        if form.is_valid():
#            selected_open_deal = None
#            
#            if opendeals_task_form.is_valid():
#                selected_open_deal = opendeals_task_form.cleaned_data['open_deal_task']            
#            task = form.save(commit=False)
#            if selected_open_deal is not None:
#                task.deal_id = selected_open_deal.deal_id
#            task.save()
#            task_queryset = profile.company.task_set.order_by('-due_date_time')
#            tasks, paginator_t, page_t, page_number_t = makePaginator(request, 3, task_queryset) 
#            variables = {'tasks':tasks, 'contact_id':contact.pk}
#            variables = merge_with_pagination_variables(paginator_t, page_t, page_number_t, variables, 'task_')
#            return render(request, 'task_list.html', variables)
#        else:
#            validation_error_ajax = True
#    else:
#        #opendeass_add_form contains only one dropdown to add open deals to task        
#        opendeals_task_form = OpenDealTaskForm(contact, task.deal_id, prefix='opendeals_task_form')
#        if contact:
#            form = TaskForm(instance=task, prefix='form', initial = {'contact' : contact.pk})
#        else:
#            form = TaskForm(instance=task, prefix='form')
#
#    variables = {'form':form, 'template_title':template_title, 'opendeals_task_form':opendeals_task_form, 'validation_error_ajax':validation_error_ajax }
#    variables = merge_with_localized_variables(request, variables)    
#    return render(request, 'task.html', variables)
#
#
#@login_required
#def task_delete(request, task_id):
#    if task_id is None:
#        raise Http404(_(u'Task not found'))    
#    else:
#        profile = request.user.get_profile()
#        task = get_object_or_404(profile.company.task_set.all(), pk=task_id)        
#        task.delete()
#        task_queryset = profile.company.task_set.order_by('-due_date_time')   
#        tasks, paginator, page, page_number = makePaginator(request, 3, task_queryset)
#        contact_id = None
#        if 'contact' in request.GET:
#            contact_id = request.GET['contact']          
#        variables = { 'tasks': tasks , 'contact_id':contact_id}
#        variables = merge_with_pagination_variables(paginator, page, page_number, variables, 'task_')
#    return render(request, 'task_list.html', variables)


@login_required
def event_display(request):
    profile = request.user.get_profile()        
    events = profile.company.event_set.order_by('due_date_time')
    
    #tasks, paginator, page, page_number = makePaginator(request, 3, task_queryset)
    variables = {
                 'events': events,
                }
    #variables = merge_with_pagination_variables(paginator, page, page_number, variables, 'task_')
    return render(request, 'event_list.html', variables)


@login_required
def event_add_edit(request, open_deal_id=None, event_id=None):
    profile = request.user.get_profile()
        
    if event_id is None and open_deal_id:
        deal = get_object_or_404(profile.company.deal_set.all(), pk=open_deal_id)
        event = Event(company=profile.company, user=request.user, deal_id=deal.deal_id) 
        template_title = _(u'Add New Event')
    elif event_id and open_deal_id is None:
        event = get_object_or_404(profile.company.event_set.all(), pk=event_id)
        template_title = _(u'Edit Event')
    
    validation_error_ajax = False

    if request.method == 'POST':        
        form = EventForm(request.POST, instance=event, prefix='form')
        if form.is_valid():                        
            event = form.save()            
            events = profile.company.event_set.filter(deal_id = event.deal_id).order_by('due_date_time')[:3]
            #tasks, paginator_t, page_t, page_number_t = makePaginator(request, 3, event_queryset) 
            variables = {'events':events}
            #variables = merge_with_pagination_variables(paginator_t, page_t, page_number_t, variables, 'task_')
            return render(request, 'event_list.html', variables)
        else:
            validation_error_ajax = True
    else:        
        form = EventForm(instance=event, prefix='form')

    variables = {'form':form, 'template_title':template_title, 'validation_error_ajax':validation_error_ajax }       
    return render(request, 'event.html', variables)

@login_required
def event_tick(request, event_id):
    if event_id is None:
        raise Http404(_(u'Event not found'))    
    else:
        profile = request.user.get_profile()
        event = get_object_or_404(profile.company.event_set.all(), pk=event_id)        
        event.delete()
        variables = get_event_variables(profile)
    return render(request, 'events.html', variables)

@login_required
def event_delete(request, event_id):
    if event_id is None:
        raise Http404(_(u'Event not found'))    
    else:
        profile = request.user.get_profile()
        event = get_object_or_404(profile.company.event_set.all(), pk=event_id)        
        deal_id = event.deal_id
        event.delete()           
        events = profile.company.event_set.filter(deal_id = deal_id).order_by('due_date_time')[:3]
        #tasks, paginator, page, page_number = makePaginator(request, 3, event_queryset)        
        variables = { 'events': events}
        #variables = merge_with_pagination_variables(paginator, page, page_number, variables, 'task_')
    return render(request, 'event_list.html', variables)


@login_required
def events_display(request):
    profile = request.user.get_profile()    
    variables = get_event_variables(profile)    
    return render(request, 'events.html', variables)

def get_event_variables(profile):
    datetime.date.today()
    today_min = datetime.datetime.combine(timezone.now(), datetime.time.min)
    today_max = datetime.datetime.combine(timezone.now(), datetime.time.max)
    today_events = profile.company.event_set.filter(due_date_time__range=(today_min, today_max))
    
    tom_min = datetime.datetime.combine(timezone.now() + datetime.timedelta(days=1), datetime.time.min)
    tom_max = datetime.datetime.combine(timezone.now() + datetime.timedelta(days=1), datetime.time.max)    
    tomorrow_events = profile.company.event_set.filter(due_date_time__range=(tom_min, tom_max))
    
    today = timezone.now()
    start_week = today - datetime.timedelta(today.weekday())
    end_week = start_week + datetime.timedelta(6)
    week_min = datetime.datetime.combine(start_week, datetime.time.min)
    week_max = datetime.datetime.combine(end_week, datetime.time.max)
    this_week_events = profile.company.event_set.filter(due_date_time__range=(week_min, week_max))        
    this_week_events = this_week_events.exclude(pk__in=[item.pk for item in today_events])
    this_week_events = this_week_events.exclude(pk__in=[item.pk for item in tomorrow_events])
                                 
    start_week_next = start_week + datetime.timedelta(7)  
    end_week_next = end_week + datetime.timedelta(7)
    week_min = datetime.datetime.combine(start_week_next, datetime.time.min)
    week_max = datetime.datetime.combine(end_week_next, datetime.time.max)
    next_week_events = profile.company.event_set.filter(due_date_time__range=(week_min, week_max))
    next_week_events = next_week_events.exclude(pk__in=[item.pk for item in today_events])
    next_week_events = next_week_events.exclude(pk__in=[item.pk for item in tomorrow_events])
    
    variables = {'today_events':today_events, 'tomorrow_events':tomorrow_events, 'this_week_events':this_week_events, 'next_week_events':next_week_events}
    return variables

@login_required
def sales_item_display(request):
    profile = request.user.get_profile()
    sales_items_queryset = profile.company.salesitem_set.order_by('item_name')    
    ajax = False
    
        
    if 'ajax' in request.GET:
        ajax = True        
        if 'item_name' in request.GET:    
            item_name = request.GET['item_name']
            sales_items_queryset = sales_items_queryset.filter(item_name__icontains=item_name).order_by('item_name')

    
    filter_form = FilterSalesItemForm(request.GET)    
    sales_items, paginator, page, page_number = makePaginator(request, ITEMS_PER_PAGE, sales_items_queryset)    
    #New SalesItem form for adding a possible new one on UI
    sales_item = SalesItem(company=profile.company)
    form = SalesItemForm(instance=sales_item)
    source = 'sales_items/'          
    variables = {
                 'sales_items': sales_items, 'form':form, 'filter_form' : filter_form, 'get_request':get_request_parameters(request), 'source':source
                }   
    variables = merge_with_additional_variables(request, paginator, page, page_number, variables) 
    if ajax:    
        return render(request, 'sales_item_list.html', variables)
    else:        
        return render(request, '_sales_items_table.html', variables)
#        else:
#            return render(request, 'sales_items.html', variables)  

@login_required
def single_sales_item_display(request, sales_item_id):
    profile = request.user.get_profile()    
    sales_item = get_object_or_404(profile.company.salesitem_set.all(), pk=sales_item_id)
    variables = {'sales_items' : [sales_item]}
    return render(request, '_sales_item_rows.html', variables)

@login_required
def deal_template_sales_item_display(request):
    profile = request.user.get_profile()        
    deal = DealTemplate(company=profile.company)
    form = DealTemplateForm(instance=deal)    
    variables = {'form':form }
    return render(request, 'deal_template_sales_item.html', variables)
   

@login_required
def sales_item_add_edit(request, sales_item_id=None):    
    profile = request.user.get_profile()    
    validation_error_ajax = False;
    source = 'sales_items/'  
    if sales_item_id is None:
        sales_item = SalesItem(company=profile.company)        
    else:
        sales_item = get_object_or_404(profile.company.salesitem_set.all(), pk=sales_item_id)        
    if request.method == 'POST':                
        form = SalesItemForm(request.POST, instance=sales_item)
        if form.is_valid():
            sales_item = form.save()
            if sales_item_id is not None:
                # Only successful Edit (POST) --> rendering only the changed row
                variables = {'sales_items' : [sales_item]}
                return render(request, '_sales_item_rows.html', variables)        
        else:
            validation_error_ajax = True;
            if sales_item_id is None:
                # Only unsuccessful Add (POST) --> rendering only the invalid Add row
                variables = {'form' : form, 'validation_error_ajax' : validation_error_ajax}
                return render(request, 'sales_item_add_save_form.html', variables)
    else:
        form = SalesItemForm(instance=sales_item)
    if sales_item_id is None:
        # Only first-time GET Add or Successful Add (POST) --> The List incl. paginators will get updated
        sales_items_queryset = profile.company.salesitem_set.all().order_by('item_name')
        sales_items, paginator, page, page_number = makePaginator(request, ITEMS_PER_PAGE, sales_items_queryset)        
        variables = {
                     'sales_items': sales_items, 'form':form, 'source':source,
                     'salesitem_id' : sales_item_id, 'validation_error_ajax' : validation_error_ajax, 'get_request':get_request_parameters(request)
                     }
        variables = merge_with_additional_variables(request, paginator, page, page_number, variables)
        return render(request, 'sales_item_list.html', variables)
    else:
        # Only first-time GET Edit or invalid POST Edit --> Edit Save row will be rendered
        variables = {
                     'form':form, 'salesitem_id' : sales_item_id, 'validation_error_ajax' : validation_error_ajax, 'source':source 
                    }        
        return render(request, 'sales_item_edit_save_form.html', variables)

@login_required
def sales_item_delete(request, sales_item_id=None):
    source = 'sales_items/'  
    if sales_item_id is None:
        raise Http404(_(u'Sales item not found'))
    else:
        profile = request.user.get_profile()
        sales_item = get_object_or_404(profile.company.salesitem_set.all(), pk=sales_item_id)
        sales_item.delete()                
        sales_items_queryset = profile.company.salesitem_set.all().order_by('item_name')   
        sales_items, paginator, page, page_number = makePaginator(request, ITEMS_PER_PAGE, sales_items_queryset)    
        #New SalesItem form for adding a possible new one on UI
        sales_item = SalesItem(company=profile.company)
        form = SalesItemForm(instance=sales_item)        
        variables = { 'sales_items': sales_items, 'form':form, 'source':source}
        variables = merge_with_additional_variables(request, paginator, page, page_number, variables)
    return render(request, 'sales_item_list.html', variables)




@login_required
def deal_template_display(request):    
    profile = request.user.get_profile()
    deal_templates_queryset = profile.company.dealtemplate_set.order_by('deal_name')
    ajax = False
    if 'ajax' in request.GET:
        ajax = True        
        if 'deal_name' in request.GET:    
            deal_name = request.GET['deal_name']
            deal_templates_queryset = deal_templates_queryset.filter(deal_name__icontains=deal_name).order_by('deal_name')
        if 'sales_item' in request.GET:            
            sales_item_keywords = request.GET.getlist('sales_item')
            # Q are queries that can be stacked with Or operators. If none of the Qs contains any value, `reduce` minimizes them to no queryset,             
            q_filters = reduce(operator.or_, (Q(item_name__icontains=item.strip()) for item in sales_item_keywords))
            sales_items = profile.company.salesitem_set.filter(q_filters)       
            deal_templates_queryset = deal_templates_queryset.filter(sales_item__in=sales_items)
        if 'price' in request.GET:    
            price = request.GET['price']
            deal_templates_queryset = deal_templates_queryset.filter(price__icontains=price).order_by('price')
        if 'sales_term' in request.GET:    
            sales_term = request.GET['sales_term']
            sales_terms = SalesTerm.objects.filter(sales_term__icontains=sales_term)
            deal_templates_queryset = deal_templates_queryset.filter(sales_term__in=sales_terms)
        if 'quantity' in request.GET:    
            quantity = request.GET['quantity']
            deal_templates_queryset = deal_templates_queryset.filter(quantity__icontains=quantity).order_by('quantity')    
    
    source = 'deal_templates/'
    filter_form = FilterDealTemplateForm(profile.company, request.GET)            
    deal_templates, paginator, page, page_number = makePaginator(request, ITEMS_PER_PAGE, deal_templates_queryset)    
    variables = {
                 'deal_templates': deal_templates, 'filter_form' : filter_form, 'source':source
                 }
    variables = merge_with_additional_variables(request, paginator, page, page_number, variables)
    if ajax:    
        return render(request, 'deal_template_list.html', variables)
    else:
        return render(request, 'deal_templates.html', variables)
    

@login_required
def deal_template_add_edit(request, deal_id=None):
    profile = request.user.get_profile()
    source = 'deal_templates/'    
    if deal_id is None:
        deal = DealTemplate(company=profile.company)        
        template_title = _(u'Add New Deal Template')
    else:
        deal = get_object_or_404(profile.company.dealtemplate_set.all(), pk=deal_id)
        template_title = _(u'Edit Deal Template')
    if request.method == 'POST':
        form = DealTemplateForm(request.POST, instance=deal)
        if form.is_valid():
            deal = form.save()
            
            deal_templates_queryset = profile.company.dealtemplate_set.order_by('deal_name')                        
            deal_templates, paginator, page, page_number = makePaginator(request, ITEMS_PER_PAGE, deal_templates_queryset)    
            variables = {
                         'deal_templates': deal_templates, 'source':source
                         }
            variables = merge_with_additional_variables(request, paginator, page, page_number, variables)
            return render(request, 'deal_templates.html', variables)
    else:
        form = DealTemplateForm(instance=deal)    
    variables = {'form':form, 'template_title': template_title}
    return render(request, 'deal_template.html', variables)


@login_required
def deal_template_delete(request, deal_id=None):
    if deal_id is None:
        raise Http404(_(u'Deal Type not found'))
    else:
        profile = request.user.get_profile()
        deal_template = get_object_or_404(profile.company.dealtemplate_set.all(), pk=deal_id)
        deal_template.delete()
        deal_templates_queryset = profile.company.dealtemplate_set.order_by('deal_name')   
        deal_templates, paginator, page, page_number = makePaginator(request, ITEMS_PER_PAGE, deal_templates_queryset)
        source = 'deal_templates/'          
        variables = { 'deal_templates': deal_templates, 'source':source}
        variables = merge_with_additional_variables(request, paginator, page, page_number, variables)
    return render(request, 'deal_template_list.html', variables)
    

@login_required
def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/')

def register_page(request):    
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')    
    if request.method == 'POST':
        if 'invitation' in request.session:
            invitation = Invitation.objects.get(id=request.session['invitation'])
            profile = invitation.sender.get_profile()            
            form = RegistrationForm(request.POST, is_accept_invite = True, _company_name = profile.company.company_name, _company_email = profile.company.company_email, _email = invitation.email)
        else:
            form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password2'],
                email=form.cleaned_data['email']                
            )
            
            if 'invitation' in request.session:
                # Retrieve the invitation object.
                invitation = Invitation.objects.get(id=request.session['invitation'])                
                profile = invitation.sender.get_profile()                
                userProfile = UserProfile(user=user, company = profile.company, is_cb_superuser=False, license = profile.license)
                userProfile.save()
                # Delete the invitation from the database and session.
                invitation.delete()
                del request.session['invitation']
            else:            
                company = Company.objects.create(
                    company_name = form.cleaned_data['company_name'],
                    company_email = form.cleaned_data['company_email']
                )
                userProfile = UserProfile(user=user, company = company, is_cb_superuser=True, license = LicenseTemplate.objects.get(pk=2))
                userProfile.save()

            return HttpResponseRedirect('/register/success/')
    else:
        if 'invitation' in request.session:
            invitation = Invitation.objects.get(id=request.session['invitation'])
            profile = invitation.sender.get_profile()            
            form = RegistrationForm(is_accept_invite = True, _company_name = profile.company.company_name, _company_email = profile.company.company_email, _email = invitation.email)
        else:            
            form = RegistrationForm()
    variables = {'form':form}    
    return render(request, 'registration/register.html', variables)




def GenerateUsername():
    i = 0
    MAX = 1000000
    while(i < MAX):
        username = str(random.randint(0,MAX))
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
    raise Exception('All random username are taken')





@login_required
def charts_display(request, contact_id):
    profile = request.user.get_profile()
    contact = get_object_or_404(profile.company.contact_set.all(), pk=contact_id)
    deals = contact.deal_set.all().order_by('deal_id', 'deal_datetime')
    stac = {'VEM':0, 'EM':0, 'LM':0, 'EA':0, 'LA':0, 'EE':0, 'LE':0}
    for deal in deals:        
        part = part_of_day_statistics(deal.conversation.conversation_datetime)
        stac[part] += 1    
    variables = {'deals':deals, 'stac':stac, 'contact':contact}    
    return render(request, 'charts.html', variables)



def sales_item_autocomplete(request):
    if 'query' in request.GET:
        #Get the prerequisite fields for autocomplete
        profile, kwargs, fieldname = get_fields_for_autocomplete(request)
        #filter the related queryset with the prereq fields
        queryset = profile.company.salesitem_set.filter(**kwargs)[:10]
        #prepare the json convertion from the search items we found  
        to_json = prepare_json_for_autocomplete(fieldname, queryset)
        return HttpResponse(simplejson.dumps(to_json), mimetype='application/json')        
    return HttpResponse()

def contacts_autocomplete(request):
    if 'query' in request.GET:
        profile, kwargs, fieldname = get_fields_for_autocomplete(request)
        queryset = profile.company.contact_set.filter(**kwargs)[:10]
        to_json = prepare_json_for_autocomplete(fieldname, queryset)
        return HttpResponse(simplejson.dumps(to_json), mimetype='application/json')        
    return HttpResponse()

def opendeal_autocomplete(request):
    if 'query' in request.GET:
        profile, kwargs, fieldname = get_fields_for_autocomplete(request)
        queryset = all_open_deals(request, profile.company).filter(**kwargs)[:10]
        to_json = prepare_json_for_autocomplete(fieldname, queryset)
        return HttpResponse(simplejson.dumps(to_json), mimetype='application/json')        
    return HttpResponse()

def deal_autocomplete(request):
    if 'query' in request.GET:
        profile, kwargs, fieldname = get_fields_for_autocomplete(request)
        try:
            queryset = profile.company.dealtemplate_set.filter(**kwargs)[:10]
        except:
            # Foreignkey related fields must folow this pattern
            if fieldname == 'sales_term':
                #First see which of the generic sales_terms the user tried to search against
                sales_term = SalesTerm.objects.filter(sales_term__istartswith=request.GET['query'])
                #Now that we know, let see which of the existing deal_templates have such sales_terms we were searching for previously 
                deal_templates = profile.company.dealtemplate_set.filter(sales_term__in=sales_term)
                #Create a queryset dictionary to eliminate the double entries
                queryset = {}
                for deal in deal_templates:                    
                    if queryset.has_key(deal.sales_term):
                        continue             
                    #store the DealTemplate's sales term as one possible search suggestion...
                    queryset[deal.sales_term]=deal.sales_term
            
            # Many-to-Many relationship fields must follow this pattern                
            elif fieldname == 'sales_item':
                #First see which of the company wide generated sales items the user tried to search against
                sales_item = profile.company.salesitem_set.filter(item_name__istartswith=request.GET['query'])
                #Now that we know, let see which of the existing deal_templates have such sales_item(s) we were searching for previously
                deal_templates = profile.company.dealtemplate_set.filter(sales_item__in=sales_item)
                #Create a queryset dictionary to eliminate the double entries
                queryset = {}
                for deal in deal_templates:
                    #Since its M2M, each DealTemplate's sales_item could point to several items itself, hence another loop is required
                    for si in deal.sales_item.select_related():
                        if queryset.has_key(si):
                            continue                        
                        queryset[si]=si
                #Now that we captured all possible sales_items that are used in DealTemplate instances
                #We need to change the fieldname we search against to the name of sales_item's field instead so that the json method after here works. 
                fieldname = 'item_name'
                
        to_json = prepare_json_for_autocomplete(fieldname, queryset)
        return HttpResponse(simplejson.dumps(to_json), mimetype='application/json')        
    return HttpResponse()

def conversations_autocomplete(request, contact_id):
    if 'query' in request.GET:
        profile, kwargs, fieldname = get_fields_for_autocomplete(request)
        contact = profile.company.contact_set.get(pk=contact_id)
        queryset = contact.conversation_set.filter(**kwargs)[:10]        
        to_json = prepare_json_for_autocomplete(fieldname, queryset)
        return HttpResponse(simplejson.dumps(to_json), mimetype='application/json')        
    return HttpResponse()

#Returns the profile, the passed in fieldname to search against and the kwargs that is teh filter expression
def get_fields_for_autocomplete(request):
    profile = request.user.get_profile()
    fieldname = request.GET['fieldname']
    kwargs = {'%s__istartswith' % (fieldname):request.GET['query']}
    return profile, kwargs, fieldname

#It goes through the queryset and and adds the possible search candidates to a list to be sent later as json.
def prepare_json_for_autocomplete(fieldname, queryset):                    
    to_json = []
    for item in queryset:
        to_json.append(str(getattr(item, fieldname)))
    return to_json


@login_required
def colleague_invite(request):
    profile = request.user.get_profile()
    if not profile.is_cb_superuser:
        return HttpResponseForbidden()
    
    if request.method == 'POST':
        form = ColleagueInviteForm(request.POST)
        if form.is_valid():
            invitation = Invitation(
                                    name=form.cleaned_data['name'],
                                    email=form.cleaned_data['email'],
                                    code=User.objects.make_random_password(20),
                                    sender=request.user
                                    )
            invitation.save()
            try:
                invitation.send()                
                messages.success(request, _(u'An invitation was sent to %(name)s.') % {'name' : invitation.email})
            except Exception:                
                messages.error(request, _(u'An error happened when sending the invitation.'))            
            return HttpResponseRedirect('/colleague/invite/')
    else:
        form = ColleagueInviteForm()
    
    user_profiles = profile.company.userprofile_set.all()
       
    license_template = profile.license
    count = (license_template.max_users-len(user_profiles))
    template_announcement_1 = ungettext(u'Currently you can invite %(count)s more colleague to Chasebot', u'Currently you can invite %(count)s more colleagues to Chasebot', count) % {'count' : count}
    variables = {'form': form, 'license': license_template, 'user_profiles':user_profiles, 'template_announcement_1':template_announcement_1}
    return render(request, 'registration/colleague_invite.html', variables)


def colleague_accept(request, code):
    invitation = get_object_or_404(Invitation, code__exact=code)
    request.session['invitation'] = invitation.id
    return HttpResponseRedirect('/register/')
    
@login_required
def sidebar_contacts(request):
    filter_form = FilterContactsForm()
    variables = { 'filter_form':filter_form }
    return render(request, 'contacts_sidebar.html', variables)

@login_required
def sidebar_deal_templates(request):
    profile = request.user.get_profile()
    filter_form = FilterDealTemplateForm(profile.company)
    variables = { 'filter_form':filter_form }
    return render(request, 'deal_template_sidebar.html', variables)    

@login_required
def sidebar_open_deals(request):    
    filter_form = FilterOpenDealForm()
    variables = { 'filter_form':filter_form }
    return render(request, 'open_deal_sidebar.html', variables)

@login_required
def sidebar_conversations(request, contact_id):
    profile = request.user.get_profile()
    filter_form = FilterConversationForm()
    contact = get_object_or_404(profile.company.contact_set.all(), pk=contact_id)
    variables = { 'filter_form':filter_form, 'contact':contact }
    return render(request, 'conversations_sidebar.html', variables)

def part_of_day_statistics(x):
    if x.hour >= 6 and x.hour < 9:
        return 'EM'
    if x.hour >= 9 and x.hour < 12:
        return 'LM'
    if x.hour >= 12 and x.hour < 15:
        return 'EA'
    if x.hour >= 15 and x.hour < 18:
        return 'LA'
    if x.hour >= 18 and x.hour < 21:
        return 'EE'
    if x.hour >= 21 and x.hour < 24:
        return 'LE'
    if x.hour >= 0 and x.hour < 6:
        return 'VEM'

def get_datepicker_format(request):
    if request.LANGUAGE_CODE == 'en':
        locale = 'mm/dd/yyyy'
    else:
        locale = 'dd/mm/yyyy'
    return locale


def makePaginator(request, ITEMS_PER_PAGE, queryset):
    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    try:
        page_number = int(request.GET['page'])
    except (KeyError, ValueError):
        page_number = 1
    try:
        page = paginator.page(page_number)
    except InvalidPage:
        raise Http404
    objects = page.object_list
    return objects, paginator, page, page_number


def get_request_parameters(request):    
    get_request = '?ajax'
    for key, value in request.GET.iteritems():
        if key == 'ajax' or key == 'modal':
            continue        
        get_request = get_request + '&' + key + '=' + value
    return get_request


def get_paginator_variables(paginator, page, page_number, custom_prefix):
    if custom_prefix:
        return {
                custom_prefix + 'show_paginator': paginator.num_pages > 1, 
                custom_prefix + 'has_prev': page.has_previous(), 
                custom_prefix + 'has_next': page.has_next(), 
                custom_prefix + 'page': page_number, 
                custom_prefix + 'pages': paginator.num_pages, 
                custom_prefix + 'next_page': page_number + 1, 
                custom_prefix + 'prev_page': page_number - 1                
                }
    else:
        return {
                'show_paginator': paginator.num_pages > 1, 
                'has_prev': page.has_previous(), 
                'has_next': page.has_next(), 
                'page': page_number, 
                'pages': paginator.num_pages, 
                'next_page': page_number + 1, 
                'prev_page': page_number - 1                
                }

def get_localized_variables(request):
    timezone = request.session['django_timezone'].zone
    return { 'locale' : get_datepicker_format(request), 'timezones': pytz.common_timezones, 'timezone':timezone}  

def merge_with_additional_variables(request, paginator, page, page_number, variables):
    variables = dict(variables.items() + get_paginator_variables(paginator, page, page_number, None).items() + get_localized_variables(request).items())
    return variables

def merge_with_localized_variables(request, variables):
    variables = dict(variables.items() + get_localized_variables(request).items())
    return variables

def merge_with_pagination_variables(paginator, page, page_number, variables, custom_prefix):
    variables = dict(variables.items() + get_paginator_variables(paginator, page, page_number, custom_prefix).items())
    return variables

@register.inclusion_tag('tag_form_label_tr.html')
def show_row_tr(form_field, *args, **kwargs):
    ignore_error_text = False
    if 'ignore_error_text' in kwargs:
        ignore_error_text = True
    return {'form_field': form_field, 'ignore_error_text':ignore_error_text}


@register.inclusion_tag('tag_form_label_div.html')
def show_row_div(form_field, *args, **kwargs):
    ignore_error_text = False
    if 'ignore_error_text' in kwargs:
        ignore_error_text = True
    return {'form_field': form_field, 'ignore_error_text':ignore_error_text}

@register.inclusion_tag('tag_form_label_time_div.html')
def show_row_time_div(form_field, *args, **kwargs):
    ignore_error_text = False
    if 'ignore_error_text' in kwargs:
        ignore_error_text = True
    return {'form_field': form_field, 'ignore_error_text':ignore_error_text}

#@login_required

#def _deal_status_view(request, call_id=None):        
#    conversation_deal = Conversation_Deal.objects.filter(conversation_id__in=call_id)    
#    deal_statuses = DealStatus.objects.all()        
#    all = list(Conversation_Deal.objects.filter(conversation_id__in=call_id)) + list(DealStatus.objects.all())
#    
#    to_json =  [ {"deal_pk": 1, "fields": [{"selected": "true", "status": "Pending 0%"}, {"selected": "false", "status": "Pending 25%"} ]}, {"deal_pk": 2, "fields": [{"selected": "false", "status": "Pending 0%"}, {"selected": "true", "status": "Pending 25%"} ]} ]  
#   
#    return HttpResponse(simplejson.dumps(to_json), mimetype='application/json')



