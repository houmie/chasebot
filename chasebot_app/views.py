# Create your views here.
import datetime
from itertools import chain
from datetime import datetime as dt 
from django.http import Http404, HttpResponse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404, render
from django.template.context import RequestContext
from chasebot_app.forms import RegistrationForm, ContactsForm, ContactTypeForm, MaritalStatusForm, CountryForm, CallsForm, SalesItemForm, DealTypeForm,\
    DealForm, BaseDealFormSet, DealCForm, FilterContactsForm, FilterCallsForm,\
    FilterDealsForm, FilterSalesItemForm
from chasebot_app.models import Company, Contact, ContactType, MaritalStatus, Country, Conversation, SalesItem, DealType, DealStatus, Deal,\
    UserProfile, SalesTerm
from chasebot_app.models import UserProfile
from django.core import serializers
from django.utils.translation import ugettext as _
from django.template import response
from django.utils import simplejson, timezone
from django.forms.models import modelformset_factory
import uuid
from django.forms.formsets import formset_factory
from django.db.models.aggregates import Max
import time
from django.utils.translation import activate
from django.core.paginator import Paginator, InvalidPage
from django.utils.timezone import utc
import pytz
from django.shortcuts import redirect, render
from chasebot.formats.en import formats as formats_en
from chasebot.formats.en_GB import formats as formats_en_GB
import operator
from django.db.models.query_utils import Q

def set_timezone(request):
    if request.method == 'POST':
        request.session['django_timezone'] = pytz.timezone(request.POST['timezone'])
        return redirect(request.path)
    else:
        return redirect('/')

def display_current_language(request):
    if request.LANGUAGE_CODE == 'en-gb':
        lang = "British English"        
    elif request.LANGUAGE_CODE == 'en':        
        lang = "American English"           
    return lang

def get_current_format(request):
    if request.LANGUAGE_CODE == 'en-gb':
        return formats_en_GB.DATE_INPUT_FORMATS[0]
    elif request.LANGUAGE_CODE == 'en':        
        return formats_en.DATE_INPUT_FORMATS[0]

def create_date_from_javascript_date(request, date, to_date_format = None):
    current_tz = timezone.get_current_timezone()    
    date_time_unaware = dt.strptime(date, get_current_format(request))
    if to_date_format:    
        date_time_unaware = date_time_unaware.replace(hour=23, minute=59, second=59)
    date_time = current_tz.localize(date_time_unaware)            
    return date_time

@login_required
def main_page_view(request):    
    ITEMS_PER_PAGE = 3
    lang = display_current_language(request)
    delete_button_confirmation = get_delete_button_confirmation()
    profile = request.user.get_profile()
    company_name = profile.company.company_name
    contacts_queryset = profile.company.contact_set.all().order_by('last_name')    
    ajax = False
    
    if 'ajax' in request.GET:
        ajax = True
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
    
    filter_form = FilterContactsForm(request.GET)
    contacts, paginator, page, page_number = makePaginator(request, ITEMS_PER_PAGE, contacts_queryset)    
    variables = {
                 'company_name': company_name, 'contacts' : contacts, 'locale' : get_datepicker_format(request), 'lang': lang, 'delete_button_confirmation': delete_button_confirmation,
                 'show_paginator': paginator.num_pages > 1, 'has_prev': page.has_previous(), 'has_next': page.has_next(), 'page': page_number, 'pages': paginator.num_pages,
                 'next_page': page_number + 1, 'prev_page': page_number - 1, 'filter_form' : filter_form, 'timezones': pytz.common_timezones
                 }
    if ajax:    
        return render(request, 'contacts_list.html', variables)
    else:
        return render(request, 'main_page.html', variables)        

