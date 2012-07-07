__author__ = 'houman'
from django.contrib import admin
from chasebot_app.models import Company, UserProfile, Contact, MaritalStatus, ContactType, Country, Gender

admin.site.register(Contact)
admin.site.register(Company)
admin.site.register(UserProfile)
admin.site.register(MaritalStatus)
admin.site.register(Country)
admin.site.register(ContactType)
admin.site.register(Gender)
