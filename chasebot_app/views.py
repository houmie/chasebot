from datetime import datetime
from datetime import timedelta
from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from chasebot_app.forms import RegistrationForm, ContactsForm, ConversationForm, ProductsForm, DealTemplateForm,\
     DealForm, FilterContactsForm, FilterConversationForm, FilterDealTemplateForm, FilterProductsForm,\
    DealsAddForm, OpenDealsAddForm, ColleagueInviteForm, \
    EventForm, DealNegotiateForm, FilterOpenDealForm, FeedbackForm,\
    AddNewDealForm, DealsAddFormLight
from chasebot_app.models import Company, Contact, Conversation, Products, DealTemplate, Deal, SalesTerm,\
    Invitation, LicenseTemplate, MaritalStatus, \
    Currency, Event, DealStatus, CBLogging, Conversation_history,\
    Deal_history, Contact_history, Event_history, Products_history,\
    DealTemplate_history
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
from django.core.mail import send_mail
from chasebot import settings
from chasebot_app.utils import get_user_location_details, get_user_browser


ITEMS_PER_PAGE = 9

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
    date_time_unaware = datetime.strptime(date, get_current_date_input_format(request))
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
def feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            send_mail('Feedback', form.cleaned_data['feedback'] + ' username: ' + request.user.username, settings.DEFAULT_FROM_EMAIL, [settings.DEFAULT_FROM_EMAIL])
            messages.info(request, _(u'Thank you for your feedback.'))
            return render(request, 'messages.html')
    else:
        form = FeedbackForm()
    variables = {'form':form}    
    return render(request, 'feedback.html', variables)

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
    if 'demo' in request.GET:
        messages.success(request, _(u'Congratulations. Your free account is now ready.'))
        messages.warning(request, _(u'Once happy with the testing, You may delete all the demo data and start entering your own data.'))

    profile = request.user.get_profile()
    if not 'django_timezone' in request.session: 
        request.session['django_timezone'] = pytz.timezone(profile.timezone)
    company_name = profile.company.company_name
    variables = {'company_name': company_name, 'user_name' : request.user}
    variables = merge_with_localized_variables(request, variables)
    return render(request, 'index.html', variables)        


@login_required
def open_deals_display(request):
    profile = request.user.get_profile()
    ajax = False    
#    if 'page' in request.GET:
#        size = 10
#        if 'size' in request.GET:
#            size = request.GET['size']
#                    
#        queryset = all_open_deals(request, profile.company)
#        paginator = Paginator(queryset, size)
#        page_nr = int(request.GET['page']) + 1
#        try:
#            page = paginator.page(page_nr)
#        except InvalidPage:
#            raise Http404
#        objects = page.object_list
#        # Manual json creation
#        to_json = {}
#        to_json['total_rows'] = paginator.count
#        to_json['cols'] = ["deal_instance_name",]
#        to_json['rows'] = []           
#        for item in objects:                        
#            to_json['rows'].append({ 'deal_instance_name': str(getattr(item, 'deal_instance_name')) })
#        return HttpResponse(simplejson.dumps(to_json), mimetype='application/json')
    if 'ajax' in request.GET:
        ajax = True
        deals_query = all_open_deals(request, profile.company)
        
        if 'deal_instance_name' in request.GET:    
            deal_instance_name = request.GET['deal_instance_name']
            deals_query = deals_query.filter(deal_instance_name__icontains=deal_instance_name).order_by('deal_instance_name')
        if 'status' in request.GET:    
            status = request.GET['status']
            deals_query = deals_query.filter(status__deal_status__icontains=status).order_by('status')
        if 'last_contacted' in request.GET:    
            last_contacted = request.GET['last_contacted']            
            current_tz = timezone.get_current_timezone()
            try:
                date_time = current_tz.localize(datetime.strptime(last_contacted, get_current_date_input_format(request)))
                date_min = date_time.replace(hour=0, minute=0, second=0)
                date_max = date_time.replace(hour=23, minute=59, second=59)                        
                deals_query = deals_query.filter(deal_datetime__range=(date_min, date_max))
            except:
                pass            
        if 'total_value' in request.GET:    
            total_value = request.GET['total_value']
            deals_query = deals_query.filter(total_value__icontains=total_value).order_by('total_value')
    else:
        deals_query = all_open_deals(request, profile.company)
    
    #deals, paginator, page, page_number = makePaginator(request, 20, deals_query)
    source = '/open_deals'
    variables = {'deals': deals_query, 'source':source}
    #variables = merge_with_additional_variables(request, paginator, page, page_number, variables)
    if ajax:
        return render(request, 'open_deals_list.html', variables)
    else:
        return render(request, 'open_deals.html', variables)