@login_required
def contact_view(request, contact_id=None):    
    profile = request.user.get_profile()
    if contact_id is None:
        contact = Contact(company=profile.company)
        template_title = _(u'Add New Contact')
    else:
        contact = get_object_or_404(profile.company.contact_set.all(), pk=contact_id)
        template_title = _(u'Edit Contact')
    if request.method == 'POST':
        form = ContactsForm(profile.company, request.POST, instance=contact)
        if form.is_valid():
            contact = form.save()
            return HttpResponseRedirect('/')
    else:
        form = ContactsForm(instance=contact, company=profile.company)    
    lang = display_current_language(request)
    variables = {'form':form, 'template_title': template_title, 'contact_id' : contact_id, 'locale' : get_datepicker_format(request), 'lang':lang}
    return render(request, 'contact.html', variables)

@login_required
def delete_contact_view(request, contact_id):
    if contact_id is None:
        raise Http404(_(u'Customer not found'))
    else:
        profile = request.user.get_profile()
        contact = get_object_or_404(profile.company.contact_set.all(), pk=contact_id)
        contact.delete()
        ITEMS_PER_PAGE = 3
        contacts_queryset = profile.company.contact_set.all().order_by('last_name')
        contacts, paginator, page, page_number = makePaginator(request, ITEMS_PER_PAGE, contacts_queryset)    
        variables = {                 
                 'contacts': contacts, 'show_paginator': paginator.num_pages > 1, 'has_prev': page.has_previous(), 'has_next': page.has_next(), 'page': page_number, 'pages': paginator.num_pages,
                 'next_page': page_number + 1, 'prev_page': page_number - 1
                 }
    return render(request, 'contacts_list.html', variables)     


@login_required
def call_display_view(request, contact_id):
    ITEMS_PER_PAGE = 10
    profile = request.user.get_profile()
    contact = get_object_or_404(profile.company.contact_set.all(), pk=contact_id)
    calls_queryset = contact.conversation_set.all().order_by('-time_stamp')            
    lang = display_current_language(request)    
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
        if 'subject' in request.GET:    
            subject = request.GET['subject']
            calls_queryset = calls_queryset.filter(subject__icontains=subject).order_by('subject')        
    
    filter_form = FilterCallsForm(request.GET)
    calls, paginator, page, page_number = makePaginator(request, ITEMS_PER_PAGE, calls_queryset)    
    variables = {
                 'calls': calls, 'contact': contact, 'locale' : get_datepicker_format(request), 'lang':lang,
                 'show_paginator': paginator.num_pages > 1, 'has_prev': page.has_previous(), 'has_next': page.has_next(), 'page': page_number, 'pages': paginator.num_pages,
                 'next_page': page_number + 1, 'prev_page': page_number - 1, 'filter_form' : filter_form, 'timezones': pytz.common_timezones
                 }
    if ajax:    
        return render(request, 'calls_list.html', variables)
    else:
        return render(request, 'calls.html', variables)  
    


@login_required
def call_view(request, contact_id, call_id=None):
    profile = request.user.get_profile()
    contact = get_object_or_404(profile.company.contact_set.all(), pk=contact_id)
    
    if call_id is None:
        call = Conversation(contact=contact, conversation_datetime = timezone.now()) 
    else:
        call = get_object_or_404(contact.conversation_set.all(), pk=call_id)
        
    deals_formset_factory = modelformset_factory(Deal, form=DealCForm, extra=0)    
    attached_deals_to_call_query = call.deal_set.all()
    
    opendeal_formset_factory = modelformset_factory(Deal, form=DealCForm, extra=0)    
    raw = contact.get_open_deals();
    opendeals_formset_query = Deal.objects.filter(id__in=[item.id for item in raw]) 
        
    template_title = _(u'Edit Past Conversation')
    deal_title = _(u'Deals attached to this Conversation')
    is_atleast_one_opendeal_attached = False
    
    if request.method == 'POST':
        non_attached_opendeal_formset = opendeal_formset_factory(request.POST, prefix='opendeals')
        attached_deals_formset = deals_formset_factory(request.POST, prefix='deals')                
        form = CallsForm(profile.company, request.POST, instance=call)           
        if form.is_valid() and attached_deals_formset.is_valid() and non_attached_opendeal_formset.is_valid():
            # Always localize the entered date by user into his timezone before saving it to database
            call = form.save(commit=False)            
            current_tz = timezone.get_current_timezone()            
            date = form.cleaned_data['conversation_date']
            time = form.cleaned_data['conversation_time']            
            date_time = current_tz.localize(datetime.datetime(date.year, date.month, date.day, time.hour, time.minute))                        
            call.conversation_datetime = date_time
            call.save()
                        
            # The row number of the five possible deals to add are captured as key, while the value is the actual deal that was selected in that given row. 
            deal_dic = {}
            for query, value in form.data.items():
                if query.startswith('deal_'):
                    deal_dic[query[5:]] = value
            
            #Now it needs to check if the row was really meant to be added (in case the delete button was pressed, before submitting)
            deals_to_add = []
            for row, value in form.data.items():
                if row.startswith('deal_show_row_'):
                    deals_to_add.append(deal_dic[row[14:]])
                    
            if deals_to_add:                
                for deal_pk in deals_to_add:
                    deal_type = profile.company.dealtype_set.get(pk=deal_pk)
                    set_dic = contact.deal_set.filter(deal_type_id=deal_type.id).aggregate(Max('set'))
                    set_val = set_dic.get('set__max', 0)
                    if not set_val:
                        set_val = 0                    
                    Deal.objects.create(deal_id=uuid.uuid1(), status=DealStatus.objects.get(pk=1), contact=call.contact, deal_type=deal_type, conversation=call, set=set_val+1)
            
            
            for fm in attached_deals_formset:
                #if len(fm.changed_data) > 0:
                if fm.has_changed(): 
                    fm.save()
                    
            for fm in non_attached_opendeal_formset:                    
                if fm.has_changed() and fm.cleaned_data['attach_deal_conversation']:
                    deal_to_add = fm.save(commit=False)                    
                    Deal.objects.create(deal_id=deal_to_add.deal_id, status=deal_to_add.status, contact=call.contact, deal_type=deal_to_add.deal_type, conversation=call, set=deal_to_add.set)            
                            
            return HttpResponseRedirect('/contact/' + contact_id + '/calls/')        
            
    else:        
        form = CallsForm(profile.company, instance=call)              
        attached_deals_formset = deals_formset_factory(queryset=attached_deals_to_call_query, prefix='deals')        
        exclude_attached_opendeals = []
        for attached_deal in attached_deals_to_call_query:
            for open_deal in opendeals_formset_query:
                if attached_deal.deal_id == open_deal.deal_id:
                    exclude_attached_opendeals.append(open_deal.deal_id)
                    is_atleast_one_opendeal_attached = True        
        exclude_attached_opendeals_query = opendeals_formset_query.exclude(deal_id__in=exclude_attached_opendeals)
        
        non_attached_opendeal_formset = opendeal_formset_factory(queryset=exclude_attached_opendeals_query, prefix='opendeals')
                            
    lang = display_current_language(request)
    variables = {'form':form, 'attached_deals_formset':attached_deals_formset, 'opendeal_formset':non_attached_opendeal_formset, 'is_atleast_one_opendeal_attached':is_atleast_one_opendeal_attached, 'locale' : get_datepicker_format(request), 'lang':lang, 'timezones': pytz.common_timezones}
    return render(request, 'conversation.html', variables)





@login_required
def delete_call_view(request, contact_id, call_id):
    if contact_id is None:
        raise Http404(_(u'Contact not found'))
    elif call_id is None:
        raise Http404(_(u'Conversation not found'))
    else:
        profile = request.user.get_profile()
        contact = get_object_or_404(profile.company.contact_set.all(), pk=contact_id)
        call = get_object_or_404(contact.conversation_set.all(), pk=call_id)
        call.delete()
    return HttpResponseRedirect('/contact/' + contact_id + '/calls/')


