"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test chasebot_app".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from chasebot_app.models import Company, UserProfile, Contact, ContactType,\
    SalesItem, SalesTerm, Conversation, DealTemplate, Deal, DealStatus
import datetime
import uuid
from django.utils.timezone import utc
from django.utils import timezone



#Fixture for creating two company, two users and three contacts
def setup_contacts(self):
        self.user1 = User.objects.create_user(username='username1', password='password1', email='email1@email.com')
        self.company1 = Company.objects.create(company_name='company_name1', company_email='company_email1@email.com')
        UserProfile.objects.create(user=self.user1, company=self.company1)
        self.user2 = User.objects.create_user(username='username2', password='password2', email='email2@email.com')
        self.company2 = Company.objects.create(company_name='company_name2', company_email='company_email2@email.com')
        UserProfile.objects.create(user=self.user2, company=self.company2)        
        ctype = ContactType.objects.create(contact_type="test1")
        self.contact1a = Contact.objects.create(last_name='last_name1a', contact_type=ctype, company=self.company1)
        self.contact1b = Contact.objects.create(last_name='last_name1b', contact_type=ctype, company=self.company1)
        self.contact2  = Contact.objects.create(last_name='last_name2', contact_type=ctype, company=self.company2)        

#Fixture for creating a sales item per user 
def setup_sales_items(self):
        self.sales_item1 = SalesItem.objects.create(item_name = 'item_1',  company = self.company1)
        self.sales_item2 = SalesItem.objects.create(item_name = 'item_2',  company = self.company2)        

#Fixture for creating a deal_template item per company 
def setup_DealTemplate(self):
        self.deal_template1 = DealTemplate.objects.create(company=self.company1, deal_name='deal_name_1', sales_item=self.sales_item1, price=1, sales_term=self.sales_term, quantity=1)
        self.deal_template2 = DealTemplate.objects.create(company=self.company2, deal_name='deal_name_2', sales_item=self.sales_item2, price=2, sales_term=self.sales_term, quantity=2)

#Fixture for creating a deal item per company 
def setup_deal(self):
        self.deal_status = DealStatus.objects.create(deal_status = 'deal_status')
        self.deal1 = Deal.objects.create(deal_id = uuid.uuid1(), status = self.deal_status, contact = self.contact1a, deal_template = self.deal_template1, conversation = self.call1, set = 1)
        self.deal2 = Deal.objects.create(deal_id = uuid.uuid1(), status = self.deal_status, contact = self.contact2, deal_template = self.deal_template2, conversation = self.call21, set = 1)

#Fixture for creating a deal_template item per company 
def setup_sales_term(self):
        self.sales_term = SalesTerm.objects.create(sales_term = 'sales_term1')

#Fixture for creating a three calls for company1's contact1a and 1 call for company2's contact2
def setup_calls(self):
        self.call1 = Conversation.objects.create(contact = self.contact1a, conversation_datetime = timezone.now(), subject = 'subject1a')
        self.call2 = Conversation.objects.create(contact = self.contact1a, conversation_datetime = timezone.now(), subject = 'subject1b')
        self.call3 = Conversation.objects.create(contact = self.contact1a, conversation_datetime = timezone.now(), subject = 'subject1c')
        self.call21 =Conversation.objects.create(contact = self.contact2, conversation_datetime = timezone.now(), subject = 'subject2')

#Testing the ownership of the contacts belonging to a company
class ContactModelTest(TestCase):
    def setUp(self):
        setup_contacts(self)
        
    def test_get_contacts_for_company(self):        
        user1 = User.objects.get(username='username1')
        profile1 = user1.get_profile()        
        contacts = profile1.company.contact_set.order_by('last_name')
        lst = list(contacts)        
        self.assertEqual(len(lst), 2, 'Expected two contacts for this company, but got %s' % len(lst))
        self.assertEqual(lst[0].last_name, 'last_name1a', 'Expected lastname1a, but got %s' % lst[0].last_name)
        self.assertEqual(lst[1].last_name, 'last_name1b', 'Expected lastname1b, but got %s' % lst[1].last_name)
        
#Testing the ownership of the sales items belonging to a company
class SalesItemModelTest(TestCase):
    def setUp(self):
        setup_contacts(self)
        setup_sales_items(self)
        
    def test_get_sales_item_for_company(self):        
        user1 = User.objects.get(username='username1')
        profile1 = user1.get_profile()
        sales_items = profile1.company.salesitem_set.all()   
        lst = list(sales_items)     
        self.assertEqual(len(lst), 1, 'Expected one sales item for this company, but got %s' % len(lst))
        self.assertEqual(lst[0].item_name, 'item_1', 'Expected item_1, but got %s' % lst[0].item_name)
        
        
      