@login_required
def load_open_deals_variables(request, profile):
    deals_query = all_open_deals(request, profile.company)
    deals, paginator, page, page_number = makePaginator(request, 20, deals_query)  
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
def add_new_deal_from_template(request):
    profile = request.user.get_profile()
    validation_error_ajax = False    
    
    if request.method == 'POST':
        form = AddNewDealForm(request.POST, company = profile.company)        
        if form.is_valid():            
            # Always localize the entered date by user into his timezone before saving it to database
            current_tz = timezone.get_current_timezone() 
            call = Conversation(contact=form.cleaned_data['addnewdeal_contact'], conversation_datetime = current_tz.normalize(timezone.now().astimezone(current_tz)), notes=form.cleaned_data['call_notes'], user=request.user)
            call.save()
            
            log = log_call(request, call, 'add_new_deal_from_template', 'call saved', profile, False)
            
            new_deal = form.save(commit=False)            
            deal = Deal.objects.create(
                                deal_id =       new_deal.deal_id,
                                deal_datetime = call.conversation_datetime, 
                                status =        new_deal.status, 
                                contact =       call.contact, 
                                deal_template = new_deal.deal_template,
                                deal_template_name = new_deal.deal_template_name,  
                                conversation =  call,                                            
                                deal_instance_name = new_deal.deal_instance_name,
                                deal_description = new_deal.deal_description,
                                price =         new_deal.price,        
                                currency =      new_deal.currency,                
                                sales_term =    new_deal.sales_term,
                                quantity =      new_deal.quantity,
                                company =       profile.company,
                                user = request.user                                            
                                )
            #Saving M2M 
            for item in form.cleaned_data['product']:
                deal.product.add(item)
            deal.save();

            log_deal(request, deal, form.cleaned_data['product'], 'add_new_deal_from_template', 'deal saved', profile, False, log)

            variables = load_open_deals_variables(request, profile)
            return render(request, 'open_deals.html', variables)
    else:        
        form = DealsAddFormLight(company = profile.company)
        fs = AddNewDealForm(company = profile.company)
        
    variables = {'deals_add_form':form, 'fs': fs, 'validation_error_ajax':validation_error_ajax }
    return render(request, '_add_deals_from_template.html', variables)

def log_contact(request, contact, primary_action, secondary_action, profile, is_edit):
    if profile.is_log_active == False:
        return           
    ch = Contact_history(    first_name=contact.first_name,
                             last_name=contact.last_name,
                             dear_name=contact.dear_name,
                             address=contact.address,
                             city=contact.city,
                             state=contact.state,
                             postcode=contact.postcode,
                             country=contact.country,
                             company_name=contact.company_name,
                             position=contact.position,
                             phone=contact.phone,    
                             mobile_phone=contact.mobile_phone,
                             fax_number=contact.fax_number,
                             email=contact.email,
                             birth_date=contact.birth_date,
                             prev_meeting_places=contact.prev_meeting_places,
                             referred_by=contact.referred_by,
                             contact_notes=contact.contact_notes,
                             marital_status=contact.marital_status,
                             gender=contact.gender,
                             contacts_interests=contact.contacts_interests,
                             pet_names=contact.pet_names,
                             spouse_first_name=contact.spouse_first_name,
                             spouse_last_name=contact.spouse_last_name,
                             spouses_interests=contact.spouses_interests,
                             children_names=contact.children_names,
                             home_town=contact.home_town,
                             company=contact.company,
                             important_client=contact.important_client, 
                             user = contact.user                            
                         )
    if is_edit:
        ch.edit_id=contact.pk
        
    ch.save()
    log = CBLogging(user = request.user, primary_action = primary_action)
    log.save(request)
    log.cbaction_set.create(secondary_action = secondary_action,  history_id = ch.pk, history_type = 'contact')    


