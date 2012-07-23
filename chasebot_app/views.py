# Create your views here.
import datetime 
from django.http import Http404, HttpResponse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from chasebot_app.forms import RegistrationForm, ContactsForm, ContactTypeForm, MaritalStatusForm, CountryForm, CallsForm, SalesItemForm, DealForm
from chasebot_app.models import Company, Contact, ContactType, MaritalStatus, Country, Conversation, SalesItem, Deal, DealStatus,\
    Conversation_Deal 
from chasebot_app.models import UserProfile
from django.core import serializers
from django.utils.translation import ugettext as _
from django.template import response
from django.utils import simplejson


@login_required
def main_page_view(request):
    profile = request.user.get_profile()
    company_name = profile.company.company_name
    contacts= profile.company.contact_set.all().order_by('last_name')[:10]    
    vars = {'company_name': company_name, 'contacts' : contacts}
    variables = RequestContext(request, vars)
    return render_to_response('main_page.html', variables)

@login_required
def contact_view(request, contact_id=None):
    profile = request.user.get_profile()
    if contact_id is None:
        contact = Contact(company=profile.company)
        template_title = _(u'Add New Contact')
    else:
        contact = get_object_or_404(profile.company.contact_set.all(), pk=contact_id)
        template_title = _(u'Edit Contact')
    if request.POST:
        form = ContactsForm(profile.company, request.POST, instance=contact)
        if form.is_valid():
            contact = form.save()
            return HttpResponseRedirect('/')
    else:
        form = ContactsForm(instance=contact, company=profile.company)
    variables = RequestContext(request, {'form':form, 'template_title': template_title, 'contact_id' : contact_id})
#    return render_to_response("contact.html", variables)
#    if request.GET.has_key('ajax'):
    #return render_to_response('contact_modal.html', variables)
#   else:
    return render_to_response('contact.html', variables)

@login_required
def delete_contact_view(request, contact_id):
    if contact_id is None:
        raise Http404(_(u'Contact not found'))
    else:
        profile = request.user.get_profile()
        contact = get_object_or_404(profile.company.contact_set.all(), pk=contact_id)
        contact.delete()
    return HttpResponseRedirect('/')


@login_required
def call_display_view(request, contact_id):
    profile = request.user.get_profile()
    contact = get_object_or_404(profile.company.contact_set.all(), pk=contact_id)
    calls = contact.conversation_set.all().order_by('-creation_date')
    variables = RequestContext(request, {'calls': calls, 'contact': contact})
    return render_to_response('calls.html', variables)

@login_required
def call_view(request, contact_id, call_id=None):
    custom_validation_errors = {}
    profile = request.user.get_profile()
    contact = get_object_or_404(profile.company.contact_set.all(), pk=contact_id)
    if call_id is None:
        call = Conversation(company=profile.company, contact=contact, contact_date = datetime.datetime.now(), contact_time = datetime.datetime.now().strftime("%H:%M"))        
        template_title = _(u'Add New Conversation')
    else:
        call = get_object_or_404(contact.conversation_set.all(), pk=call_id)
        template_title = _(u'Edit Conversation')
    if request.POST:
        form = CallsForm(request.POST, instance=call)
        if form.is_valid():            
            
            
            call = form.save(commit=False)
            #call.save()
            
            # Extracts the Deal pk from the twin-id between the two dropdowns
            deal_dic = {}
            for query, value in form.data.items():
                if query.startswith('deal_'):
                    deal_dic[query[5:]] = value
            
            deal_status_updates = {}
            for query, value in form.data.items():
                if query.startswith('dealstatus_'):
                    key = deal_dic[query[11:]]
                    if(key in deal_status_updates):
                        deal = profile.company.deal_set.get(pk=key)
                        custom_validation_errors['deal_' + key] = deal.deal_name + ' has already been selected.'
                    else:
                        deal_status_updates[deal_dic[query[11:]]] = value
