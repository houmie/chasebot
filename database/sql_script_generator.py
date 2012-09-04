import psycopg2

conn = psycopg2.connect("dbname=Ch4s3b0tDB user=django_user password=houmie123")
cur = conn.cursor()

f = open('/home/houman/projects/chasebot/database/country_code_drupal_nov_2011.txt')
#out = open('/home/houman/Projects/Chasebot/database/chasebot_script.sql', "w")


cur.execute("INSERT INTO chasebot_app_company (company_name, company_email) VALUES ('Venus Cloud Ltd', 'info@venuscloud.com');")
cur.execute("INSERT INTO chasebot_app_company (company_name, company_email) VALUES ('Your Company Ltd', 'info@venuscloud.com');")
cur.execute("INSERT INTO chasebot_app_userprofile (user_id, company_id) VALUES (1, 1);")

cur.execute("INSERT INTO chasebot_app_contacttype (contact_type) VALUES ('Supplier'),('Customer');")
cur.execute("INSERT INTO chasebot_app_gender (gender) VALUES ('Female'),('Male');")
cur.execute("INSERT INTO chasebot_app_maritalstatus (martial_status_type) VALUES ('Single'),('Married'),('Domestic partnership'),('Civil Union'),('Divorced'),('Widowed');")

cur.execute("INSERT INTO chasebot_app_dealstatus (deal_status) VALUES ('Pending 0%'),('Pending 25%'),('Pending 50%'),('Pending 75%'),('Won'), ('Lost');")
cur.execute("INSERT INTO chasebot_app_salesitem (item_name, company_id) VALUES ('Coffee', 2);")
cur.execute("INSERT INTO chasebot_app_salesitem (item_name, company_id) VALUES ('Tea', 2);")
cur.execute("INSERT INTO chasebot_app_salesitem (item_name, company_id) VALUES ('Sandwich', 2);")
cur.execute("INSERT INTO chasebot_app_salesitem (item_name, company_id) VALUES ('Fruit Bowl', 2);")
cur.execute("INSERT INTO chasebot_app_salesitem (item_name, company_id) VALUES ('Cake', 2);")
cur.execute("INSERT INTO chasebot_app_salesitem (item_name, company_id) VALUES ('Soft Drink', 2);")
cur.execute("INSERT INTO chasebot_app_salesitem (item_name, company_id) VALUES ('Chips', 2);")

cur.execute("INSERT INTO chasebot_app_salesterm (sales_term) VALUES ('Fixed bid'),('Per hour'),('Per month'), ('Per year');")

for line in f:
    cur.execute("INSERT INTO chasebot_app_country (country_code, country_name) VALUES (%s, %s)", (line[:2] , line[3:-1]))                
        
f.close()
#out.close()

# Make the changes to the database persistent
conn.commit()

# Close communication with the database
cur.close()
conn.close()