f = open('/home/houman/Projects/Chasebot/country_code_drupal_nov_2011.txt')
out = open('/home/houman/Projects/Chasebot/chasebot_script.sql', "w")

out.write("INSERT INTO Chasebot_App_contacttype (contact_type) VALUES ('Buyer'),('Seller');\n")
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
