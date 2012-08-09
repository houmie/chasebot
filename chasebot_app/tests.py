"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from chasebot_app.models import Company, UserProfile, Contact, ContactType


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)



#To test the data visibility of a contact model belonging to a single company1
class ContactModelTest(TestCase):
    def setUp(self):
        user1 = User.objects.create_user(username='username1', password='password1', email='email1@email.com')
        company1 = Company.objects.create(company_name='company_name1', company_email = 'company_email1@email.com')
        userProfile1 = UserProfile(user=user1, company = company1)
        userProfile1.save()
        
        user2 = User.objects.create_user(username='username2', password='password2', email='email2@email.com')
        company2 = Company.objects.create(company_name='company_name2', company_email = 'company_email2@email.com')
        userProfile2 = UserProfile(user=user2, company = company2)
        userProfile2.save()


        ctype = ContactType.objects.create(contact_type= "test1")
                
        Contact.objects.create(last_name='last_name1', contact_type=ctype, company=company1)               
        Contact.objects.create(last_name='last_name2', contact_type=ctype, company=company2)
        
    def test_get_contacts_user1(self):
        
        user1 = User.objects.get(username='username1')
        profile1 = user1.get_profile()        
        contacts = profile1.company.contact_set.all()
        
        self.assertEqual(contacts.count(), 1, 'Expected one contact for this company, but got more')
        self.assertEqual(contacts[0].last_name, 'last_name1')