"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test chasebot_app".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from chasebot_app.models import Company, UserProfile, Contact, ContactType,\
    SalesItem, SalesTerm, Conversation, DealType
import datetime



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
        self.sales_item1 = SalesItem.objects.create(item_description = 'item_1',  company = self.company1)
        self.sales_item2 = SalesItem.objects.create(item_description = 'item_2',  company = self.company2)        

#Fixture for creating a deal_type item per company 
def setup_dealtype(self):
        DealType.objects.create(company=self.company1, deal_name='deal_name_1', sales_item=self.sales_item1, price=1, sales_term=self.sales_term, quantity=1)
        DealType.objects.create(company=self.company2, deal_name='deal_name_2', sales_item=self.sales_item2, price=2, sales_term=self.sales_term, quantity=2)

#Fixture for creating a deal_type item per company 
def setup_sales_term(self):
        self.sales_term = SalesTerm.objects.create(sales_term = 'sales_term1')

#Fixture for creating a three calls for company1's contact1a and 1 call for company2's contact2
def setup_calls(self):
        Conversation.objects.create(contact = self.contact1a, contact_date = datetime.datetime.now(), contact_time = datetime.datetime.now().strftime("%H:%M"), subject = 'subject1a', company = self.company1)
        Conversation.objects.create(contact = self.contact1a, contact_date = datetime.datetime.now(), contact_time = datetime.datetime.now().strftime("%H:%M"), subject = 'subject1b', company = self.company1)
        Conversation.objects.create(contact = self.contact1a, contact_date = datetime.datetime.now(), contact_time = datetime.datetime.now().strftime("%H:%M"), subject = 'subject1c', company = self.company1)
        Conversation.objects.create(contact = self.contact2, contact_date = datetime.datetime.now(), contact_time = datetime.datetime.now().strftime("%H:%M"), subject = 'subject2', company = self.company2)





#Testing the ownership of the contacts belonging to a company
class ContactModelTest(TestCase):
    def setUp(self):
        setup_contacts(self)
        
    def test_get_contacts_for_company(self):        
        user1 = User.objects.get(username='username1')
        profile1 = user1.get_profile()        
        contacts = profile1.company.contact_set.all()
        lst = list(contacts)        
        self.assertEqual(len(lst), 2, 'Expected two contacts for this company, but got %s' % len(lst))
        self.assertEqual(lst[0].last_name, 'last_name1b', 'Expected lastname1b, but got %s' % lst[0].last_name)
        self.assertEqual(lst[1].last_name, 'last_name1a', 'Expected lastname1a, but got %s' % lst[1].last_name)
        
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
        self.assertEqual(lst[0].item_description, 'item_1', 'Expected item_1, but got %s' % lst[0].item_description)
        
        
      
#Testing the ownership of the DealType belonging to a company
class DealTypeModelTest(TestCase):
    def setUp(self):
        setup_contacts(self)
        setup_sales_items(self)        
        setup_sales_term(self)        
        setup_dealtype(self)
        
    def test_get_dealtype_for_company(self):
        user1 = User.objects.get(username='username1')
        profile1 = user1.get_profile()
        dealTypes = profile1.company.dealtype_set.all()      
        lst = list(dealTypes)
        self.assertEqual(len(lst), 1, 'Expected one dealType for this company, but got %s' % len(lst))
        self.assertEqual(lst[0].deal_name, 'deal_name_1', 'Expected deal_name_1, but got %s' % lst[0].deal_name)
        
 
#Testing the ownership of the conversationbelonging to a company
class ConversationModelTest(TestCase):
    def setUp(self):
        setup_contacts(self)                        
        setup_calls(self)
        
    def test_get_conversation(self):
        user1 = User.objects.get(username='username1')
        profile1 = user1.get_profile()
        conversations = profile1.company.conversation_set.all()
        lst = list(conversations)        
        self.assertEqual(len(lst), 3, 'Expected three conversations for this company, but got %s' % len(lst))
        self.assertEqual(lst[0].subject, 'subject1a', 'Expected subject1a, but got %s' % lst[0].subject)
        self.assertEqual(lst[1].subject, 'subject1b', 'Expected subject1b, but got %s' % lst[1].subject)
        self.assertEqual(lst[2].subject, 'subject1c', 'Expected subject1c, but got %s' % lst[2].subject)
        
        
        