def log_dealtemplate(request, dealtemplate, primary_action, secondary_action, profile, is_edit):
    if profile.is_log_active == False:
        return
    dh = DealTemplate_history(company             = dealtemplate.company,
                              deal_name           = dealtemplate.deal_name,
                              deal_description    = dealtemplate.deal_description,                              
                              currency            = dealtemplate.currency,
                              price               = dealtemplate.price,
                              sales_term          = dealtemplate.sales_term,
                              quantity            = dealtemplate.quantity,
                              user                = dealtemplate.user
                          )
    if is_edit:
        dh.edit_id=dealtemplate.pk
    dh.save()
    for item in dealtemplate.product.all():
        dh.product.add(item)
    dh.save()    
    log = CBLogging(user = request.user, primary_action = primary_action)
    log.save(request)
    log.cbaction_set.create(secondary_action = secondary_action,  history_id = dh.pk, history_type = 'deal_template')
    

def log_product(request, product, primary_action, secondary_action, profile, is_edit):
    if profile.is_log_active == False:
        return
    ph = Products_history(item_name = product.item_name,
                          company   = product.company,
                          user      = product.user
                          )
    if is_edit:
        ph.edit_id=product.pk
    ph.save()    
    log = CBLogging(user = request.user, primary_action = primary_action)
    log.save(request)
    log.cbaction_set.create(secondary_action = secondary_action,  history_id = ph.pk, history_type = 'product')
    

def log_event(request, event, primary_action, secondary_action, profile, is_edit):
    if profile.is_log_active == False:
        return
    eh = Event_history(type = event.type,
                       due_date_time = event.due_date_time,
                       reminder_date_time = event.reminder_date_time,
                       reminder = event.reminder,
                       is_public = event.is_public,
                       contact = event.contact,
                       deal_id = event.deal_id,
                       company = event.company,
                       user = event.user,
                       notes = event.notes,
                       is_reminder_sent = event.is_reminder_sent
                       )
    if is_edit:
        eh.edit_id=event.pk
    eh.save()
    log = CBLogging(user = request.user, primary_action = primary_action)
    log.save(request)
    log.cbaction_set.create(secondary_action = secondary_action,  history_id = eh.pk, history_type = 'event')
    

def log_call(request, call, primary_action, secondary_action, profile, is_edit):
    if profile.is_log_active == False:
        return
    ch = Conversation_history(contact=call.contact, 
                              conversation_datetime = call.conversation_datetime, 
                              notes=call.notes,
                              user   = call.user
                              )
    if is_edit:
        ch.edit_id=call.pk
    ch.save()
    log = CBLogging(user = request.user, primary_action = primary_action)
    log.save(request)
    log.cbaction_set.create(secondary_action = secondary_action,  history_id = ch.pk, history_type = 'call')    
    return log

def log_deal(request, deal, products, primary_action, secondary_action, profile, is_edit, log=None):
    if profile.is_log_active == False:
        return
    dh = Deal_history.objects.create(
                                deal_id =       deal.deal_id,
                                deal_datetime = deal.deal_datetime, 
                                status =        deal.status, 
                                contact =       deal.contact, 
                                deal_template = deal.deal_template,
                                deal_template_name = deal.deal_template_name,  
                                conversation =  deal.conversation,                                            
                                deal_instance_name = deal.deal_instance_name,
                                deal_description = deal.deal_description,
                                price =         deal.price,        
                                currency =      deal.currency,                
                                sales_term =    deal.sales_term,
                                quantity =      deal.quantity,
                                company =       deal.company,
                                user =          deal.user                                         
                                )     
    if is_edit:
        dh.edit_id=deal.pk
    for item in products:
        dh.product.add(item)
    dh.save();   
    
    if log is None:
        log = CBLogging(user = request.user, primary_action = primary_action)
    log.save(request)
    log.cbaction_set.create(secondary_action = secondary_action,  history_id = dh.pk, history_type = 'deal')
    


@login_required
def add_new_deal(request):
    profile = request.user.get_profile()
    validation_error_ajax = False
    if request.method == 'POST':
        form = AddNewDealForm(request.POST, company = profile.company)        
        if form.is_valid():
            # Always localize the entered date by user into his timezone before saving it to database
            current_tz = timezone.get_current_timezone() 
            call = Conversation(contact=form.cleaned_data['addnewdeal_contact'], conversation_datetime = current_tz.normalize(timezone.now().astimezone(current_tz)), notes=form.cleaned_data['call_notes'], user=request.user)
            call.save()
            
            log = log_call(request, call, 'add_new_deal', 'call saved', profile, False)
            
            new_deal = form.save(commit=False)            
            deal = Deal.objects.create(
                                deal_id =       new_deal.deal_id,
                                deal_datetime = call.conversation_datetime, 
                                status =        new_deal.status, 
                                contact =       call.contact, 
                                deal_template = new_deal.deal_template,
                                deal_template_name = new_deal.deal_template_name,  
                                conversation =  call,                                            
                                deal_instance_name = new_deal.deal_instance_name,
                                deal_description = new_deal.deal_description,
                                price =         new_deal.price,        
                                currency =      new_deal.currency,                
                                sales_term =    new_deal.sales_term,
                                quantity =      new_deal.quantity,
                                company =       profile.company                                            
                                )
            #Saving M2M 
            for item in form.cleaned_data['product']:
                deal.product.add(item)
            deal.save();
            
            log_deal(request, deal, form.cleaned_data['product'], 'add_new_deal', 'save deal', profile, False, log)
            
            variables = load_open_deals_variables(request, profile)
            return render(request, 'open_deals.html', variables)
        else:
            validation_error_ajax = True    
            
    else:
        form = AddNewDealForm(company = profile.company)
        
    variables = {'fs':form, 'validation_error_ajax':validation_error_ajax }
    return render(request, '_deal_edit_item.html', variables)         

@login_required
def negotiate_open_deal(request, deal_pk):
    profile = request.user.get_profile()
    actual_deal = get_object_or_404(profile.company.deal_set.all(), pk=deal_pk)
    validation_error_ajax = False

    if request.method == 'POST':        
        form = DealNegotiateForm(request.POST, instance=actual_deal)
        
        if form.is_valid():
            # Always localize the entered date by user into his timezone before saving it to database
            current_tz = timezone.get_current_timezone() 
            call = Conversation(contact=actual_deal.contact, conversation_datetime = current_tz.normalize(timezone.now().astimezone(current_tz)), notes=form.cleaned_data['call_notes'], user=request.user)
            call.save()
            
            log = log_call(request, call, 'negotiate_open_deal', 'call saved', profile, False)
            
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
            for item in form.cleaned_data['product']:
                deal.product.add(item)
            deal.save();
            
            log_deal(request, deal, form.cleaned_data['product'], 'negotiate_open_deal', 'deal saved', profile, False, log)
            
            #In case the instance name was changed we change also all other instance names of the same set.
            adjust_deal_names_of_same_dealset(request, deal.contact, deal, profile)                                
            
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
    secondary = ''    
    is_edit = False
    if contact_id is None:
        contact = Contact(company=profile.company, user=request.user)
        template_title = _(u'Add New Contact')
        secondary = 'Add New Contact'
    else:
        is_edit = True
        contact = get_object_or_404(profile.company.contact_set.all(), pk=contact_id)
        template_title = _(u'Edit Contact')
        secondary = 'Edit Contact'
    if request.method == 'POST':
        form = ContactsForm(request.POST, instance=contact)
        if form.is_valid():
            contact = form.save()
            log_contact(request, contact, 'contact_add_edit', secondary, profile, is_edit)

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
        log_contact(request, contact, 'contact_delete', '', profile, False)
        contact.delete()
        contacts_queryset = profile.company.contact_set.order_by('last_name')
        contacts, paginator, page, page_number = makePaginator(request, ITEMS_PER_PAGE, contacts_queryset)
        source = '/contacts'    
        variables = { 'contacts': contacts, 'source':source}
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
                current_tz = timezone.get_current_timezone()                
                to_date = current_tz.normalize(timezone.now().astimezone(current_tz))
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

@login_required
def adjust_deal_names_of_same_dealset(request, contact, deal, profile):
    set_of_same_deal = contact.deal_set.filter(deal_id=deal.deal_id)
    for sdeal in set_of_same_deal:
        if sdeal.pk != deal.pk:
            if sdeal.deal_instance_name != deal.deal_instance_name:
                sdeal.deal_instance_name = deal.deal_instance_name
                sdeal.save()
                log_deal(request, sdeal, sdeal.product.all(), 'adjust_deal_names_of_same_dealset', 'deal saved', profile, True)


@login_required
def conversation_add_edit(request, contact_id, call_id=None):
    profile = request.user.get_profile()
    contact = get_object_or_404(profile.company.contact_set.all(), pk=contact_id)
    secondary = '' 
    is_edit = False
    if call_id is None:
        current_tz = timezone.get_current_timezone()
        call = Conversation(contact=contact, conversation_datetime = current_tz.normalize(timezone.now().astimezone(current_tz)), user=request.user) 
        template_title = _(u'Add New Conversation')
        secondary = 'Add New Conversation'
    else:
        is_edit = True
        call = get_object_or_404(contact.conversation_set.all(), pk=call_id)
        template_title = _(u'Edit Conversation')
        secondary = 'Edit Conversation'
    
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
            date_time = current_tz.localize(datetime(date.year, date.month, date.day, time.hour, time.minute))                        
            call.conversation_datetime = date_time
            call.save()            
            log = log_call(request, call, 'conversation_add_edit', secondary, profile, is_edit)
            
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
                        for item in fm.cleaned_data['product']:
                            deal.product.add(item)
                        deal.save();
                        
                        log_deal(request, deal, fm.cleaned_data['product'], 'conversation_add_edit', 'continue with open deal', profile, False, log)
                        
                        #In case the instance name was changed we change also all other instance names of the same set.
                        adjust_deal_names_of_same_dealset(request, contact, deal, profile)
                        
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
                        secondary = ''
                        is_edit = False
                        if deal.pk:                        
                            #In case the instance name was changed we change also all other instance names of the same set.
                            adjust_deal_names_of_same_dealset(request, contact, deal, profile)
                            secondary = 'deal edited'
                            is_edit = True
                        else:
                            secondary = 'new deal added'
                        deal.save()
                        fm.save_m2m()
                        
                        log_deal(request, deal, fm.cleaned_data['product'], 'conversation_add_edit', secondary, profile, is_edit, log)
                        
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
    current_tz = timezone.get_current_timezone(); 
    user_date = current_tz.normalize(timezone.now().astimezone(current_tz))
    variables = {'form':form, 'template_title':template_title, 'deals_add_form':deals_add_form, 'opendeals_add_form':opendeals_add_form, 'attached_deals_formset':attached_deals_formset, 'contact_id':contact.pk, 'call_id':call_id, 'extra_deal_formset':extra_deal_formset, 'validation_error_ajax':validation_error_ajax, 'user_date':user_date }    
    return render(request, '_conversation_edit.html', variables)      


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
        log_call(request, call, 'call_delete', '', profile, False)
        call.delete()
        call_queryset = contact.conversation_set.order_by('-conversation_datetime')   
        calls, paginator, page, page_number = makePaginator(request, ITEMS_PER_PAGE, call_queryset)
        source = u'{0}/{1}/{2}'.format('contact', contact.pk, 'calls')          
        variables = { 'calls': calls, 'contact':contact, 'source':source }
        variables = merge_with_additional_variables(request, paginator, page, page_number, variables)
    return render(request, 'conversation_list.html', variables)

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
    is_edit = False    
    if event_id is None and open_deal_id:
        deal = get_object_or_404(profile.company.deal_set.all(), pk=open_deal_id)
        event = Event(company=profile.company, user=request.user, deal_id=deal.deal_id) 
        template_title = _(u'Add New Event')
    elif event_id and open_deal_id is None:
        is_edit = True
        event = get_object_or_404(profile.company.event_set.all(), pk=event_id)
        template_title = _(u'Edit Event')
    
    validation_error_ajax = False

    if request.method == 'POST':        
        form = EventForm(request.POST, instance=event, prefix='form')
        if form.is_valid():                        
            event = form.save()   
            log_event(request, event, 'event_add_edit', 'event saved', profile, is_edit)
            events = profile.company.event_set.filter(deal_id = event.deal_id).order_by('due_date_time')[:3]
            #tasks, paginator_t, page_t, page_number_t = makePaginator(request, 3, event_queryset) 
            variables = {'events':events}
            #variables = merge_with_pagination_variables(paginator_t, page_t, page_number_t, variables, 'task_')
            return render(request, 'event_list.html', variables)
        else:
            validation_error_ajax = True
    else:
        form = EventForm(instance=event, prefix='form')
    current_tz = timezone.get_current_timezone();
    user_date = current_tz.normalize(timezone.now().astimezone(current_tz))
    variables = {'form':form, 'template_title':template_title, 'validation_error_ajax':validation_error_ajax, 'user_date':user_date }       
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
        log_event(request, event, 'event_delete', '', profile, False)
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
    current_tz = timezone.get_current_timezone()
    current_date_time = current_tz.normalize(timezone.now().astimezone(current_tz))
    
    today_max = current_date_time.replace(hour=23, minute=59, second=59, microsecond=0)
    today_min = current_date_time.replace(hour=00, minute=00, second=00, microsecond=0)
    today_events = profile.company.event_set.filter(due_date_time__range=(today_min, today_max))
    
    tomorrow_events = profile.company.event_set.filter(due_date_time__range=(today_min + timedelta(days=1), today_max + timedelta(days=1)))
    
    today = current_date_time
    start_week = today - timedelta(today.weekday())
    end_week = start_week + timedelta(6)
    week_max = end_week.replace(hour=23, minute=59, second=59, microsecond=0)
    week_min = start_week.replace(hour=00, minute=00, second=00, microsecond=0)    
    this_week_events = profile.company.event_set.filter(due_date_time__range=(week_min, week_max))        
    this_week_events = this_week_events.exclude(pk__in=[item.pk for item in today_events])
    this_week_events = this_week_events.exclude(pk__in=[item.pk for item in tomorrow_events])
                                 
    start_week_next = start_week + timedelta(7)  
    end_week_next = end_week + timedelta(7)    
    week_max = end_week_next.replace(hour=23, minute=59, second=59, microsecond=0)
    week_min = start_week_next.replace(hour=00, minute=00, second=00, microsecond=0)
    next_week_events = profile.company.event_set.filter(due_date_time__range=(week_min, week_max))
    next_week_events = next_week_events.exclude(pk__in=[item.pk for item in today_events])
    next_week_events = next_week_events.exclude(pk__in=[item.pk for item in tomorrow_events])
    
    variables = {'today_events':today_events, 'tomorrow_events':tomorrow_events, 'this_week_events':this_week_events, 'next_week_events':next_week_events}
    return variables

@login_required
def product_display(request):
    profile = request.user.get_profile()
    products_queryset = profile.company.products_set.order_by('item_name')    
    ajax = False
    
        
    if 'ajax' in request.GET:
        ajax = True        
        if 'item_name' in request.GET:    
            item_name = request.GET['item_name']
            products_queryset = products_queryset.filter(item_name__icontains=item_name).order_by('item_name')

    
    filter_form = FilterProductsForm(request.GET)    
    products, paginator, page, page_number = makePaginator(request, 7, products_queryset)    
    #New Products form for adding a possible new one on UI
    product = Products(company=profile.company)
    form = ProductsForm(instance=product)
    source = 'products/'          
    variables = {
                 'products': products, 'form':form, 'filter_form' : filter_form, 'get_request':get_request_parameters(request), 'source':source
                }   
    variables = merge_with_additional_variables(request, paginator, page, page_number, variables) 
    if ajax:    
        return render(request, 'product_list.html', variables)
    else:        
        return render(request, '_products_table.html', variables)
#        else:
#            return render(request, 'products.html', variables)  

@login_required
def single_product_display(request, product_id):
    profile = request.user.get_profile()    
    product = get_object_or_404(profile.company.products_set.all(), pk=product_id)
    variables = {'products' : [product]}
    return render(request, '_product_rows.html', variables)