#Testing the ownership of the DealTemplate belonging to a company
class DealTemplateModelTest(TestCase):
    def setUp(self):
        setup_contacts(self)
        setup_sales_items(self)        
        setup_sales_term(self)        
        setup_DealTemplate(self)
        
    def test_get_DealTemplate_for_company(self):
        user1 = User.objects.get(username='username1')
        profile1 = user1.get_profile()
        DealTemplates = profile1.company.dealtemplate_set.all()      
        lst = list(DealTemplates)
        self.assertEqual(len(lst), 1, 'Expected one DealTemplate for this company, but got %s' % len(lst))
        self.assertEqual(lst[0].deal_name, 'deal_name_1', 'Expected deal_name_1, but got %s' % lst[0].deal_name)
        
 
#Testing the ownership of the conversation belonging to a contact
class ConversationModelTest(TestCase):
    def setUp(self):
        setup_contacts(self)                        
        setup_calls(self)
        
    def test_get_conversation(self):
        user1 = User.objects.get(username='username1')
        profile1 = user1.get_profile()
        contact = profile1.company.contact_set.get(last_name = 'last_name1a')
        conversations = contact.conversation_set.order_by('subject')
        lst = list(conversations)        
        self.assertEqual(len(lst), 3, 'Expected three conversations for contact1a, but got %s' % len(lst))
        self.assertEqual(lst[0].subject, 'subject1a', 'Expected subject1a, but got %s' % lst[0].subject)
        self.assertEqual(lst[1].subject, 'subject1b', 'Expected subject1b, but got %s' % lst[1].subject)
        self.assertEqual(lst[2].subject, 'subject1c', 'Expected subject1c, but got %s' % lst[2].subject)
        
        
#Testing the ownership of the Deal belonging to a conversation/contact
class DealModelTest(TestCase):
    def setUp(self):
        setup_contacts(self)
        setup_calls(self)
        setup_sales_items(self)        
        setup_sales_term(self)        
        setup_DealTemplate(self)
        setup_deal(self)
        
        
    def test_get_deal_by_conversation(self):
        user1 = User.objects.get(username='username1')
        profile1 = user1.get_profile()
        contact = profile1.company.contact_set.get(last_name = 'last_name1a')
        conversation = contact.conversation_set.get(subject = 'subject1a')
        deal = conversation.deal_set.all()        
        lst = list(deal)        
        self.assertEqual(len(lst), 1, 'Expected one deal for conversation1 , but got %s' % len(lst))

        
    def test_get_deal_by_contact(self):
        user1 = User.objects.get(username='username1')
        profile1 = user1.get_profile()
        contact = profile1.company.contact_set.get(last_name = 'last_name1a')        
        deal = contact.deal_set.all()        
        lst = list(deal)        
        self.assertEqual(len(lst), 1, 'Expected one deal for conversation1 , but got %s' % len(lst))
        
class TestContact(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='username1', password='password1', email='email1@email.com')
        self.company1 = Company.objects.create(company_name='company_name1', company_email='company_email1@email.com')
        UserProfile.objects.create(user=self.user1, company=self.company1)
    
    def test_contact_view_loads(self):
        self.client.login(username='username1', password='password1')
        response = self.client.get('/contact/add/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contact.html')

    def test_contact_view_fails_blank(self):
        self.client.login(username='username1', password='password1')
        response = self.client.post('/contact/add/', {}) # blank data dictionary
        self.assertFormError(response, 'form', 'last_name', 'This field is required.')
        self.assertFormError(response, 'form', 'contact_type', 'This field is required.')
    
    def test_contact_view_denies_anonymous(self):
        response = self.client.get('/contact/add/', follow=True)
        self.assertRedirects(response, '/login/?next=/contact/add/')
        response = self.client.post('/contact/add/', follow=True)
        self.assertRedirects(response, '/login/?next=/contact/add/')

       
    def test_contact_view_success(self):
        # same again, but with valid data, then
        self.client.login(username='username1', password='password1')
        contact_type = ContactType.objects.create(contact_type='contact_type')
        response = self.client.post('/contact/add/', {u'last_name': [u'Johnson'], u'home_town': [u''], u'postcode': [u''], u'dear_name': [u''], u'contact_notes': [u''], u'city': [u''], u'first_name': [u''], u'work_phone': [u''], u'state': [u''], u'company_name': [u''], u'home_phone': [u''], u'email': [u''], u'children_names': [u''], u'mobile_phone': [u''], u'fax_number': [u''], u'spouses_interests': [u''], u'referred_by': [u''], u'address': [u''], u'prev_meeting_places': [u''], u'spouse_first_name': [u''], u'contact_type': [contact_type.pk], u'gender': [u''], u'marital_status': [u''], u'contacts_interests': [u''], u'country': [u''], u'birth_date': [u''], u'position': [u''], u'company':[u'1']})
        #print response.context['form'].errors 
        self.assertRedirects(response, '/')
