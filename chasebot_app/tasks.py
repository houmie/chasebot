from celery import task
from celery.schedules import crontab
from celery.task.base import periodic_task
import datetime
import chasebot_app
import celery
 
#@celery.task(name='tasks.add')
@periodic_task(run_every=datetime.timedelta(minutes=1))  
def test():      
    print "firing test task" 


#@task()
#def add(x, y):
#    return x + y