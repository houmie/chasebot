from celery.task.base import periodic_task
from datetime import datetime
from datetime import timedelta
import celery
from django.utils.timezone import utc
from chasebot_app.models import Event, Deal
from django.template.loader import get_template
from django.template.context import Context
from chasebot import settings
from django.core.mail import send_mail
import json
import pytz
import dateutil
from django.utils import timezone


@celery.task(name='tasks.check_for_events')
@periodic_task(run_every=timedelta(minutes=1))  
def check_for_events():    
    now = datetime.utcnow().replace(tzinfo=utc,second=00, microsecond=00)
    events = Event.objects.filter(is_reminder_sent = False).filter(reminder_date_time__range=(now - timedelta(minutes=1), now))    
    dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime) else None    
    for event in events:        
        print "Executing Task"
        time_zone = event.user.get_profile().timezone        
        timezone.activate(pytz.timezone(time_zone))
        current_tz = timezone.get_current_timezone()                
        utc_dt = datetime(event.due_date_time.year, event.due_date_time.month, event.due_date_time.day, event.due_date_time.hour, event.due_date_time.minute, 0, tzinfo=utc)
        loc_dt = current_tz.normalize(utc_dt.astimezone(current_tz))                                          
        sendEmail.delay(event.pk, event.deal_id, event.user.first_name, event.user.email, event.type, json.dumps(loc_dt, default=dthandler), event.notes)    

    


@celery.task(name='tasks.sendEmail')
def sendEmail(event_id, deal_id, first_name, email, event_type, due_date_time, notes):       
    duedatetime_clean = dateutil.parser.parse(json.loads(due_date_time))
    subject = 'Event Reminder'
    link = None
    deal = Deal.objects.filter(deal_id = deal_id)[0]
    contact_name = u'{0} {1}'.format(deal.contact.first_name, deal.contact.last_name)
    template = get_template('reminder_email.txt')
    context = Context({'name': first_name, 'link': link, 'contact': contact_name, 'deal':deal.deal_instance_name, 'communication_type':event_type, 'due_date_time':duedatetime_clean, 'notes':notes})
    message = template.render(context)
    
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

    event = Event.objects.get(pk = event_id)
    event.is_reminder_sent = True
    event.save()