@login_required
def deal_template_product_display(request):
    profile = request.user.get_profile()        
    deal = DealTemplate(company=profile.company)
    form = DealTemplateForm(instance=deal)    
    variables = {'form':form }
    return render(request, 'deal_template_product.html', variables)
   

@login_required
def product_add_edit(request, product_id=None):    
    profile = request.user.get_profile()    
    validation_error_ajax = False;
    source = 'products/'  
    secondary = ''
    is_edit = False
    if product_id is None:
        product = Products(company=profile.company, user=request.user)       
        secondary = 'add new product' 
    else:
        product = get_object_or_404(profile.company.products_set.all(), pk=product_id)
        secondary = 'edit product'
        is_edit = True
    if request.method == 'POST':
        form = ProductsForm(request.POST, instance=product)
        if form.is_valid():
            product = form.save()
            log_product(request, product, 'product_add_edit', secondary, profile, is_edit)
            
            if product_id is not None:
                # Only successful Edit (POST) --> rendering only the changed row
                variables = {'products' : [product]}
                return render(request, '_product_rows.html', variables)        
        else:
            validation_error_ajax = True;
            if product_id is None:
                # Only unsuccessful Add (POST) --> rendering only the invalid Add row
                variables = {'form' : form, 'validation_error_ajax' : validation_error_ajax}
                return render(request, 'product_add_save_form.html', variables)
    else:
        form = ProductsForm(instance=product)
    if product_id is None:
        # Only first-time GET Add or Successful Add (POST) --> The List incl. paginators will get updated
        products_queryset = profile.company.products_set.all().order_by('item_name')
        products, paginator, page, page_number = makePaginator(request, 7, products_queryset)        
        variables = {
                     'products': products, 'form':form, 'source':source,
                     'Product_id' : product_id, 'validation_error_ajax' : validation_error_ajax, 'get_request':get_request_parameters(request)
                     }
        variables = merge_with_additional_variables(request, paginator, page, page_number, variables)
        return render(request, 'product_list.html', variables)
    else:
        # Only first-time GET Edit or invalid POST Edit --> Edit Save row will be rendered
        variables = {
                     'form':form, 'Product_id' : product_id, 'validation_error_ajax' : validation_error_ajax, 'source':source 
                    }        
        return render(request, 'product_edit_save_form.html', variables)

@login_required
def product_delete(request, product_id=None):
    source = 'products/'  
    if product_id is None:
        raise Http404(_(u'Product/Service not found'))
    else:
        profile = request.user.get_profile()
        product = get_object_or_404(profile.company.products_set.all(), pk=product_id)
        log_product(request, product, 'product_delete', '', profile, False)
        product.delete()                
        products_queryset = profile.company.products_set.all().order_by('item_name')   
        products, paginator, page, page_number = makePaginator(request, 7, products_queryset)    
        #New Products form for adding a possible new one on UI
        product = Products(company=profile.company)
        form = ProductsForm(instance=product)        
        variables = { 'products': products, 'form':form, 'source':source}
        variables = merge_with_additional_variables(request, paginator, page, page_number, variables)
    return render(request, 'product_list.html', variables)




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
        if 'product' in request.GET:            
            product_keywords = request.GET.getlist('product')
            # Q are queries that can be stacked with Or operators. If none of the Qs contains any value, `reduce` minimizes them to no queryset,             
            q_filters = reduce(operator.or_, (Q(item_name__icontains=item.strip()) for item in product_keywords))
            products = profile.company.products_set.filter(q_filters)       
            deal_templates_queryset = deal_templates_queryset.filter(product__in=products)
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
    secondary = ''
    is_edit = False
    if deal_id is None:
        deal = DealTemplate(company=profile.company, user=request.user)
        template_title = _(u'Add New Deal Template')
        secondary = 'Add New Deal Template'
    else:
        is_edit = True
        deal = get_object_or_404(profile.company.dealtemplate_set.all(), pk=deal_id)
        template_title = _(u'Edit Deal Template')
        secondary = 'Edit Deal Template'
    if request.method == 'POST':
        form = DealTemplateForm(request.POST, instance=deal)
        if form.is_valid():
            deal = form.save()
            log_dealtemplate(request, deal, 'deal_template_add_edit', secondary, profile, is_edit)
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
        log_dealtemplate(request, deal_template, 'deal_template_delete', '', profile, False)
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
                user_location = get_user_location_details(request)
                browser_type = get_user_browser(request)
                userProfile = UserProfile(user=user, company = profile.company, is_cb_superuser=False, license = profile.license, ip=user_location.ip, country=user_location.country, city=user_location.city, timezone=form.cleaned_data['timezone'], browser=browser_type)
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



