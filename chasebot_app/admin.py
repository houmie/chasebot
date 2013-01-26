from djcelery.models import TaskMeta
__author__ = 'houman'
from django.contrib import admin
from chasebot_app.models import Company, UserProfile, Contact, MaritalStatus, \
    Conversation, LicenseTemplate, Event

admin.site.register(Contact)
admin.site.register(Company)
admin.site.register(UserProfile)
admin.site.register(MaritalStatus)
#admin.site.register(Country)
admin.site.register(Conversation)
admin.site.register(LicenseTemplate)
#admin.site.register(Task)
admin.site.register(Event)
class TaskMetaAdmin(admin.ModelAdmin):
    readonly_fields = ('result',)    
admin.site.register(TaskMeta, TaskMetaAdmin)