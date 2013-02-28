#!/bin/bash

rtpass="houmie123"
dbname="Ch4seb0tDB"

sudo mysql --user=root --password=$rtpass --execute="DROP DATABASE $dbname"
sudo mysql --user=root --password=$rtpass --execute="CREATE DATABASE $dbname"
sudo mysql --user=root --password=$rtpass --execute="GRANT ALL PRIVILEGES ON $dbname.* TO 'root'@'localhost' IDENTIFIED BY '$rtpass'"  
sudo mysql --user=root --password=$rtpass --execute="FLUSH PRIVILEGES"

source ~/venuscloud/chasebot-env/bin/activate

~/venuscloud/chasebot-env/site/manage.py syncdb
~/venuscloud/chasebot-env/site/manage.py migrate djcelery
#~/venuscloud/chasebot-env/site/manage.py migrate chasebot_app
#~/venuscloud/chasebot-env/site/manage.py migrate chasebot_app 0001 --fake
#~/venuscloud/chasebot-env/site/manage.py migrate chasebot_app
#~/venuscloud/chasebot-env/site/manage.py schemamigration chasebot_app --auto
#~/venuscloud/chasebot-env/site/manage.py migrate chasebot_app
~/venuscloud/chasebot-env/bin/python database/mysql_startup_data.py 


