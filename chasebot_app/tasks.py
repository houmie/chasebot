from celery import task
from celery.schedules import crontab
from celery.task.base import periodic_task
import datetime
import chasebot_app
import celery
import chasebot_app.models as mdls
from django.utils.timezone import utc
from chasebot_app.models import Event

@celery.task(name='tasks.check_for_events')
@periodic_task(run_every=datetime.timedelta(minutes=5))  
def check_for_events():    
    print "Starting"    
    now = datetime.datetime.utcnow().replace(tzinfo=utc,second=00, microsecond=00)
    events = Event.objects.filter(reminder_date_time__range=(now - datetime.timedelta(minutes=5), now))
    for event in events:        
        print "match"
        event.sendMail()
    print "Ending"

#@task()
#def add(x, y):
#    return x + y