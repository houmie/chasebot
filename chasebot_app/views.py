# Create your views here.
import datetime 
from __builtin__ import id
from django.http import Http404
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from chasebot_app.forms import RegistrationForm, ContactsForm, ContactTypeForm, MaritalStatusForm, CountryForm, CallsForm
from chasebot_app.models import Company, Contact, ContactType, MaritalStatus, Country, ConversationHistory
from chasebot_app.models import UserProfile
from django.utils.translation import ugettext as _


@login_required
def main_page_view(request):
    profile = request.user.get_profile()
    company_name = profile.company.company_name
    contacts= profile.company.contact_set.all().order_by('last_name')[:10]    
    vars = {'company_name': company_name, 'contacts' : contacts}
    variables = RequestContext(request, vars)
    return render_to_response('main_page.html', variables)

@login_required
def call_display_view(request, contact_id):
    profile = request.user.get_profile()
    contact = get_object_or_404(profile.company.contact_set.all(), pk=contact_id)
    calls = contact.conversationhistory_set.all().order_by('-creation_date')
    variables = RequestContext(request, {'calls': calls})
    return render_to_response('calls_page.html', variables)

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
def contact_view(request, contact_id=None):
    profile = request.user.get_profile()
    if contact_id is None:
        contact = Contact(company=profile.company)
        template_title = _(u'Add New Contact')
    else:
        contact = get_object_or_404(profile.company.contact_set.all(), pk=contact_id)
        template_title = _(u'Edit Contact')
    if request.POST:
#        if request.POST.get('cancel', None):
#            return HttpResponseRedirect('/')
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
def call_view(request, contact_id, call_id=None):
    profile = request.user.get_profile()
    contact = get_object_or_404(profile.company.contact_set.all(), pk=contact_id)
    if call_id is None:
        call = ConversationHistory(company=profile.company, contact=contact, contact_date = datetime.datetime.now(), contact_time = datetime.datetime.now().strftime("%H:%M"))        
        template_title = _(u'Add New Conversation')
    else:
        call = get_object_or_404(contact.conversationhistory_set.all(), pk=call_id)
        template_title = _(u'Edit Conversation')
    if request.POST:
        form = CallsForm(profile.company, contact, request.POST, instance=call)
        if form.is_valid():
            call = form.save()            
            return HttpResponseRedirect('/contact/' + contact_id + '/calls/')
    else:
        form = CallsForm(instance=call, company=profile.company, contact=contact)
    variables = RequestContext(request, {'form':form})
    return render_to_response('conversation.html', variables)

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
def delete_call_view(request, contact_id, call_id):
    if contact_id is None:
        raise Http404(_(u'Contact not found'))
    elif call_id is None:
        raise Http404(_(u'Conversation not found'))
    else:
        profile = request.user.get_profile()
        contact = get_object_or_404(profile.company.contact_set.all(), pk=contact_id)
        call = get_object_or_404(contact.conversationhistory_set.all(), pk=call_id)
        call.delete()
    return HttpResponseRedirect('/contact/' + contact_id + '/calls/')


@login_required
def contact_type_view(request, contact_type_id=None):
    profile = request.user.get_profile()
    if contact_type_id is None:
        contact_type = ContactType(company=profile.company)
        template_title = _(u'Add Contact Type')
    else:
        contact_type = get_object_or_404(profile.company.contacttype_set.all(), pk=contact_type_id)
        template_title = _(u'Edit Contact Type')

    if request.POST:
        form = ContactTypeForm(request.POST, instance=contact_type)
        if form.is_valid():
            contact_type = form.save()
            return HttpResponseRedirect('/')
    else:
        form = ContactTypeForm(instance=contact_type)
    variables = RequestContext(request, {'form': form, 'template_title': template_title})
    return render_to_response('contact_type.html', variables)

@login_required
def delete_contact_type_view(request, contact_type_id):
    if contact_type_id is None:
        raise Http404(_(u'Contact Type not found'))
    else:
        profile = request.user.get_profile()
        contact_type = get_object_or_404(profile.company.contacttype_set.all(), pk=contact_type_id)
        contact_type.delete()
        return HttpResponseRedirect('/')