def product_autocomplete(request):
    if 'query' in request.GET:
        #Get the prerequisite fields for autocomplete
        profile, kwargs, fieldname = get_fields_for_autocomplete(request)
        #filter the related queryset with the prereq fields
        queryset = profile.company.products_set.filter(**kwargs)[:10]
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
        q = all_open_deals(request, profile.company)
        try:        
            queryset = q.filter(**kwargs)[:10]
        except:
            # Foreignkey related fields must folow this pattern
            if fieldname == 'status':
                queryset = q.filter(status__deal_status__icontains=request.GET['query'])[:10]
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
            elif fieldname == 'product':
                #First see which of the company wide generated sales items the user tried to search against
                product = profile.company.products_set.filter(item_name__istartswith=request.GET['query'])
                #Now that we know, let see which of the existing deal_templates have such product(s) we were searching for previously
                deal_templates = profile.company.dealtemplate_set.filter(product__in=product)
                #Create a queryset dictionary to eliminate the double entries
                queryset = {}
                for deal in deal_templates:
                    #Since its M2M, each DealTemplate's product could point to several items itself, hence another loop is required
                    for si in deal.product.select_related():
                        if queryset.has_key(si):
                            continue                        
                        queryset[si]=si
                #Now that we captured all possible products that are used in DealTemplate instances
                #We need to change the fieldname we search against to the name of product's field instead so that the json method after here works. 
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
        return render(request, 'registration/invite_forbidden.html')
    
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
                messages.warning(request, _(u'An invitation was sent to %(name)s.') % {'name' : invitation.email})
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
def sidebar_todo(request):
    return render(request, 'todo_sidebar.html')
    

@login_required
def sidebar_open_deals(request):    
    filter_form = FilterOpenDealForm()
    current_tz = timezone.get_current_timezone()
    user_date = current_tz.normalize(timezone.now().astimezone(current_tz))
    variables = { 'filter_form':filter_form, 'user_date':user_date }
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

@register.inclusion_tag('tag_form_label_div_below_error.html')
def show_row_div_below_error(form_field, *args, **kwargs):
    return {'form_field': form_field }

@register.inclusion_tag('tag_form_label_time_div.html')
def show_row_time_div(form_field, *args, **kwargs):
    ignore_error_text = False
    if 'ignore_error_text' in kwargs:
        ignore_error_text = True
    return {'form_field': form_field, 'ignore_error_text':ignore_error_text}

@register.inclusion_tag('tag_form_label_icon.html')
def show_row_icon(form_field, icon, *args, **kwargs):    
    return {'form_field': form_field, 'icon':icon}

#@login_required

#def _deal_status_view(request, call_id=None):        
#    conversation_deal = Conversation_Deal.objects.filter(conversation_id__in=call_id)    
#    deal_statuses = DealStatus.objects.all()        
#    all = list(Conversation_Deal.objects.filter(conversation_id__in=call_id)) + list(DealStatus.objects.all())
#    
#    to_json =  [ {"deal_pk": 1, "fields": [{"selected": "true", "status": "Pending 0%"}, {"selected": "false", "status": "Pending 25%"} ]}, {"deal_pk": 2, "fields": [{"selected": "false", "status": "Pending 0%"}, {"selected": "true", "status": "Pending 25%"} ]} ]  
#   
#    return HttpResponse(simplejson.dumps(to_json), mimetype='application/json')



