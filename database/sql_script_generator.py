import psycopg2

conn = psycopg2.connect("dbname=Ch4s3b0tDB user=django_user password=houmie123")
cur = conn.cursor()

f = open('/home/houman/projects/chasebot/database/country_code_drupal_nov_2011.txt')
#out = open('/home/houman/Projects/Chasebot/database/chasebot_script.sql', "w")


cur.execute("INSERT INTO chasebot_app_company (company_name, company_email) VALUES ('Venus Cloud Ltd', 'info@venuscloud.com');")
cur.execute("INSERT INTO chasebot_app_userprofile (user_id, company_id) VALUES (1, 1);")

cur.execute("INSERT INTO chasebot_app_contacttype (contact_type, company_id) VALUES ('Buyer', 1),('Seller', 1);")
cur.execute("INSERT INTO chasebot_app_gender (gender) VALUES ('Female'),('Male');")
cur.execute("INSERT INTO chasebot_app_maritalstatus (martial_status_type) VALUES ('Single'),('Married'),('Domestic partnership'),('Civil Union'),('Divorced'),('Widowed');")

for line in f:
    cur.execute("INSERT INTO chasebot_app_country (country_code, country_name) VALUES (%s, %s)", (line[:2] , line[3:-1]))                
        
f.close()
#out.close()

# Make the changes to the database persistent
conn.commit()

# Close communication with the database
cur.close()
conn.close()