f = open('/home/houman/Projects/Chasebot/database/country_code_drupal_nov_2011.txt')
out = open('/home/houman/Projects/Chasebot/database/chasebot_script.sql', "w")

out.write("INSERT INTO Chasebot_App_company (company_name, company_email) VALUES ('Venus Cloud Ltd', 'info@venuscloud.com');\n")
out.write("INSERT INTO Chasebot_App_userprofile (user_id, company_id) VALUES (1, 1);\n")

out.write("INSERT INTO Chasebot_App_contacttype (contact_type, company_id) VALUES ('Buyer', 1),('Seller', 1);\n")
out.write("INSERT INTO Chasebot_App_maritalstatus (martial_status_type) VALUES ('Single'),('Married'),('Domestic partnership'),('Civil Union'),('Divorced'),('Widowed');\n")
out.write("INSERT INTO Chasebot_App_country (country_code, country_name) VALUES \n")
count = 0
for line in f:
        if line[-1] == '\n':
                out.write('("' + line[:2] + '", "' + line[3:-1] + '"),\n')
        else:
                out.write('("' + line[:2] + '", "' + line[3:] + '");')
        
f.close()
out.close()
