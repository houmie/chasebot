from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.views.generic.simple import direct_to_template
from chasebot import settings
from chasebot_app.views import main_page_view, logout_page_view, register_page_view, contact_view, delete_contact_view, call_display_view, \
     delete_call_view, sales_item_view, sales_item_display_view, delete_sales_item_view, deal_template_display_view, deal_template_view, delete_template_deal_view,\
    charts_view, call_view

admin.autodiscover()

urlpatterns = patterns('',
    
    # Session management
    (r'^login/$', 'django.contrib.auth.views.login'),
    (r'^logout/$', logout_page_view),
    (r'^change-password/$', 'django.contrib.auth.views.password_change'),
    (r'^password-changed/$', 'django.contrib.auth.views.password_change_done'),
    (r'^password_reset/$','django.contrib.auth.views.password_reset'),
    (r'^password_reset_done/$','django.contrib.auth.views.password_reset_done'),
    (r'^password_reset_confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$','django.contrib.auth.views.password_reset_confirm'),
    (r'^password_reset_complete/$','django.contrib.auth.views.password_reset_complete'),
    (r'^register/$', register_page_view),
    (r'^register/success/$', direct_to_template, {'template': 'registration/register_success.html'}),

    #Browsing
    (r'^$', main_page_view),
    (r'^contact/delete/(?P<contact_id>\d+)/$', delete_contact_view),
    (r'^contact/edit/(?P<contact_id>\d+)/$', contact_view),
    (r'^contact/add/', contact_view),
        
    (r'^contact/(?P<contact_id>\d+)/call/edit/(?P<call_id>\w+)/$', call_view),
    (r'^contact/(?P<contact_id>\d+)/call/delete/(?P<call_id>\w+)/$', delete_call_view),
    (r'^contact/(?P<contact_id>\d+)/call/add/$', call_view),    
    (r'^contact/(?P<contact_id>\d+)/calls/$', call_display_view),

    (r'^sales_item/add/$', sales_item_view),    
    (r'^sales_item/edit/(?P<sales_item_id>\d+)/$', sales_item_view),
    (r'^sales_items/$', sales_item_display_view),
    (r'^sales_item/delete/(?P<sales_item_id>\d+)/$', delete_sales_item_view),
    
    (r'^deal/add/$', deal_template_view),    
    (r'^deal/edit/(?P<deal_id>\d+)/$', deal_template_view),
    (r'^deals/$', deal_template_display_view),
    (r'^deal/delete/(?P<deal_id>\d+)/$', delete_template_deal_view),
    
    (r'^charts/contact/(?P<contact_id>\d+)$', charts_view),
    
    #(r'^deal_status/(?P<deal_id>\d+(,\d+)*)/$', _deal_status_view),
#    (r'^deal_status/(?P<call_id>\d+)/$', _deal_status_view),
    
    #i18n
    (r'^i18n/', include('django.conf.urls.i18n')),
    
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns()