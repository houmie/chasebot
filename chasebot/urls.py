from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.views.generic.simple import direct_to_template
from chasebot_app.views import logout_page, contact_delete, conversation_display, \
     conversation_delete, sales_item_add_edit, sales_item_display, sales_item_delete, deal_type_display, deal_type_add_edit, deal_type_delete,\
     charts_display, conversation_add_edit, sales_item_cancel, set_timezone,\
     contacts_display, register_page, contact_add_edit,\
    sales_item_autocomplete, contacts_autocomplete, conversations_autocomplete

admin.autodiscover()

urlpatterns = patterns('',
    
    # Session management
    (r'^login/$', 'django.contrib.auth.views.login'),
    (r'^logout/$', logout_page),
    (r'^change-password/$', 'django.contrib.auth.views.password_change'),
    (r'^password-changed/$', 'django.contrib.auth.views.password_change_done'),
    (r'^password_reset/$','django.contrib.auth.views.password_reset'),
    (r'^password_reset_done/$','django.contrib.auth.views.password_reset_done'),
    (r'^password_reset_confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$','django.contrib.auth.views.password_reset_confirm'),
    (r'^password_reset_complete/$','django.contrib.auth.views.password_reset_complete'),
    (r'^register/$', register_page),
    (r'^register/success/$', direct_to_template, {'template': 'registration/register_success.html'}),

    #Browsing
    (r'^$', contacts_display),
    (r'^contact/delete/(?P<contact_id>\d+)/$', contact_delete),
    (r'^contact/edit/(?P<contact_id>\d+)/$', contact_add_edit),
    (r'^contact/add/', contact_add_edit),
        
    (r'^contact/(?P<contact_id>\d+)/call/edit/(?P<call_id>\w+)/$', conversation_add_edit),
    (r'^contact/(?P<contact_id>\d+)/call/delete/(?P<call_id>\w+)/$', conversation_delete),
    (r'^contact/(?P<contact_id>\d+)/call/add/$', conversation_add_edit),    
    (r'^contact/(?P<contact_id>\d+)/calls/$', conversation_display),

    (r'^sales_item/add/$', sales_item_add_edit),    
    (r'^sales_item/edit/(?P<sales_item_id>\d+)/$', sales_item_add_edit),
    (r'^sales_item/edit/cancel/(?P<sales_item_id>\d+)/$', sales_item_cancel),    
    (r'^sales_items/$', sales_item_display),
    (r'^sales_item/delete/(?P<sales_item_id>\d+)/$', sales_item_delete),
    
    (r'^deal/add/$', deal_type_add_edit),    
    (r'^deal/edit/(?P<deal_id>\d+)/$', deal_type_add_edit),
    (r'^deals/$', deal_type_display),
    (r'^deal/delete/(?P<deal_id>\d+)/$', deal_type_delete),
    
    (r'^charts/contact/(?P<contact_id>\d+)$', charts_display),

    (r'^autocomplete/sales_items/$', sales_item_autocomplete),
    (r'^autocomplete/contacts/$', contacts_autocomplete),
    (r'^autocomplete/conversations/(?P<contact_id>\d+)/$', conversations_autocomplete),        
            
    #i18n
    (r'^i18n/', include('django.conf.urls.i18n')),
    (r'^timezone/', set_timezone),
        
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),    
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns()