from celery import task
from celery.schedules import crontab
from celery.task.base import periodic_task
 

@periodic_task(run_every=crontab(hour="*", minute="*", day_of_week="*"))  
def test():      
    print "firing test task" 


@task()
def add(x, y):
    return x + y