@login_required
def sales_item_display_view(request):
    ITEMS_PER_PAGE = 3
    profile = request.user.get_profile()
    sales_items_queryset = profile.company.salesitem_set.order_by('item_description')            
    lang = display_current_language(request)    
    ajax = False
    
    if 'ajax' in request.GET:
        ajax = True        
        if 'item_description' in request.GET:    
            item_description = request.GET['item_description']
            sales_items_queryset = sales_items_queryset.filter(item_description__icontains=item_description).order_by('item_description')        
    
    filter_form = FilterSalesItemForm(request.GET)    
    sales_items, paginator, page, page_number = makePaginator(request, ITEMS_PER_PAGE, sales_items_queryset)    
    #New SalesItem form for adding a possible new one on UI
    sales_item = SalesItem(company=profile.company)
    form = SalesItemForm(instance=sales_item)
    delete_button_confirmation = get_delete_button_confirmation()
    
    get_request = get_request_parameters(request)
      
    variables = {
                 'sales_items': sales_items, 'locale' : get_datepicker_format(request), 'lang': lang, 'form':form, 'delete_button_confirmation' : delete_button_confirmation,
                 'show_paginator': paginator.num_pages > 1, 'has_prev': page.has_previous(), 'has_next': page.has_next(), 'page': page_number, 'pages': paginator.num_pages,
                 'next_page': page_number + 1, 'prev_page': page_number - 1, 'filter_form' : filter_form, 'timezones': pytz.common_timezones, 'get_request':get_request
                 }    
    if ajax:    
        return render(request, 'sales_item_list.html', variables)
    else:
        return render(request, 'sales_items.html', variables)  

@login_required
def sales_item_cancel_view(request, sales_item_id):
    profile = request.user.get_profile()    
    sales_item = get_object_or_404(profile.company.salesitem_set.all(), pk=sales_item_id)
    variables = {'sales_items' : [sales_item]}
    return render(request, '_sales_item_rows.html', variables)


@login_required
def sales_item_view(request, sales_item_id=None):
    ITEMS_PER_PAGE = 3
    profile = request.user.get_profile()
    #lang = display_current_language(request)
    validation_error_ajax = False;
    if sales_item_id is None:
        sales_item = SalesItem(company=profile.company)        
    else:
        sales_item = get_object_or_404(profile.company.salesitem_set.all(), pk=sales_item_id)        
    if request.method == 'POST':                
        form = SalesItemForm(request.POST, instance=sales_item)
        if form.is_valid():
            sales_item = form.save()
            if sales_item_id is not None:
                variables = {'sales_items' : [sales_item]}
                return render(request, '_sales_item_rows.html', variables)        
        else:
            validation_error_ajax = True;
    else:
        form = SalesItemForm(instance=sales_item)
    if sales_item_id is None:
        sales_items_queryset = profile.company.salesitem_set.all().order_by('item_description')
        sales_items, paginator, page, page_number = makePaginator(request, ITEMS_PER_PAGE, sales_items_queryset)
        delete_button_confirmation = get_delete_button_confirmation()
        variables = {
                     'sales_items': sales_items, 'locale' : get_datepicker_format(request), 'form':form, 'delete_button_confirmation' : delete_button_confirmation,
                     'show_paginator': paginator.num_pages > 1, 'has_prev': page.has_previous(), 'has_next': page.has_next(), 'page': page_number, 'pages': paginator.num_pages,
                     'next_page': page_number + 1, 'prev_page': page_number - 1, 'salesitem_id' : sales_item_id, 'validation_error_ajax' : validation_error_ajax, 'get_request':get_request_parameters(request)
                     }
        return render(request, 'sales_item_list.html', variables)
    else:
        variables = {
                     'locale' : get_datepicker_format(request), 'form':form,                     
                     'salesitem_id' : sales_item_id, 'validation_error_ajax' : validation_error_ajax, 
                    }
        return render(request, 'sales_item_save_form.html', variables)

