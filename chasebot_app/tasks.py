from celery import task
from celery.schedules import crontab
from celery.task.base import periodic_task
import datetime
import chasebot_app
import celery
import chasebot_app.models as mdls
from django.utils.timezone import utc

@celery.task(name='tasks.check_for_tasks')
@periodic_task(run_every=datetime.timedelta(minutes=1))  
def check_for_tasks():      
    tasks = mdls.Task.objects.all()
    now = datetime.datetime.utcnow().replace(tzinfo=utc,second=00, microsecond=00)
    for task in tasks:
        if task.reminder_date_time == now:
            print "match"

#@task()
#def add(x, y):
#    return x + y