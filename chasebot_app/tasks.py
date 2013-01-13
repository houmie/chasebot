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
@periodic_task(run_every=datetime.timedelta(minutes=15))  
def check_for_events():    
    events = Event.objects.all()
    now = datetime.datetime.utcnow().replace(tzinfo=utc,second=00, microsecond=00)
    for event in events:
        if event.reminder_date_time.replace(tzinfo=utc,second=00, microsecond=00) == now:
            print "match"
            event.sendMail()

#@task()
#def add(x, y):
#    return x + y