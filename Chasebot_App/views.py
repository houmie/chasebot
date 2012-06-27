# Create your views here.
from ufw.applications import get_profiles
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from Chasebot_App.forms import RegistrationForm, ContactsForm, ContactTypeForm, MaritalStatusForm, CountryForm
#from Chasebot_App.models import UserProfile
from Chasebot_App.models import Company, Contact, ContactType, MaritalStatus, Country
from Chasebot_App.models import UserProfile

def main_page_view(request):
    if request.user.is_authenticated():
        profile = request.user.get_profile()
        company_name = profile.company.company_name
    else:
        company_name = ''
    company = {'company_name': company_name}
    variables = RequestContext(request, company)
    return render_to_response('main_page.html', variables)

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
def new_contact_view(request):
    if request.method == 'POST':
        form = ContactsForm(request.POST)
        if form.is_valid():
            contact = Contact.objects.create(
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                dear=form.cleaned_data['dear'],
                address=form.cleaned_data['address'],
                city=form.cleaned_data['city'],
                state=form.cleaned_data['state'],
                postcode=form.cleaned_data['postcode'],
                country=form.cleaned_data['country'],
                company_name=form.cleaned_data['company_name'],
                title=form.cleaned_data['title'],
                work_phone=form.cleaned_data['work_phone'],
                home_phone=form.cleaned_data['home_phone'],
                mobile_phone=form.cleaned_data['mobile_phone'],
                fax_number=form.cleaned_data['fax_number'],
                email=form.cleaned_data['email'],
                birth_date=form.cleaned_data['birth_date'],
                prev_meeting_places=form.cleaned_data['prev_meeting_places'],
                contact_type=form.cleaned_data['contact_type'],
                referred_by=form.cleaned_data['referred_by'],
                contact_notes=form.cleaned_data['contact_notes'],
                marital_status=form.cleaned_data['marital_status'],
                contacts_interests=form.cleaned_data['contacts_interests'],
                spouse_first_name=form.cleaned_data['spouse_first_name'],
                spouse_last_name=form.cleaned_data['spouse_last_name'],
                spouses_interests=form.cleaned_data['spouses_interests'],
                children_names=form.cleaned_data['children_names'],
                home_town=form.cleaned_data['home_town']
            )
            contact.save()
            return HttpResponseRedirect('/')
    else:
        form = ContactsForm()
    variables = RequestContext(request, {'form':form})
    return render_to_response('contact_add.html', variables)

@login_required
def new_contact_type_view(request):
    if request.method == 'POST':
        form = ContactTypeForm(request.POST)
        if form.is_valid():
            contact_type = ContactType.objects.create(contact_type = form.cleaned_data['contact_type'])
            contact_type.save()
            return HttpResponseRedirect('/')
    else:
        form = ContactTypeForm()
    variables = RequestContext(request, {'form': form})
    return render_to_response('contact_type_add.html', variables)

@login_required
def new_marital_status_view(request):
    if request.method == 'POST':
        form = MaritalStatusForm(request.POST)
        if form.is_valid():
            marital_status = MaritalStatus.objects.create(martial_status_type = form.cleaned_data['martial_status_type'])
            marital_status.save()
            return HttpResponseRedirect('/')
    else:
        form = MaritalStatusForm()
    variables = RequestContext(request, {'form':form})
    return render_to_response('marital_status_add.html', variables)

@login_required
def new_country_view(request):
    if request.method == 'POST':
        form = CountryForm(request.POST)
        if form.is_valid():
            country = Country.objects.create(
                country_code = form.cleaned_data['country_code'],
                country_name = form.cleaned_data['country_name']
            )
            country.save()
            return HttpResponseRedirect('/')
    else:
        form = CountryForm()
    variables = RequestContext(request, {'form' : form})
    return render_to_response('country_add.html', variables)