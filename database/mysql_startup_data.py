#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import MySQLdb

conn = MySQLdb.connect('localhost', 'django_user', 'houmie123', 'Ch4seb0tDB', charset='utf8')
cur = conn.cursor()

f = open('/home/hooman/venuscloud/chasebot-env/site/database/country_code_drupal_nov_2011.txt')

cur.execute("INSERT INTO chasebot_app_company (company_name, company_email) VALUES ('Venus Cloud Ltd', 'info@venuscloud.com');")
cur.execute("INSERT INTO chasebot_app_currency (currency) VALUES ('USD - $'),('EUR - €'), ('GBP - £'), ('CAD - $'), ('AUD - $'), ('BRL - R$');")
cur.execute("INSERT INTO chasebot_app_licensetemplate (name, max_users, description, currency_id, price) VALUES ('Solo', '1', 'Solo plan (1 user, 5 GB file storage, max 20,000 contacts)', 1,  '24');")
cur.execute("INSERT INTO chasebot_app_licensetemplate (name, max_users, description, currency_id, price) VALUES ('Basic', '2', 'Free plan (2 users, no file storage, max 275 contacts)', 1, '0');")
cur.execute("INSERT INTO chasebot_app_licensetemplate (name, max_users, description, currency_id, price) VALUES ('Standard', '6', 'For small teams (6 users, 6 GB file storage, max 6,000 contacts)', 1, '19');")
cur.execute("INSERT INTO chasebot_app_licensetemplate (name, max_users, description, currency_id, price) VALUES ('Premium', '15', 'For mid-sized teams (15 users, 15 GB file storage, 15,000 contacts)', 1,  '39');")
cur.execute("INSERT INTO chasebot_app_licensetemplate (name, max_users, description, currency_id, price) VALUES ('Coorporate', '42', 'For large teams (40 users, 40 GB file storage, 40,0000 contacts)', 1, '89');")

cur.execute("INSERT INTO chasebot_app_userprofile (user_id, company_id, is_cb_superuser, license_id) VALUES (1, 1, TRUE, 3);")

#cur.execute("INSERT INTO chasebot_app_gender (gender) VALUES ('Female'),('Male');")

cur.execute("INSERT INTO chasebot_app_maritalstatus (martial_status_type) VALUES ('Single'),('Married'),('Domestic partnership'),('Civil Union'),('Divorced'),('Widowed');")

cur.execute("INSERT INTO chasebot_app_dealstatus (deal_status) VALUES ('Pending 0%'),('Pending 25%'),('Pending 50%'),('Pending 75%'),('Won'), ('Lost');")

cur.execute("INSERT INTO chasebot_app_salesterm (sales_term) VALUES ('Fixed bid'),('Per hour'),('Per month'), ('Per year');")

#for line in f:
#    cur.execute("INSERT INTO chasebot_app_country (country_code, country_name) VALUES (%s, %s)", (line[:2] , line[3:-1]))                
#        
#f.close()

# Make the changes to the database persistent
conn.commit()

# Close communication with the database
cur.close()
conn.close()