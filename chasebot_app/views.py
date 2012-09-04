import datetime
from datetime import datetime as dt 
from django.http import Http404
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from chasebot_app.forms import RegistrationForm, ContactsForm, ConversationForm, SalesItemForm, DealTypeForm,\
     DealCForm, FilterContactsForm, FilterCallsForm, FilterDealsForm, FilterSalesItemForm
from chasebot_app.models import Company, Contact, Conversation, SalesItem, DealType, DealStatus, Deal, SalesTerm
from chasebot_app.models import UserProfile
from django.utils.translation import ugettext as _
from django.utils import timezone
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

ITEMS_PER_PAGE = 3

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

@login_required
def contacts_display(request):      
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
                 'company_name': company_name, 'contacts' : contacts, 'filter_form' : filter_form, 
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
        form = ContactsForm(profile.company, request.POST, instance=contact)
        if form.is_valid():
            contact = form.save()
            return HttpResponseRedirect('/')
    else:
        form = ContactsForm(instance=contact, company=profile.company)    
    variables = {'form':form, 'template_title': template_title, 'contact_id' : contact_id, }
    variables = merge_with_localized_variables(request, variables)
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
        variables = merge_with_pagination_variables(paginator, page, page_number, variables)
    return render(request, 'contact_list.html', variables)     


@login_required
def conversation_display(request, contact_id):    
    profile = request.user.get_profile()
    contact = get_object_or_404(profile.company.contact_set.all(), pk=contact_id)
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
        if 'subject' in request.GET:    
            subject = request.GET['subject']
            calls_queryset = calls_queryset.filter(subject__icontains=subject).order_by('subject')        
    
    filter_form = FilterCallsForm(request.GET)
    calls, paginator, page, page_number = makePaginator(request, ITEMS_PER_PAGE, calls_queryset)    
    variables = {
                 'calls': calls, 'contact': contact, 'filter_form' : filter_form,
                 }
    variables = merge_with_additional_variables(request, paginator, page, page_number, variables)
    if ajax:    
        return render(request, 'conversation_list.html', variables)
    else:
        return render(request, 'conversations.html', variables)  
    


@login_required
def conversation_add_edit(request, contact_id, call_id=None):
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
        form = ConversationForm(profile.company, request.POST, instance=call)           
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
                if fm.has_changed(): 
                    fm.save()
                    
            for fm in non_attached_opendeal_formset:                    
                if fm.has_changed() and fm.cleaned_data['attach_deal_conversation']:
                    deal_to_add = fm.save(commit=False)                    
                    Deal.objects.create(deal_id=deal_to_add.deal_id, status=deal_to_add.status, contact=call.contact, deal_type=deal_to_add.deal_type, conversation=call, set=deal_to_add.set)            
                            
            return HttpResponseRedirect('/contact/' + contact_id + '/calls/')        
            
    else:        
        form = ConversationForm(profile.company, instance=call)              
        attached_deals_formset = deals_formset_factory(queryset=attached_deals_to_call_query, prefix='deals')        
        exclude_attached_opendeals = []
        for attached_deal in attached_deals_to_call_query:
            for open_deal in opendeals_formset_query:
                if attached_deal.deal_id == open_deal.deal_id:
                    exclude_attached_opendeals.append(open_deal.deal_id)
                    is_atleast_one_opendeal_attached = True        
        exclude_attached_opendeals_query = opendeals_formset_query.exclude(deal_id__in=exclude_attached_opendeals)
        
        non_attached_opendeal_formset = opendeal_formset_factory(queryset=exclude_attached_opendeals_query, prefix='opendeals')
    
    variables = {'form':form, 'attached_deals_formset':attached_deals_formset, 'opendeal_formset':non_attached_opendeal_formset, 'is_atleast_one_opendeal_attached':is_atleast_one_opendeal_attached }
    variables = merge_with_localized_variables(request, variables)   
    return render(request, 'conversation.html', variables)





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
        variables = { 'calls': calls, }
        variables = merge_with_additional_variables(request, paginator, page, page_number, variables)
    return render(request, 'conversation_list.html', variables)


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
    variables = {
                 'sales_items': sales_items, 'form':form, 'filter_form' : filter_form, 'get_request':get_request_parameters(request)
                }   
    variables = merge_with_additional_variables(request, paginator, page, page_number, variables) 
    if ajax:    
        return render(request, 'sales_item_list.html', variables)
    else:
        return render(request, 'sales_items.html', variables)  

@login_required
def sales_item_cancel(request, sales_item_id):
    profile = request.user.get_profile()    
    sales_item = get_object_or_404(profile.company.salesitem_set.all(), pk=sales_item_id)
    variables = {'sales_items' : [sales_item]}
    return render(request, '_sales_item_rows.html', variables)


@login_required
def sales_item_add_edit(request, sales_item_id=None):    
    profile = request.user.get_profile()    
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
        sales_items_queryset = profile.company.salesitem_set.all().order_by('item_name')
        sales_items, paginator, page, page_number = makePaginator(request, ITEMS_PER_PAGE, sales_items_queryset)        
        variables = {
                     'sales_items': sales_items, 'form':form,                     
                     'salesitem_id' : sales_item_id, 'validation_error_ajax' : validation_error_ajax, 'get_request':get_request_parameters(request)
                     }
        variables = merge_with_additional_variables(request, paginator, page, page_number, variables)
        return render(request, 'sales_item_list.html', variables)
    else:
        variables = {
                     'form':form, 'salesitem_id' : sales_item_id, 'validation_error_ajax' : validation_error_ajax, 
                    }
        variables = merge_with_localized_variables(request, variables)   
        return render(request, 'sales_item_save_form.html', variables)

@login_required
def sales_item_delete(request, sales_item_id=None):
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
        variables = { 'sales_items': sales_items, 'form':form, }
        variables = merge_with_additional_variables(request, paginator, page, page_number, variables)
    return render(request, 'sales_item_list.html', variables)



@login_required
def deal_type_display(request):    
    profile = request.user.get_profile()
    deals_queryset = profile.company.dealtype_set.order_by('deal_name')
    ajax = False
    if 'ajax' in request.GET:
        ajax = True        
        if 'deal_name' in request.GET:    
            deal_name = request.GET['deal_name']
            deals_queryset = deals_queryset.filter(deal_name__icontains=deal_name).order_by('deal_name')
        if 'sales_item' in request.GET:            
            sales_item_keywords = request.GET.getlist('sales_item')
            # Q are queries that can be stacked with Or operators. If none of the Qs contains any value, `reduce` minimizes them to no queryset,             
            q_filters = reduce(operator.or_, (Q(item_name__icontains=item.strip()) for item in sales_item_keywords))
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
    variables = {
                 'deals': deals, 'filter_form' : filter_form,
                 }
    variables = merge_with_additional_variables(request, paginator, page, page_number, variables)
    if ajax:    
        return render(request, 'deal_list.html', variables)
    else:
        return render(request, 'deals.html', variables)
    

@login_required
def deal_type_add_edit(request, deal_id=None):
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
    variables = {'form':form, 'template_title': template_title}
    variables = merge_with_localized_variables(request, variables)   
    return render(request, 'deal.html', variables)

@login_required
def deal_type_delete(request, deal_id=None):
    if deal_id is None:
        raise Http404(_(u'Deal Type not found'))
    else:
        profile = request.user.get_profile()
        deal = get_object_or_404(profile.company.dealtype_set.all(), pk=deal_id)
        deal.delete()
        deal_queryset = profile.company.dealtype_set.order_by('deal_name')   
        deals, paginator, page, page_number = makePaginator(request, ITEMS_PER_PAGE, deal_queryset)          
        variables = { 'deals': deals, }
        variables = merge_with_additional_variables(request, paginator, page, page_number, variables)
    return render(request, 'deal_list.html', variables)
    

@login_required
def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/')

def register_page(request):    
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
    variables = {'form':form,}
    variables = merge_with_localized_variables(request, variables)   
    return render(request, 'registration/register.html', variables)

@login_required
def charts_display(request, contact_id):
    profile = request.user.get_profile()
    contact = get_object_or_404(profile.company.contact_set.all(), pk=contact_id)
    deals = contact.deal_set.all().order_by('deal_id', 'time_stamp')
    stac = {'EM':0, 'LM':0, 'EA':0, 'LA':0, 'EE':0}
    for deal in deals:        
        part = part_of_day_statistics(deal.conversation.conversation_datetime)
        stac[part] += 1    
    variables = {'deals':deals, 'stac':stac, 'contact':contact, }
    variables = merge_with_localized_variables(request, variables)   
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


def get_paginator_variables(paginator, page, page_number):
    return { 'show_paginator': paginator.num_pages > 1, 'has_prev': page.has_previous(), 'has_next': page.has_next(), 'page': page_number, 'pages': paginator.num_pages, 'next_page': page_number + 1, 'prev_page': page_number - 1}

def get_localized_variables(request):
    return { 'locale' : get_datepicker_format(request), 'lang': display_current_language(request), 'delete_button_confirmation': get_delete_button_confirmation(), 'timezones': pytz.common_timezones, 'chosen' : _(u'No results matched') }  

def merge_with_additional_variables(request, paginator, page, page_number, variables):
    variables = dict(variables.items() + get_paginator_variables(paginator, page, page_number).items() + get_localized_variables(request).items())
    return variables

def merge_with_localized_variables(request, variables):
    variables = dict(variables.items() + get_localized_variables(request).items())
    return variables

def merge_with_pagination_variables(paginator, page, page_number, variables):
    variables = dict(variables.items() + get_paginator_variables(paginator, page, page_number).items())
    return variables



#@login_required
#def _deal_status_view(request, call_id=None):        
#    conversation_deal = Conversation_Deal.objects.filter(conversation_id__in=call_id)    
#    deal_statuses = DealStatus.objects.all()        
#    all = list(Conversation_Deal.objects.filter(conversation_id__in=call_id)) + list(DealStatus.objects.all())
#    
#    to_json =  [ {"deal_pk": 1, "fields": [{"selected": "true", "status": "Pending 0%"}, {"selected": "false", "status": "Pending 25%"} ]}, {"deal_pk": 2, "fields": [{"selected": "false", "status": "Pending 0%"}, {"selected": "true", "status": "Pending 25%"} ]} ]  
#   
#    return HttpResponse(simplejson.dumps(to_json), mimetype='application/json')