@login_required
def delete_sales_item_view(request, sales_item_id=None):
    if sales_item_id is None:
        raise Http404(_(u'Sales item not found'))
    else:
        profile = request.user.get_profile()
        sales_item = get_object_or_404(profile.company.salesitem_set.all(), pk=sales_item_id)
        sales_item.delete()
        ITEMS_PER_PAGE = 3        
        sales_items_queryset = profile.company.salesitem_set.all().order_by('item_description')   
        sales_items, paginator, page, page_number = makePaginator(request, ITEMS_PER_PAGE, sales_items_queryset)    
        #New SalesItem form for adding a possible new one on UI
        sales_item = SalesItem(company=profile.company)
        form = SalesItemForm(instance=sales_item)
        delete_button_confirmation = get_delete_button_confirmation()
        variables = {
                 'sales_items': sales_items, 'locale' : get_datepicker_format(request), 'form':form, 'delete_button_confirmation' : delete_button_confirmation,
                 'show_paginator': paginator.num_pages > 1, 'has_prev': page.has_previous(), 'has_next': page.has_next(), 'page': page_number, 'pages': paginator.num_pages,
                 'next_page': page_number + 1, 'prev_page': page_number - 1
                 }    
    return render(request, 'sales_item_list.html', variables)


@login_required
def deal_template_display_view(request):
    ITEMS_PER_PAGE = 10
    profile = request.user.get_profile()
    deals_queryset = profile.company.dealtype_set.all()
    ajax = False
    if 'ajax' in request.GET:
        ajax = True        
        if 'deal_name' in request.GET:    
            deal_name = request.GET['deal_name']
            deals_queryset = deals_queryset.filter(deal_name__icontains=deal_name).order_by('deal_name')
        if 'sales_item' in request.GET:    
            #sales_item_raw = request.GET['sales_item']
            #sales_item_keywords = sales_item_raw.split(',')
            sales_item_keywords = request.GET.getlist('sales_item')
            # Q are queries that can be stacked with Or operators. If none of the Qs contains any value, `reduce` minimizes them to no queryset,             
            q_filters = reduce(operator.or_, (Q(item_description__icontains=item.strip()) for item in sales_item_keywords))
            sales_items = profile.company.salesitem_set.filter(q_filters)       
            deals_queryset = deals_queryset.filter(sales_item__in=sales_items)
        if 'price' in request.GET:    
            price = request.GET['price']
            deals_queryset = deals_queryset.filter(price__icontains=price).order_by('price')
        if 'sales_term' in request.GET:    
            sales_term = request.GET['sales_term']
            sales_terms = SalesTerm.objects.filter(sales_term__icontains=sales_term)
            deals_queryset = deals_queryset.filter(sales_term__in=sales_terms)
        if 'quantity' in request.GET:    
            quantity = request.GET['quantity']
            deals_queryset = deals_queryset.filter(quantity__icontains=quantity).order_by('quantity')    

    filter_form = FilterDealsForm(profile.company, request.GET)            
    deals, paginator, page, page_number = makePaginator(request, ITEMS_PER_PAGE, deals_queryset)    
    lang = display_current_language(request)
    delete_button_confirmation = get_delete_button_confirmation()
    variables = {
                 'deals': deals, 'lang': lang, 'delete_button_confirmation' : delete_button_confirmation,
                 'show_paginator': paginator.num_pages > 1, 'has_prev': page.has_previous(), 'has_next': page.has_next(), 'page': page_number, 'pages': paginator.num_pages,
                 'next_page': page_number + 1, 'prev_page': page_number - 1,'filter_form' : filter_form, 'timezones': pytz.common_timezones                 
                 }
    if ajax:    
        return render(request, 'deals_list.html', variables)
    else:
        return render(request, 'deals.html', variables)
    

@login_required
def deal_template_view(request, deal_id=None):
    profile = request.user.get_profile()
    
    if deal_id is None:
        deal = DealType(company=profile.company)        
        template_title = _(u'Add a new deal')
    else:
        deal = get_object_or_404(profile.company.dealtype_set.all(), pk=deal_id)
        template_title = _(u'Edit deal')
    if request.method == 'POST':
        form = DealTypeForm(request.POST, instance=deal)
        if form.is_valid():
            deal = form.save()
            return HttpResponseRedirect('/deals')
    else:
        form = DealTypeForm(instance=deal)
    lang = display_current_language(request)
    variables = {'form':form, 'template_title': template_title, 'chosen' : _(u'No results matched'), 'locale' : get_datepicker_format(request), 'lang': lang}
    return render(request, 'deal.html', variables)

