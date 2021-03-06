#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import MySQLdb
dbname = "Ch4seb0tDB"
conn = MySQLdb.connect('localhost', 'django_user', 'houmie123', dbname, charset='utf8')
cur = conn.cursor()

f = open('/home/hooman/venuscloud/chasebot-env/site/database/country_code_drupal_nov_2011.txt')

cur.execute("INSERT INTO chasebot_app_company (company_name, company_email) VALUES ('Venus Cloud Ltd', 'info@venuscloud.com');")
cur.execute("INSERT INTO chasebot_app_currency (currency) VALUES ('USD - $'),('EUR - €'), ('GBP - £'), ('CAD - $'), ('AUD - $'), ('BRL - R$');")
#cur.execute("INSERT INTO chasebot_app_licensetemplate (name, max_users, description, currency_id, price) VALUES ('Solo', '1', 'Solo plan (1 user, 5 GB file storage, max 20,000 contacts)', 1,  '24');")
#cur.execute("INSERT INTO chasebot_app_licensetemplate (name, max_users, description, currency_id, price) VALUES ('Basic', '2', 'Free plan (2 users, no file storage, max 275 contacts)', 1, '0');")
#cur.execute("INSERT INTO chasebot_app_licensetemplate (name, max_users, description, currency_id, price) VALUES ('Standard', '6', 'For small teams (6 users, 6 GB file storage, max 6,000 contacts)', 1, '19');")
#cur.execute("INSERT INTO chasebot_app_licensetemplate (name, max_users, description, currency_id, price) VALUES ('Premium', '15', 'For mid-sized teams (15 users, 15 GB file storage, 15,000 contacts)', 1,  '39');")
#cur.execute("INSERT INTO chasebot_app_licensetemplate (name, max_users, description, currency_id, price) VALUES ('Coorporate', '42', 'For large teams (40 users, 40 GB file storage, 40,0000 contacts)', 1, '89');")
cur.execute("INSERT INTO chasebot_app_licensetemplate (name, max_users, description, currency_id, price) VALUES ('Free', '5', 'Free plan (5 users, 1 GB file storage, unlimited deals, max 1000 contacts)', 1, '0');")
cur.execute("INSERT INTO chasebot_app_licensetemplate (name, max_users, description, currency_id, price) VALUES ('Demo', '5', '30 Days Demo Plan (5 users, 1 GB file storage, unlimited deals, max 1000 contacts)', 1, '0');")

cur.execute("INSERT INTO chasebot_app_userprofile (user_id, company_id, is_cb_superuser, license_id, timezone, browser, is_log_active) VALUES (1, 1, TRUE, 1, 'Europe/London', 'x', TRUE);")

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


cur.execute("ALTER DATABASE `%s` CHARACTER SET 'utf8' COLLATE 'utf8_unicode_ci'" % dbname)

sql = "SELECT DISTINCT(table_name) FROM information_schema.columns WHERE table_schema = '%s'" % dbname
cur.execute(sql)

results = cur.fetchall()
for row in results:
    sql = "ALTER TABLE `%s` convert to character set DEFAULT COLLATE DEFAULT" % (row[0])
    cur.execute(sql)

# Close communication with the database
cur.close()
conn.close()