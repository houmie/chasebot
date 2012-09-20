import datetime
from datetime import datetime as dt 
from django.http import Http404, HttpResponse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from chasebot_app.forms import RegistrationForm, ContactsForm, ConversationForm, SalesItemForm, DealTemplateForm,\
     DealCForm, FilterContactsForm, FilterConversationForm, FilterDealsForm, FilterSalesItemForm,\
    DealsAddForm
from chasebot_app.models import Company, Contact, Conversation, SalesItem, DealTemplate, DealStatus, Deal, SalesTerm
from chasebot_app.models import UserProfile
from django.utils.translation import ugettext as _
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

ITEMS_PER_PAGE = 3

def set_timezone(request):
    if request.method == 'POST':
        request.session['django_timezone'] = pytz.timezone(request.POST['timezone'])
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
    
    filter_form = FilterConversationForm(request.GET)
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
def get_deal_template(request, deal_template_id):        
#    if 'query' in request.GET:
    profile = request.user.get_profile()        
    deal_template = profile.company.dealtemplate_set.get(pk=deal_template_id)

#   to_json = []
#   for item in deal_template_queryset:
#       to_json.append(str(getattr(item, fieldname)))
    
    return HttpResponse(toJSON(deal_template), mimetype='application/json')        
                
        


@login_required
def conversation_add_edit(request, contact_id, call_id=None):
    profile = request.user.get_profile()
    contact = get_object_or_404(profile.company.contact_set.all(), pk=contact_id)
    
    if call_id is None:
        call = Conversation(contact=contact, conversation_datetime = timezone.now()) 
    else:
        call = get_object_or_404(contact.conversation_set.all(), pk=call_id)
        
    deals_formset_factory = modelformset_factory(Deal, form=DealCForm, extra=1, can_delete=True, max_num=5)    
    attached_deals_to_call_query = call.deal_set.all()
    
    opendeal_formset_factory = modelformset_factory(Deal, form=DealCForm, extra=0)
    raw = contact.get_open_deals();
    opendeals_formset_query = Deal.objects.filter(id__in=[item.id for item in raw]) 
        
    template_title = _(u'Edit Past Conversation')
    deal_title = _(u'Deals attached to this Conversation')
    is_atleast_one_opendeal_attached = False
    
    
#    new_post = request.POST.copy()
#            deal_types = dict()
#            for k,v in new_post.items():
#                if k.startswith('hidden'):
#                    deal_types[k[7:]]= v
#            for k,v in deal_types.iteritems():
#                new_post[k] = v
#            formset = deal_formset(new_post, queryset=formset_query)
    
    if request.method == 'POST':
        non_attached_opendeal_formset = opendeal_formset_factory(request.POST, prefix='opendeals')
        attached_deals_formset = deals_formset_factory(request.POST, prefix='deals')                
        form = ConversationForm(profile.company, request.POST, instance=call, prefix='form')           
        deals_add_form = DealsAddForm(profile.company, call, request.POST, prefix='deals_add_form')
        if form.is_valid() and attached_deals_formset.is_valid() and non_attached_opendeal_formset.is_valid() and deals_add_form.is_valid():
            # Always localize the entered date by user into his timezone before saving it to database
            call = form.save(commit=False)            
            current_tz = timezone.get_current_timezone()            
            date = form.cleaned_data['conversation_date']
            time = form.cleaned_data['conversation_time']            
            date_time = current_tz.localize(datetime.datetime(date.year, date.month, date.day, time.hour, time.minute))                        
            call.conversation_datetime = date_time
            call.save()
                        
#            # The row number of the five possible deals to add are captured as key, while the value is the actual deal that was selected in that given row. 
#            deal_dic = {}
#            for query, value in form.data.items():
#                if query.startswith('deal_'):
#                    deal_dic[query[5:]] = value
#            
#            #Now it needs to check if the row was really meant to be added (in case the delete button was pressed, before submitting)
#            deals_to_add = []
#            for row, value in form.data.items():
#                if row.startswith('deal_show_row_'):
#                    deals_to_add.append(deal_dic[row[14:]])
#                    
#            if deals_to_add:                
#                for deal_pk in deals_to_add:
#                    deal_template = profile.company.dealtemplate_set.get(pk=deal_pk)
#                    set_dic = contact.deal_set.filter(deal_template_id=deal_template.id).aggregate(Max('set'))
#                    set_val = set_dic.get('set__max', 0)
#                    if not set_val:
#                        set_val = 0                    
#                    Deal.objects.create(deal_id=uuid.uuid1(), status=DealStatus.objects.get(pk=1), contact=call.contact, deal_template=deal_template, conversation=call, set=set_val+1)
#            
            for fm in attached_deals_formset:                
                if fm.has_changed():        
                    deal = fm.save(commit=False)
                    set_dic = contact.deal_set.filter(deal_template_id=deal.deal_template.id).aggregate(Max('set'))
                    set_val = set_dic.get('set__max', 0)
                    if not set_val:
                        set_val = 0                                 
                    deal.contact = contact
                    deal.conversation = call
                    deal.status = DealStatus.objects.get(pk=1) 
                    deal.set=set_val+1                    
                    deal.save()
                    fm.save_m2m()
            
            
                    
            for fm in non_attached_opendeal_formset:                    
                if fm.has_changed() and fm.cleaned_data['attach_deal_conversation']:
                    deal_to_add = fm.save(commit=False)                    
                    Deal.objects.create(deal_id=deal_to_add.deal_id, status=deal_to_add.status, contact=call.contact, deal_template=deal_to_add.deal_template, conversation=call, set=deal_to_add.set)            
                            
            return HttpResponseRedirect('/contact/' + contact_id + '/calls/')        
            
    else:        
        deals_add_form = DealsAddForm(profile.company, call, prefix='deals_add_form')
        form = ConversationForm(profile.company, instance=call, prefix='form')              
        attached_deals_formset = deals_formset_factory(queryset=attached_deals_to_call_query, prefix='deals')                
        exclude_attached_opendeals = []
        for attached_deal in attached_deals_to_call_query:
            for open_deal in opendeals_formset_query:
                if attached_deal.deal_id == open_deal.deal_id:
                    exclude_attached_opendeals.append(open_deal.deal_id)
                    is_atleast_one_opendeal_attached = True        
        non_attached_opendeal_query = opendeals_formset_query.exclude(deal_id__in=exclude_attached_opendeals)
        
        non_attached_opendeal_formset = opendeal_formset_factory(queryset=non_attached_opendeal_query, prefix='opendeals')
    
    variables = {'form':form, 'deals_add_form':deals_add_form, 'attached_deals_formset':attached_deals_formset, 'opendeal_formset':non_attached_opendeal_formset, 'is_atleast_one_opendeal_attached':is_atleast_one_opendeal_attached }
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
        variables = { 'calls': calls, 'contact':contact }
        variables = merge_with_additional_variables(request, paginator, page, page_number, variables)
    return render(request, 'conversation_list.html', variables)


@login_required
def sales_item_display(request):    
    profile = request.user.get_profile()
    sales_items_queryset = profile.company.salesitem_set.order_by('item_name')    
    ajax = False
    is_modal = False 
        
    if 'ajax' in request.GET:
        ajax = True        
        if 'item_name' in request.GET:    
            item_name = request.GET['item_name']
            sales_items_queryset = sales_items_queryset.filter(item_name__icontains=item_name).order_by('item_name')
    if 'modal' in request.GET:
        is_modal = True        
    
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
        if is_modal:
            return render(request, 'sales_items_modal.html', variables)
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
                     'sales_items': sales_items, 'form':form,                     
                     'salesitem_id' : sales_item_id, 'validation_error_ajax' : validation_error_ajax, 'get_request':get_request_parameters(request)
                     }
        variables = merge_with_additional_variables(request, paginator, page, page_number, variables)
        return render(request, 'sales_item_list.html', variables)
    else:
        # Only first-time GET Edit or invalid POST Edit --> Edit Save row will be rendered
        variables = {
                     'form':form, 'salesitem_id' : sales_item_id, 'validation_error_ajax' : validation_error_ajax, 
                    }
        variables = merge_with_localized_variables(request, variables)   
        return render(request, 'sales_item_edit_save_form.html', variables)

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
def deal_template_display(request):    
    profile = request.user.get_profile()
    deals_queryset = profile.company.dealtemplate_set.order_by('deal_name')
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
def deal_template_add_edit(request, deal_id=None):
    profile = request.user.get_profile()
    
    if deal_id is None:
        deal = DealTemplate(company=profile.company)        
        template_title = _(u'Add a new deal')
    else:
        deal = get_object_or_404(profile.company.dealtemplate_set.all(), pk=deal_id)
        template_title = _(u'Edit deal')
    if request.method == 'POST':
        form = DealTemplateForm(request.POST, instance=deal)
        if form.is_valid():
            deal = form.save()
            return HttpResponseRedirect('/deals')
    else:
        form = DealTemplateForm(instance=deal)    
    variables = {'form':form, 'template_title': template_title}
    variables = merge_with_localized_variables(request, variables)   
    return render(request, 'deal.html', variables)

@login_required
def deal_template_delete(request, deal_id=None):
    if deal_id is None:
        raise Http404(_(u'Deal Type not found'))
    else:
        profile = request.user.get_profile()
        deal = get_object_or_404(profile.company.dealtemplate_set.all(), pk=deal_id)
        deal.delete()
        deal_queryset = profile.company.dealtemplate_set.order_by('deal_name')   
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
    stac = {'VEM':0, 'EM':0, 'LM':0, 'EA':0, 'LA':0, 'EE':0, 'LE':0}
    for deal in deals:        
        part = part_of_day_statistics(deal.conversation.conversation_datetime)
        stac[part] += 1    
    variables = {'deals':deals, 'stac':stac, 'contact':contact, }
    variables = merge_with_localized_variables(request, variables)   
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
    get_request = '?ajax'
    for key, value in request.GET.iteritems():
        if key == 'ajax' or key == 'modal':
            continue        
        get_request = get_request + '&' + key + '=' + value
    return get_request


def get_paginator_variables(paginator, page, page_number):
    return { 'show_paginator': paginator.num_pages > 1, 'has_prev': page.has_previous(), 'has_next': page.has_next(), 'page': page_number, 'pages': paginator.num_pages, 'next_page': page_number + 1, 'prev_page': page_number - 1}

def get_localized_variables(request):
    return { 'locale' : get_datepicker_format(request), 'delete_button_confirmation': get_delete_button_confirmation(), 'timezones': pytz.common_timezones}  

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