@login_required
def delete_template_deal_view(request, deal_id=None):
    if deal_id is None:
        raise Http404(_(u'Deal not found'))
    else:
        profile = request.user.get_profile()
        deal = get_object_or_404(profile.company.dealtype_set.all(), pk=deal_id)
        deal.delete()
    return HttpResponseRedirect('/deals')


def logout_page_view(request):
    logout(request)
    return HttpResponseRedirect('/')

def register_page_view(request):    
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            usr = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password2'],
                email=form.cleaned_data['email']
            )
            usr.save()

            company = Company.objects.create()
            company.company_name = form.cleaned_data['company_name']
            company.company_email = form.cleaned_data['company_email']
            company.save()

            userProfile = UserProfile(user=usr, company = company)
            userProfile.save()

#            userProfile = usr.get_profile()
#            userProfile.company = company
#            userProfile.save()


            #usr.UserProfile.company.company_name=form.cleaned_data['company_name']
            #usr.save()

#            if 'invitation' in request.session:
#                # Retrieve the invitation object.
#                invitation = Invitation.objects.get(id=request.session['invitation'])
#                # Create friendship from user to sender.
#                friendship = Friendship(from_friend=user, to_friend=invitation.sender)
#                friendship.save()
#                # Create friendship from sender to user.
#                friendship = Friendship (from_friend=invitation.sender, to_friend=user)
#                friendship.save()
#                # Delete the invitation from the database and session.
#                invitation.delete()
#                del request.session['invitation']
            return HttpResponseRedirect('/register/success/')
    else:
        form = RegistrationForm()
    lang = display_current_language(request)
    variables = {'form':form, 'locale' : get_datepicker_format(request), 'lang':lang}
    return render(request, 'registration/register.html', variables)

@login_required
def charts_view(request, contact_id):
    profile = request.user.get_profile()
    contact = get_object_or_404(profile.company.contact_set.all(), pk=contact_id)
    deals = contact.deal_set.all().order_by('deal_id', 'time_stamp')
    stac = {'EM':0, 'LM':0, 'EA':0, 'LA':0, 'EE':0}
    for deal in deals:        
        part = part_of_day_statistics(deal.conversation.conversation_datetime)
        stac[part] += 1                 
    lang = display_current_language(request)
    variables = {'deals':deals, 'stac':stac, 'contact':contact, 'locale' : get_datepicker_format(request), 'lang':lang}
    return render(request, 'charts.html', variables)
    

def part_of_day_statistics(x):
    if x.hour > 6 and x.hour < 9:
        return 'EM'
    if x.hour >= 9 and x.hour < 12:
        return 'LM'
    if x.hour >= 12 and x.hour < 15:
        return 'EA'
    if x.hour >= 15 and x.hour < 18:
        return 'LA'
    if x.hour >= 18 and x.hour < 21:
        return 'EE'

def get_datepicker_format(request):
    if request.LANGUAGE_CODE == 'en':
        locale = 'mm/dd/yyyy'
    else:
        locale = 'dd/mm/yyyy'
    return locale

    
def get_delete_button_confirmation():
    return _(u'Are you sure you want to delete this row?')

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
    get_request = ''
    for key, value in request.GET.iteritems():
        if key == 'ajax':
            get_request = '?ajax'
            continue
        get_request = get_request + '&' + key + '=' + value
    return get_request
  

#@login_required
#def _deal_status_view(request, call_id=None):        
#    conversation_deal = Conversation_Deal.objects.filter(conversation_id__in=call_id)    
#    deal_statuses = DealStatus.objects.all()        
#    all = list(Conversation_Deal.objects.filter(conversation_id__in=call_id)) + list(DealStatus.objects.all())
#    
#    to_json =  [ {"deal_pk": 1, "fields": [{"selected": "true", "status": "Pending 0%"}, {"selected": "false", "status": "Pending 25%"} ]}, {"deal_pk": 2, "fields": [{"selected": "false", "status": "Pending 0%"}, {"selected": "true", "status": "Pending 25%"} ]} ]  
#   
#    return HttpResponse(simplejson.dumps(to_json), mimetype='application/json')



