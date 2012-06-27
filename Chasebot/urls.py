from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.views.generic.simple import direct_to_template
from Chasebot import settings
from Chasebot_App.views import main_page_view, logout_page_view, register_page_view, new_contact_view, new_contact_type_view, new_marital_status_view, new_country_view

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
    (r'^contact/add/$', new_contact_view),
    (r'^contact_type/add/$', new_contact_type_view),
    (r'^marital_status/add/$', new_marital_status_view),
    (r'^country/add/$', new_country_view),

    #i18n

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)


# DEBUG
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )