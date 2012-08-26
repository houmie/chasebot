# Create your views here.
import datetime 
from django.http import Http404, HttpResponse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404, render
from django.template.context import RequestContext
from chasebot_app.forms import RegistrationForm, ContactsForm, ContactTypeForm, MaritalStatusForm, CountryForm, CallsForm, SalesItemForm, DealTypeForm,\
    DealForm, BaseDealFormSet, DealCForm
from chasebot_app.models import Company, Contact, ContactType, MaritalStatus, Country, Conversation, SalesItem, DealType, DealStatus, Deal,\
    UserProfile
from chasebot_app.models import UserProfile
from django.core import serializers
from django.utils.translation import ugettext as _
from django.template import response
from django.utils import simplejson
from django.forms.models import modelformset_factory
import uuid
from django.forms.formsets import formset_factory
from django.db.models.aggregates import Max
import time
from django.utils.translation import activate


def display_current_language(request):
    if request.LANGUAGE_CODE == 'en-gb':
        lang = "British English"        
    elif request.LANGUAGE_CODE == 'en':        
        lang = "American English"           
    return lang

@login_required
def main_page_view(request):
    lang = display_current_language(request)
    delete_button_confirmation = get_delete_button_confirmation()
    profile = request.user.get_profile()
    company_name = profile.company.company_name
    contacts= profile.company.contact_set.all().order_by('last_name')[:10]    
    variables = {'company_name': company_name, 'contacts' : contacts, 'locale' : get_datepicker_format(request), 'lang': lang, 'delete_button_confirmation': delete_button_confirmation}    
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
    return HttpResponseRedirect('/')


@login_required
def call_display_view(request, contact_id):
    profile = request.user.get_profile()
    contact = get_object_or_404(profile.company.contact_set.all(), pk=contact_id)
    calls = contact.conversation_set.all().order_by('-time_stamp')
    lang = display_current_language(request)
    variables = {'calls': calls, 'contact': contact, 'locale' : get_datepicker_format(request), 'lang':lang}
    return render(request, 'calls.html', variables)


@login_required
def call_view(request, contact_id, call_id=None):
    profile = request.user.get_profile()
    contact = get_object_or_404(profile.company.contact_set.all(), pk=contact_id)
    
    if call_id is None:
        call = Conversation(contact=contact, contact_date = datetime.date.today(), contact_time = datetime.datetime.now().time())
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
            call = form.save()            
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
    variables = {'form':form, 'attached_deals_formset':attached_deals_formset, 'opendeal_formset':non_attached_opendeal_formset, 'is_atleast_one_opendeal_attached':is_atleast_one_opendeal_attached, 'locale' : get_datepicker_format(request), 'lang':lang}
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
    profile = request.user.get_profile()
    sales_items = profile.company.salesitem_set.all()
    lang = display_current_language(request)
    
    sales_item = SalesItem(company=profile.company)
    form = SalesItemForm(instance=sales_item)
    delete_button_confirmation = get_delete_button_confirmation()
    variables = {'sales_items': sales_items, 'locale' : get_datepicker_format(request), 'lang': lang, 'form':form, 'delete_button_confirmation' : delete_button_confirmation}
    return render(request, 'sales_items.html', variables)

@login_required
def sales_item_cancel_view(request, sales_item_id):
    profile = request.user.get_profile()    
    sales_item = get_object_or_404(profile.company.salesitem_set.all(), pk=sales_item_id)
    variables = {'sales_items' : [sales_item]}
    return render(request, 'sales_item_list.html', variables)


@login_required
def sales_item_view(request, sales_item_id=None):
    profile = request.user.get_profile()
    lang = display_current_language(request)
    validation_error_ajax = False;
    if sales_item_id is None:
        sales_item = SalesItem(company=profile.company)
        template_title = _(u'Add a new Sales Item')
    else:
        sales_item = get_object_or_404(profile.company.salesitem_set.all(), pk=sales_item_id)
        template_title = _(u'Edit Sales Item')
    if request.method == 'POST':
        #list_post = list(request.POST)
        #if 'submit-button' in list_post:        
        form = SalesItemForm(request.POST, instance=sales_item)
        if form.is_valid():
            sales_item = form.save()            
            variables = {'sales_items' : [sales_item]}
            return render(request, 'sales_item_list.html', variables)
        else:
            validation_error_ajax = True;                
#        else:
#            sales_item = profile.company.salesitem_set.get(pk=sales_item_id)
#            variables = {'sales_items' : [sales_item]}
#            return render(request, 'sales_item_list.html', variables)            
    else:
        form = SalesItemForm(instance=sales_item)
    variables = {'form':form, 'template_title': template_title, 'locale' : get_datepicker_format(request), 'lang': lang, 'salesitem_id' : sales_item_id, 'validation_error_ajax' : validation_error_ajax}
    if sales_item_id is None:
        return render(request, 'sales_item_add_save_form.html', variables)
    else:
        return render(request, 'sales_item_save_form.html', variables)

@login_required
def delete_sales_item_view(request, sales_item_id=None):
    if sales_item_id is None:
        raise Http404(_(u'Sales item not found'))
    else:
        profile = request.user.get_profile()
        sales_item = get_object_or_404(profile.company.salesitem_set.all(), pk=sales_item_id)
        sales_item.delete()
    return HttpResponseRedirect('/sales_items')



@login_required
def deal_template_display_view(request):
    profile = request.user.get_profile()
    deals = profile.company.dealtype_set.all()
    lang = display_current_language(request)
    delete_button_confirmation = get_delete_button_confirmation()
    variables = {'deals': deals, 'lang': lang, 'delete_button_confirmation' : delete_button_confirmation}
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
        part = part_of_day_statistics(deal.conversation.contact_time)
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



  

#@login_required
#def _deal_status_view(request, call_id=None):        
#    conversation_deal = Conversation_Deal.objects.filter(conversation_id__in=call_id)    
#    deal_statuses = DealStatus.objects.all()        
#    all = list(Conversation_Deal.objects.filter(conversation_id__in=call_id)) + list(DealStatus.objects.all())
#    
#    to_json =  [ {"deal_pk": 1, "fields": [{"selected": "true", "status": "Pending 0%"}, {"selected": "false", "status": "Pending 25%"} ]}, {"deal_pk": 2, "fields": [{"selected": "false", "status": "Pending 0%"}, {"selected": "true", "status": "Pending 25%"} ]} ]  
#   
#    return HttpResponse(simplejson.dumps(to_json), mimetype='application/json')