#            
#            deals = form.cleaned_data["deals"]
#            for deal in deals:                
#                deal_status = DealStatus.objects.get(pk=deal_status_updates[deal.pk])
#                conversation_deal, id_created = Conversation_Deal.objects.get_or_create(conversation=call, deal=deal)
#                conversation_deal.status=deal_status
#                conversation_deal.save()
            if not custom_validation_errors:                
                return HttpResponseRedirect('/contact/' + contact_id + '/calls/')
    else:
        form = CallsForm(instance=call)
    deal_statuses = DealStatus.objects.all()
    deals = profile.company.deal_set.all()
    conversation_deals = call.deals.through.objects.all()
    variables = RequestContext(request, {'form':form, 'template_title': template_title, 'deal_statuses' : deal_statuses, 'deals' : deals, 'conversation_deals' : conversation_deals, 'custom_validation_errors': custom_validation_errors})
    return render_to_response('conversation.html', variables)

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
    variables = RequestContext(request, {'sales_items': sales_items})
    return render_to_response('sales_items.html', variables)

@login_required
def sales_item_view(request, sales_item_id=None):
    profile = request.user.get_profile()
    if sales_item_id is None:
        sales_item = SalesItem(company=profile.company)
        template_title = _(u'Add a new Sales Item')
    else:
        sales_item = get_object_or_404(profile.company.salesitem_set.all(), pk=sales_item_id)
        template_title = _(u'Edit Sales Item')
    if request.POST:
        form = SalesItemForm(request.POST, instance=sales_item)
        if form.is_valid():
            sales_item = form.save()
            return HttpResponseRedirect('/sales_items')
    else:
        form = SalesItemForm(instance=sales_item)
    variables = RequestContext(request, {'form':form, 'template_title': template_title})
    return render_to_response('sales_item.html', variables)

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
def deal_display_view(request):
    profile = request.user.get_profile()
    deals = profile.company.deal_set.all()
    variables = RequestContext(request, {'deals': deals})
    return render_to_response('deals.html', variables)

@login_required
def deal_view(request, deal_id=None):
    profile = request.user.get_profile()
    if deal_id is None:
        deal = Deal(company=profile.company)
        deal.status = DealStatus.objects.get(id=1)
        template_title = _(u'Add a new deal')
    else:
        deal = get_object_or_404(profile.company.deal_set.all(), pk=deal_id)
        template_title = _(u'Edit deal')
    if request.POST:
        form = DealForm(request.POST, instance=deal)
        if form.is_valid():
            deal = form.save()
            return HttpResponseRedirect('/deals')
    else:
        form = DealForm(instance=deal)
    variables = RequestContext(request, {'form':form, 'template_title': template_title})
    return render_to_response('deal.html', variables)

@login_required
def delete_deal_view(request, deal_id=None):
    if deal_id is None:
        raise Http404(_(u'Deal not found'))
    else:
        profile = request.user.get_profile()
        deal = get_object_or_404(profile.company.deal_set.all(), pk=deal_id)
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
    variables = RequestContext(request, {'form':form})
    return render_to_response('registration/register.html', variables)

@login_required
def _deal_status_view(request, call_id=None):        
    conversation_deal = Conversation_Deal.objects.filter(conversation_id__in=call_id)    
    deal_statuses = DealStatus.objects.all()        
    all = list(Conversation_Deal.objects.filter(conversation_id__in=call_id)) + list(DealStatus.objects.all())
    
    to_json =  [ {"deal_pk": 1, "fields": [{"selected": "true", "status": "Pending 0%"}, {"selected": "false", "status": "Pending 25%"} ]}, {"deal_pk": 2, "fields": [{"selected": "false", "status": "Pending 0%"}, {"selected": "true", "status": "Pending 25%"} ]} ]  
    
    #data = serializers.serialize("json", employees)
    return HttpResponse(simplejson.dumps(to_json), mimetype='application/json')
#dic = {'conversation_deal' : conversation_deal, 'deal_statuses' : deal_statuses}


