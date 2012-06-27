__author__ = 'houman'
from django.contrib import admin
from Chasebot_App.models import Company, UserProfile, Contact, MaritalStatus, ContactType, Country

admin.site.register(Contact)
admin.site.register(Company)
admin.site.register(UserProfile)
admin.site.register(MaritalStatus)
admin.site.register(Country)
admin.site.register(ContactType)
