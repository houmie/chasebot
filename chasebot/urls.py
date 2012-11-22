from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.views.generic.simple import direct_to_template
from chasebot_app.views import logout_page, contact_delete, conversation_display, \
     conversation_delete, sales_item_add_edit, sales_item_display, sales_item_delete, deal_template_display, deal_template_add_edit, deal_template_delete,\
     charts_display, conversation_add_edit, single_sales_item_display, set_timezone,\
     contacts_display, register_page, contact_add_edit,\
    sales_item_autocomplete, contacts_autocomplete, conversations_autocomplete,\
    deal_autocomplete, get_deal_template, get_opendeal, colleague_invite,\
    colleague_accept, single_conversation_display, \
    task_display, task_add_edit, task_delete
from chasebot_app.demo_view import demo

admin.autodiscover()

js_info_dict = {
     'packages': ('chasebot_app',),
}

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
    (r'^colleague/invite/$', colleague_invite),
    (r'^colleague/accept/(\w+)/$', colleague_accept),
    (r'^demo/$', demo),

    #Browsing
    (r'^$', contacts_display),
    (r'^contact/delete/(?P<contact_id>\d+)/$', contact_delete),
    (r'^contact/edit/(?P<contact_id>\d+)/$', contact_add_edit),
    (r'^contact/add/', contact_add_edit),

    (r'^contact/(?P<contact_id>\d+)/call/edit/(?P<call_id>\w+)/$', conversation_add_edit),
    (r'^contact/(?P<contact_id>\d+)/call/delete/(?P<call_id>\w+)/$', conversation_delete),
    (r'^contact/(?P<contact_id>\d+)/call/add/$', conversation_add_edit),    
    (r'^contact/(?P<contact_id>\d+)/calls/$', conversation_display),
    (r'^contact/(?P<contact_id>\d+)/call/(?P<call_id>\w+)/$', single_conversation_display),
    
    #Ajax
    (r'^deal_template/(?P<deal_template_id>\d+)/$', get_deal_template),
    (r'^open_deal/(?P<deal_id>\d+)/(?P<contact_id>\d+)/$', get_opendeal),
        
    (r'^sales_item/add/$', sales_item_add_edit),    
    (r'^sales_item/edit/(?P<sales_item_id>\d+)/$', sales_item_add_edit),
    (r'^sales_item/(?P<sales_item_id>\d+)/$', single_sales_item_display),    
    (r'^sales_items/$', sales_item_display),
    (r'^sales_item/delete/(?P<sales_item_id>\d+)/$', sales_item_delete),
    
    (r'^deal/add/$', deal_template_add_edit),    
    (r'^deal/edit/(?P<deal_id>\d+)/$', deal_template_add_edit),
    (r'^deals/$', deal_template_display),
    (r'^deal/delete/(?P<deal_id>\d+)/$', deal_template_delete),
    #(r'^opendeals/$', open_deals),
    
    (r'^charts/contact/(?P<contact_id>\d+)$', charts_display),

    (r'^autocomplete/sales_items/$', sales_item_autocomplete),
    (r'^autocomplete/contacts/$', contacts_autocomplete),
    (r'^autocomplete/conversations/(?P<contact_id>\d+)/$', conversations_autocomplete),   
    (r'^autocomplete/deals/$', deal_autocomplete),

    (r'^task/add/$', task_add_edit),    
    (r'^task/edit/(?P<task_id>\d+)/$', task_add_edit),
    (r'^task/(?P<task_id>\d+)/$', task_display),    
    #(r'^tasks/$', task_display),
    (r'^task/delete/(?P<task_id>\d+)/$', task_delete),

    #i18n
    (r'^i18n/', include('django.conf.urls.i18n')),
    (r'^timezone/', set_timezone),
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns()