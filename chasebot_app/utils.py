from django.contrib.gis.geoip import GeoIP
from collections import namedtuple

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_user_location_details(request):
    g = GeoIP()
    ip=get_client_ip(request)
    country = ''
    city = ''
    
    if ip:
        try:
            country = g.city(ip)['country_name']
            city = g.city(ip)['city']
            if not country: 
                country = g.country(ip)['country_name']
        except TypeError:
            pass
    
    Result = namedtuple("result", ["city", "country", "ip"])
    return Result(city=city, country=country, ip=ip)
    

def get_user_browser(request):
    browser_type = ''
    if 'HTTP_USER_AGENT' in request.META:
        browser_type = request.META['HTTP_USER_AGENT']
    return browser_type