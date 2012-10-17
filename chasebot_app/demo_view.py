from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from chasebot_app.models import Company, DealStatus, SalesTerm,\
    LicenseTemplate, ContactType, Country, MaritalStatus, Gender,\
    Currency
from chasebot_app.models import UserProfile
from django.utils.translation import ugettext as _
from django.db.models.aggregates import Max
from django.contrib import messages
from random import choice
from string import ascii_lowercase, digits
from django.contrib.auth import authenticate, login
from django.utils import timezone
from django.shortcuts import redirect

def generate_random_username(length=4, chars=ascii_lowercase+digits, split=4, delimiter='-'):
    username = ''.join([choice(chars) for i in xrange(length)])
    if split:
        username = delimiter.join([username[start:start+split] for start in range(0, len(username), split)])
    try:
        User.objects.get(username=username)
        return generate_random_username(length=length, chars=chars, split=split, delimiter=delimiter)
    except User.DoesNotExist:
        return username;


def demo(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')

    username = generate_random_username()
    password = User.objects.make_random_password(7)
    user = User.objects.create_user(                
                username=username,
                password=password,
                email='testuser@your_company.com'
            )
    user.first_name = _(u'Testuser')
    user.last_name = _(u'Testuser')
    user.save()    
        
    company = Company.objects.create(
                company_name = _(u'Your Company Ltd'),
                company_email = 'info@your_company.com'
            )
    
    userProfile = UserProfile(user=user, company = company, is_cb_superuser=True, license = LicenseTemplate.objects.get(pk=3))
    userProfile.save()
    
    user = authenticate(username=username, password=password)
    login(request, user)
    
    profile = user.get_profile()
        
    c1=profile.company.contact_set.create(first_name = 'John', last_name = 'Johnson', dear_name = '', address = '34 Awesome street', city='Nottinghill', postcode='2W3 5TD', country=Country.objects.get(pk=228), contact_type = ContactType.objects.get(pk=2), company_name='Johnson Brothers co.', position='Director', work_phone='020 555 78754', email='john@johnsonbro.com', birth_date='1973-12-17', contact_notes=_(u'John is a very kind and down to earth person.'), marital_status=MaritalStatus.objects.get(pk=2), gender=Gender.objects.get(pk=2), contacts_interests=_(u'Skiing, Hiking'), spouse_first_name='Maria', spouses_interests=_(u'Singing in the choir'), children_names='Dennis 4, Elena 6', home_town='London', important_client=2)
    c2=profile.company.contact_set.create(first_name = 'Ashley', last_name = 'Perrier', dear_name = '', address = '4 Nogo street', city='London', postcode='W3 2TD', country=Country.objects.get(pk=228), contact_type = ContactType.objects.get(pk=2), company_name='Aurora co.', position='Manager', work_phone='020 555 99754', email='ashley@aurora.com', birth_date='1983-02-27', contact_notes=_(u'Ashley is cold. She needs some compliments and friendly talk before the pitch.'), marital_status=MaritalStatus.objects.get(pk=1), gender=Gender.objects.get(pk=1), contacts_interests=_(u'Boxing, Dancing'), spouse_first_name='', spouses_interests='', children_names='', home_town='Glasgow', important_client=1)
    c3=profile.company.contact_set.create(first_name = 'Silvia', last_name = 'Cruze', dear_name = '', address = 'Calle de Villava 1', city='Madrid', postcode='28 950', country=Country.objects.get(pk=203), contact_type = ContactType.objects.get(pk=2), company_name='Hola co.', position='Manager', work_phone='0625 555 99754', email='silvia@hola.com', birth_date='1981-05-17', contact_notes=_(u'Silvia is an artistic person. Talking about latest art exhibition is perfect to make her interested.'), marital_status=MaritalStatus.objects.get(pk=1), gender=Gender.objects.get(pk=1), contacts_interests=_(u'Art, Painting'), spouse_first_name='', spouses_interests='', children_names='', home_town='Barcelona', important_client=0)
    c4=profile.company.contact_set.create(first_name = 'Michael', last_name = 'Anderson', dear_name = 'Mike', address = '5 Main Street', city='Platteville', postcode='53818', country=Country.objects.get(pk=229), contact_type = ContactType.objects.get(pk=2), company_name='Alien co.', position='Director', work_phone='(954) 555-1234', email='mike@alien.com', birth_date='1979-07-07', contact_notes=_(u'Mike is a religious person. Talking about church opens him up for a pitch.'), marital_status=MaritalStatus.objects.get(pk=2), gender=Gender.objects.get(pk=2), contacts_interests=_(u'Bible reading, Charity work'), spouse_first_name='Marta', spouses_interests=_(u'Bible reading, singing in the choir'), children_names='', home_town='Milwaukee', important_client=1)
    c5=profile.company.contact_set.create(first_name = 'Harry', last_name = 'Jackson', dear_name = '', address = '15 Side Street', city='New York', postcode='10008', country=Country.objects.get(pk=229), contact_type = ContactType.objects.get(pk=2), company_name='Milihop co.', position='Sales Manager', work_phone='(954) 555-4534', email='harry@milihop.com', birth_date='1967-03-09', contact_notes=_(u'Harry is introverted and gets annoyed easily. It is best to keep conversations short and get to the point.'), marital_status=MaritalStatus.objects.get(pk=6), gender=Gender.objects.get(pk=2), contacts_interests=_(u'Shooting'), spouse_first_name='Maria', spouses_interests='', children_names='Larry', home_town='Oshkosh', important_client=3)
    c6=profile.company.contact_set.create(first_name = 'Rosa', last_name = 'Wilston', dear_name = 'Ros', address = '25 Upper Street', city='New Jersey', postcode='07018', country=Country.objects.get(pk=229), contact_type = ContactType.objects.get(pk=2), company_name='Grainmill co.', position='Owner', work_phone='(954) 555-3768', email='rosa@grainmill.com', birth_date='1959-03-09', contact_notes=_(u'Rosa is friendly and easy going. She likes to speak about her children.'), marital_status=MaritalStatus.objects.get(pk=2), gender=Gender.objects.get(pk=1), contacts_interests=_(u'Running the farm'), spouse_first_name='Jack', spouses_interests=_(u'Woodcutting'), children_names='Abel, Abraham', home_town='Boscobel', important_client=2)
    c7=profile.company.contact_set.create(first_name = 'Hugo', last_name = 'Finn', dear_name = 'Harry', address = '33 Down Street', city='Los Angeles', postcode='90004', country=Country.objects.get(pk=229), contact_type = ContactType.objects.get(pk=2), company_name='Silicon Crusher co.', position='CEO', work_phone='(954) 555-3452', email='hugo@silicon-crusher.com', birth_date='1989-02-19', contact_notes=_(u'Hugo loves food. Talk subtle about any cuisine and the pitch is easy.'), marital_status=MaritalStatus.objects.get(pk=2), gender=Gender.objects.get(pk=2), contacts_interests=_(u'Exotic cuisine and restaurants'), spouse_first_name='Anna', spouses_interests=_(u'housewife, cooking'), children_names='Katy, William', home_town='Hudson', important_client=3)
    c8=profile.company.contact_set.create(first_name = 'Homer', last_name = 'Santana', dear_name = '', address = '21 Jump Street', city='Los Angeles', postcode='90006', country=Country.objects.get(pk=229), contact_type = ContactType.objects.get(pk=2), company_name='Blue Athlon co.', position='Director', work_phone='(954) 555-7833', email='hugo@blue-athlon.com', birth_date='1981-07-29', contact_notes=_(u'Homer is a funny person and loves comedy. Just crack a joke and the ice is broken.'), marital_status=MaritalStatus.objects.get(pk=1), gender=Gender.objects.get(pk=2), contacts_interests=_(u'Theater, Movies'), spouse_first_name='', spouses_interests='', children_names='Bart', home_town='Fox Lake', important_client=2)
    c9=profile.company.contact_set.create(first_name = 'William', last_name = 'Murrey', dear_name = 'Bill', address = '67 Maritime Alley', city='Chicago', postcode='46312', country=Country.objects.get(pk=229), contact_type = ContactType.objects.get(pk=2), company_name='Red Mine co.', position='Line Manager', work_phone='(954) 555-7433', email='bill@red-mine.com', birth_date='1971-01-30', contact_notes=_(u'Bill is serious and likes coffee beans. Talk about a new coffee flavor to grab his attention.'), marital_status=MaritalStatus.objects.get(pk=5), gender=Gender.objects.get(pk=2), contacts_interests=_(u'Coffee Beans, Coffee plantage'), spouse_first_name='Jane', spouses_interests='', children_names='Ann, Peter', home_town='New Berlin', important_client=1)
    c10=profile.company.contact_set.create(first_name = 'Matthew', last_name = 'Spalding', dear_name = 'Matt', address = '54 Seaside Alley', city='Chicago', postcode='46332', country=Country.objects.get(pk=229), contact_type = ContactType.objects.get(pk=2), company_name='Pink Bottle co.', position='Manager', work_phone='(954) 555-5463', email='matt@pink-bottle.com', birth_date='1975-03-30', contact_notes=_(u'Matt is calm and friendly. He loves financial topics.'), marital_status=MaritalStatus.objects.get(pk=1), gender=Gender.objects.get(pk=2), contacts_interests=_(u'Reading History, Art'), spouse_first_name='', spouses_interests='', children_names='', home_town='Rice Lake', important_client=2)
    c11=profile.company.contact_set.create(first_name = 'Jonas', last_name = 'Jones', dear_name = 'John', address = '313 Long Street', city='Florida', postcode='32007', country=Country.objects.get(pk=229), contact_type = ContactType.objects.get(pk=2), company_name='Black Cross co.', position='Manager', work_phone='(954) 555-3452', email='jonas@black-cross.com', birth_date='1978-09-21', contact_notes=_(u'John is a very busy person. You need to get to the point quickly.'), marital_status=MaritalStatus.objects.get(pk=2), gender=Gender.objects.get(pk=2), contacts_interests=_(u'Golf'), spouse_first_name='', spouses_interests='', children_names='', home_town='Waterloo', important_client=3)
    c12=profile.company.contact_set.create(first_name = 'Kaylee', last_name = 'Ashton', dear_name = '', address = '22 Short Street', city='Florida', postcode='32004', country=Country.objects.get(pk=229), contact_type = ContactType.objects.get(pk=2), company_name='Grey Train co.', position='Director', work_phone='(954) 555-3295', email='kaylee@grey-train.com', birth_date='1988-05-25', contact_notes=_(u'Kaylee is very relaxed and keen in getting discounts. With some discount any deal might turn to be successful.'), marital_status=MaritalStatus.objects.get(pk=2), gender=Gender.objects.get(pk=1), contacts_interests=_(u'Shopping'), spouse_first_name='Adam', spouses_interests=_(u'Hunting'), children_names='Eve', home_town='Sparta', important_client=2)
    c13=profile.company.contact_set.create(first_name = 'Tamara', last_name = 'Sierra', dear_name = '', address = 'Calle fontanella 7', city='Madrid', postcode='28 950', country=Country.objects.get(pk=203), contact_type = ContactType.objects.get(pk=2), company_name='Corrida co.', position='Sales Manager', work_phone='0625 555 9965', email='tamara@corrida.com', birth_date='1980-07-20', contact_notes=_(u'Tamara loves flaminco dancing. Asking about her progress in the class could open up opportunities.'), marital_status=MaritalStatus.objects.get(pk=2), gender=Gender.objects.get(pk=1), contacts_interests=_(u'flamenco dancing, playing guitar'), spouse_first_name='Fernando', spouses_interests=_(u'Theater, Music events'), children_names='Luca, Roberto, Maria', home_town='Barcelona', important_client=3)

    profile.company.salesitem_set.create(item_name = 'Hotel 3 Star')
    hotel4 = profile.company.salesitem_set.create(item_name = 'Hotel 4 Star')
    ticket = profile.company.salesitem_set.create(item_name = 'Flight Ticket')
    car = profile.company.salesitem_set.create(item_name = 'Car Hire')
    
    sandwitch = profile.company.salesitem_set.create(item_name = 'Sandwich')
    juice = profile.company.salesitem_set.create(item_name = 'Orange juice')
    cake = profile.company.salesitem_set.create(item_name = 'Cake')
    
    shirts = profile.company.salesitem_set.create(item_name = '2 x Shirts')
    ties = profile.company.salesitem_set.create(item_name = '2 x Ties')
    
    co1 = profile.company.salesitem_set.create(item_name = '10 x Cotton Saw')
    co2 = profile.company.salesitem_set.create(item_name = '120mm Cotton Mill')
    co3 = profile.company.salesitem_set.create(item_name = 'Free Installation')
    
    w1 = profile.company.salesitem_set.create(item_name = 'Web Site Development')
    w2 = profile.company.salesitem_set.create(item_name = '24/7 Support')
    w3 = profile.company.salesitem_set.create(item_name = 'Website Hosting')
    
    holiday = profile.company.dealtemplate_set.create(deal_name = _(u'Holiday package'), deal_description = _(u'This is a romantic holiday package for two weeks at the coast.'), currency = Currency.objects.get(pk=3), price = 1499, sales_term = SalesTerm.objects.get(pk=1), quantity = 1)
    holiday.sales_item.add(hotel4)
    holiday.sales_item.add(ticket)
    holiday.sales_item.add(car)
    holiday.save()
    
    lunch = profile.company.dealtemplate_set.create(deal_name = _(u'Lunch Deal'), deal_description = _(u'This is a lunch deal package for interested food chains. We aim to sell 10 deal packages per customer.'), currency = Currency.objects.get(pk=1), price = 3.99, sales_term = SalesTerm.objects.get(pk=1), quantity = 10)
    lunch.sales_item.add(sandwitch)
    lunch.sales_item.add(juice)
    lunch.sales_item.add(cake)
    lunch.save()
    
    shirt = profile.company.dealtemplate_set.create(deal_name = _(u'Shirt Deal'), deal_description = _(u'A shirt/tie deal for the fall collection. We aim to sell two deal packages per customer.'), currency = Currency.objects.get(pk=1), price = 39.99, sales_term = SalesTerm.objects.get(pk=1), quantity = 2)
    shirt.sales_item.add(shirts)
    shirt.sales_item.add(ties)    
    shirt.save()
    
    cotton = profile.company.dealtemplate_set.create(deal_name = _(u'Cotton Industrial Deal'), deal_description = _(u'Providing the basic cotton mill machinery for cotton farmers.'), currency = Currency.objects.get(pk=1), price = 4499.99, sales_term = SalesTerm.objects.get(pk=1), quantity = 1)
    cotton.sales_item.add(co1)
    cotton.sales_item.add(co2)
    cotton.sales_item.add(co3)    
    cotton.save()
    
    web = profile.company.dealtemplate_set.create(deal_name = _(u'Website Starter Deal'), deal_description = _(u'Developing a website, hosting the website and providing support in one deal.'), currency = Currency.objects.get(pk=2), price = 19.99, sales_term = SalesTerm.objects.get(pk=3), quantity = 1)
    web.sales_item.add(w1)
    web.sales_item.add(w2)
    web.sales_item.add(w3)    
    web.save()
    
    call1 = c1.conversation_set.create(conversation_datetime=timezone.now(), subject='Initial Offer', notes=_(u'%(name)s doesn\'t seem too keen on the new offer. Maybe a discount would be helpful.') % {'name' : 'John'})
    set_dic = c1.deal_set.filter(deal_template_id=holiday.id).aggregate(Max('set'))                            
    set_val = set_dic.get('set__max', 0)
    if not set_val:
        set_val = 0    
    deal1 = c1.deal_set.create(
                        conversation = call1,
                        deal_datetime=call1.conversation_datetime, 
                        status=DealStatus.objects.get(pk=1),                         
                        deal_template=holiday,
                        deal_template_name=holiday.deal_name,
                        set=set_val+1,
                        deal_description = holiday.deal_description,
                        price = holiday.price,        
                        currency = holiday.currency,                
                        sales_term = holiday.sales_term,
                        quantity = holiday.quantity                                                                    
                        )    
    for item in holiday.sales_item.all():
        deal1.sales_item.add(item)
    deal1.save()
    
    call2 = c1.conversation_set.create(conversation_datetime=call1.conversation_datetime + timezone.timedelta(days=7, hours=4), subject=_(u'Follow Up Offer'), notes=_(u'%(name)s would commit if there is a discount of 5%% on the deal.') % {'name' : 'John'})
    deal2 = c1.deal_set.create(
                        deal_id=deal1.deal_id,
                        conversation = call2,
                        deal_datetime=call2.conversation_datetime, 
                        status=DealStatus.objects.get(pk=3),
                        deal_template=deal1.deal_template,
                        deal_template_name=deal1.deal_template_name,
                        deal_instance_name=deal1.deal_instance_name,
                        set=deal1.set,
                        deal_description = deal1.deal_description,
                        price = deal1.price - deal1.price * 0.05,
                        currency = deal1.currency,                
                        sales_term = deal1.sales_term,
                        quantity = deal1.quantity                                                                    
                        )    
    for item in deal1.sales_item.all():
        deal2.sales_item.add(item)
    deal2.save()
    
    call3 = c1.conversation_set.create(conversation_datetime=call2.conversation_datetime + timezone.timedelta(days=4, hours=3), subject=_(u'Second Follow Up Offer'), notes=_(u"After another conversation, %(name)s has accepted the offer. It's a win.") % {'name' : 'John'})
    deal3 = c1.deal_set.create(
                        deal_id=deal2.deal_id,
                        conversation = call3,
                        deal_datetime=call3.conversation_datetime, 
                        status=DealStatus.objects.get(pk=5),
                        deal_template=deal2.deal_template,
                        deal_template_name=deal2.deal_template_name,
                        deal_instance_name=deal2.deal_instance_name,
                        set=deal2.set,
                        deal_description = deal2.deal_description,
                        price = deal2.price,
                        currency = deal2.currency,                
                        sales_term = deal2.sales_term,
                        quantity = deal2.quantity                                                                    
                        )    
    for item in deal2.sales_item.all():
        deal3.sales_item.add(item)
    deal3.save()

    call1 = c2.conversation_set.create(conversation_datetime=timezone.now(), subject=_(u'Initial Offer'), notes=_(u'%(name)s looks for a cloud solution for her B2B business. I will try to see if our Website package might interest her.') % {'name' : 'Ashley' })
    set_dic = c2.deal_set.filter(deal_template_id=holiday.id).aggregate(Max('set'))                            
    set_val = set_dic.get('set__max', 0)
    if not set_val:
        set_val = 0    
    deal1 = c2.deal_set.create(
                        conversation = call1,
                        deal_datetime=call1.conversation_datetime, 
                        status=DealStatus.objects.get(pk=1),                         
                        deal_template=web,
                        deal_template_name=web.deal_name,
                        set=set_val+1,
                        deal_description = web.deal_description,
                        price = web.price,        
                        currency = web.currency,                
                        sales_term = web.sales_term,
                        quantity = web.quantity                                                                    
                        )    
    for item in web.sales_item.all():
        deal1.sales_item.add(item)
    deal1.save()
    
    call2 = c2.conversation_set.create(conversation_datetime=call1.conversation_datetime + timezone.timedelta(days=2, hours=1), subject=_(u'Follow Up Offer'), notes=_(u'%(name)s will consider the offer and needs some time to think about it.') % {'name' : 'Ashley'})
    deal2 = c2.deal_set.create(
                        deal_id=deal1.deal_id,
                        conversation = call2,
                        deal_datetime=call2.conversation_datetime, 
                        status=DealStatus.objects.get(pk=2),
                        deal_template=deal1.deal_template,
                        deal_template_name=deal1.deal_template_name,
                        deal_instance_name=deal1.deal_instance_name,
                        set=deal1.set,
                        deal_description = deal1.deal_description,
                        price = deal1.price,
                        currency = deal1.currency,                
                        sales_term = deal1.sales_term,
                        quantity = deal1.quantity                                                                    
                        )
    for item in deal1.sales_item.all():
        deal2.sales_item.add(item)
    deal2.save()

    call3 = c2.conversation_set.create(conversation_datetime=call2.conversation_datetime + timezone.timedelta(days=5, hours=3), subject=_(u'Second Follow Up Offer'), notes=_(u'After another conversation, %(name)s doesn\'t seem to be interested any longer. Its a loss.') % {'name' : 'Ashley'})
    deal3 = c2.deal_set.create(
                        deal_id=deal2.deal_id,
                        conversation = call3,
                        deal_datetime=call3.conversation_datetime, 
                        status=DealStatus.objects.get(pk=6),
                        deal_template=deal2.deal_template,
                        deal_template_name=deal2.deal_template_name,
                        deal_instance_name=deal2.deal_instance_name,
                        set=deal2.set,
                        deal_description = deal2.deal_description,
                        price = deal2.price,
                        currency = deal2.currency,                
                        sales_term = deal2.sales_term,
                        quantity = deal2.quantity                                                                    
                        )    
    for item in deal2.sales_item.all():
        deal3.sales_item.add(item)
    deal3.save()

    call1 = c3.conversation_set.create(conversation_datetime=timezone.now(), subject=_(u'Initial Offer'), notes=_(u'%(name)s is interested in purchasing 25 lunch deals for her food store.') % {'name' : 'Silvia'})
    set_dic = c3.deal_set.filter(deal_template_id=holiday.id).aggregate(Max('set'))                            
    set_val = set_dic.get('set__max', 0)
    if not set_val:
        set_val = 0    
    deal1 = c3.deal_set.create(
                        conversation = call1,
                        deal_datetime=call1.conversation_datetime, 
                        status=DealStatus.objects.get(pk=1),                         
                        deal_template=lunch,
                        deal_template_name=lunch.deal_name,
                        set=set_val+1,
                        deal_description = lunch.deal_description,
                        price = lunch.price,        
                        currency = lunch.currency,                
                        sales_term = lunch.sales_term,
                        quantity = lunch.quantity                                                                    
                        )    
    for item in lunch.sales_item.all():
        deal1.sales_item.add(item)
    deal1.save()
    
    call2 = c3.conversation_set.create(conversation_datetime=call1.conversation_datetime + timezone.timedelta(days=2, hours=1), subject=_(u'Follow Up Offer'), notes=_(u'Made some progress with the deal. Trying to convince %(name)s of the lunch deal quality. Deal still in progress...') % {'name' : 'Silvia'})
    deal2 = c3.deal_set.create(
                        deal_id=deal1.deal_id,
                        conversation = call2,
                        deal_datetime=call2.conversation_datetime, 
                        status=DealStatus.objects.get(pk=2),
                        deal_template=deal1.deal_template,
                        deal_template_name=deal1.deal_template_name,
                        deal_instance_name=deal1.deal_instance_name,
                        set=deal1.set,
                        deal_description = deal1.deal_description,
                        price = deal1.price,
                        currency = deal1.currency,                
                        sales_term = deal1.sales_term,
                        quantity = deal1.quantity                                                                    
                        )
    for item in deal1.sales_item.all():
        deal2.sales_item.add(item)
    deal2.save()
    
    call1 = c4.conversation_set.create(conversation_datetime=timezone.now(), subject=_(u'Initial Offer'), notes=_(u'%(name)s has a new fashion shop and might be interested in our quality shirts and ties as a package.') % {'name' : 'Michael'})
    set_dic = c4.deal_set.filter(deal_template_id=holiday.id).aggregate(Max('set'))                            
    set_val = set_dic.get('set__max', 0)
    if not set_val:
        set_val = 0    
    deal1 = c4.deal_set.create(
                        conversation = call1,
                        deal_datetime=call1.conversation_datetime, 
                        status=DealStatus.objects.get(pk=1),                         
                        deal_template=shirt,
                        deal_template_name=shirt.deal_name,
                        set=set_val+1,
                        deal_description = shirt.deal_description,
                        price = shirt.price,        
                        currency = shirt.currency,                
                        sales_term = shirt.sales_term,
                        quantity = shirt.quantity                                                                    
                        )    
    for item in shirt.sales_item.all():
        deal1.sales_item.add(item)
    deal1.save()
    
    call2 = c4.conversation_set.create(conversation_datetime=call1.conversation_datetime + timezone.timedelta(days=4, hours=1), subject=_(u'Follow Up Offer'), notes=_(u'I offered him a discount of 5%%. %(name)s will consider the offer and needs some time to think about it.') % {'name' : 'Michael'})
    deal2 = c4.deal_set.create(
                        deal_id=deal1.deal_id,
                        conversation = call2,
                        deal_datetime=call2.conversation_datetime, 
                        status=DealStatus.objects.get(pk=3),
                        deal_template=deal1.deal_template,
                        deal_template_name=deal1.deal_template_name,
                        deal_instance_name=deal1.deal_instance_name,
                        set=deal1.set,
                        deal_description = deal1.deal_description,
                        price = deal1.price - deal1.price * 0.05,
                        currency = deal1.currency,                
                        sales_term = deal1.sales_term,
                        quantity = deal1.quantity                                                                    
                        )
    for item in deal1.sales_item.all():
        deal2.sales_item.add(item)
    deal2.save()

    call3 = c4.conversation_set.create(conversation_datetime=call2.conversation_datetime + timezone.timedelta(days=8, hours=3), subject=_(u'Second Follow Up Offer'), notes=_(u'%(name)s is happy with discount and would like to purchase ten packages.') % {'name' : 'Michael'})
    deal3 = c4.deal_set.create(
                        deal_id=deal2.deal_id,
                        conversation = call3,
                        deal_datetime=call3.conversation_datetime, 
                        status=DealStatus.objects.get(pk=5),
                        deal_template=deal2.deal_template,
                        deal_template_name=deal2.deal_template_name,
                        deal_instance_name=deal2.deal_instance_name,
                        set=deal2.set,
                        deal_description = deal2.deal_description,
                        price = deal2.price,
                        currency = deal2.currency,                
                        sales_term = deal2.sales_term,
                        quantity = deal2.quantity                                                                    
                        )    
    for item in deal2.sales_item.all():
        deal3.sales_item.add(item)
    deal3.save() 


    call1 = c5.conversation_set.create(conversation_datetime=timezone.now(), subject=_(u'Initial Offer'), notes=_(u'%(name)s is investing into a cotton mill factory and might be a potential client.') % {'name' : 'Harry'})
    set_dic = c5.deal_set.filter(deal_template_id=holiday.id).aggregate(Max('set'))                            
    set_val = set_dic.get('set__max', 0)
    if not set_val:
        set_val = 0    
    deal1 = c5.deal_set.create(
                        conversation = call1,
                        deal_datetime=call1.conversation_datetime, 
                        status=DealStatus.objects.get(pk=1),                         
                        deal_template=cotton,
                        deal_template_name=cotton.deal_name,
                        set=set_val+1,
                        deal_description = cotton.deal_description,
                        price = cotton.price,        
                        currency = cotton.currency,                
                        sales_term = cotton.sales_term,
                        quantity = cotton.quantity                                                                    
                        )    
    for item in cotton.sales_item.all():
        deal1.sales_item.add(item)
    deal1.save()
    
    call2 = c5.conversation_set.create(conversation_datetime=call1.conversation_datetime + timezone.timedelta(days=1, hours=4), subject=_(u'Follow Up Offer'), notes=_(u'%(name)s doesn\'t need the 10 cotton saws. I agreed to remove it from the package and offer a 25%% discount. He needs now some time to think about it.') % {'name' : 'Harry'})
    deal2 = c5.deal_set.create(
                        deal_id=deal1.deal_id,
                        conversation = call2,
                        deal_datetime=call2.conversation_datetime, 
                        status=DealStatus.objects.get(pk=3),
                        deal_template=deal1.deal_template,
                        deal_template_name=deal1.deal_template_name,
                        deal_instance_name=deal1.deal_instance_name,
                        set=deal1.set,
                        deal_description = deal1.deal_description,
                        price = deal1.price - deal1.price * 0.25,
                        currency = deal1.currency,                
                        sales_term = deal1.sales_term,
                        quantity = deal1.quantity                                                                    
                        )
    deal2.sales_item.add(co2)
    deal2.sales_item.add(co3)    
    deal2.save()

    call3 = c5.conversation_set.create(conversation_datetime=call2.conversation_datetime + timezone.timedelta(days=3, hours=2), subject=_(u'Second Follow Up Offer'), notes=_(u"%(name)s is happy with the new deal and price. It's a win.") % {'name' : 'Harry'})
    deal3 = c5.deal_set.create(
                        deal_id=deal2.deal_id,
                        conversation = call3,
                        deal_datetime=call3.conversation_datetime, 
                        status=DealStatus.objects.get(pk=5),
                        deal_template=deal2.deal_template,
                        deal_template_name=deal2.deal_template_name,
                        deal_instance_name=deal2.deal_instance_name,
                        set=deal2.set,
                        deal_description = deal2.deal_description,
                        price = deal2.price,
                        currency = deal2.currency,                
                        sales_term = deal2.sales_term,
                        quantity = deal2.quantity                                                                    
                        )    
    for item in deal2.sales_item.all():
        deal3.sales_item.add(item)
    deal3.save()
    
    call1 = c6.conversation_set.create(conversation_datetime=timezone.now(), subject=_(u'Initial Offer'), notes=_(u'%(name)s looks for a cloud solution for her B2B business. I will try to see if our Website package might interest her.') % {'name' : 'Rosa' })
    set_dic = c6.deal_set.filter(deal_template_id=holiday.id).aggregate(Max('set'))                            
    set_val = set_dic.get('set__max', 0)
    if not set_val:
        set_val = 0    
    deal1 = c6.deal_set.create(
                        conversation = call1,
                        deal_datetime=call1.conversation_datetime, 
                        status=DealStatus.objects.get(pk=1),
                        deal_template=web,
                        deal_template_name=web.deal_name,
                        set=set_val+1,
                        deal_description = web.deal_description,
                        price = web.price,
                        currency = web.currency,
                        sales_term = web.sales_term,
                        quantity = web.quantity
                        )    
    for item in web.sales_item.all():
        deal1.sales_item.add(item)
    deal1.save()
    
    call2 = c6.conversation_set.create(conversation_datetime=call1.conversation_datetime + timezone.timedelta(days=2, hours=1), subject=_(u'Follow Up Offer'), notes=_(u'%(name)s will consider the offer and needs some time to think about it. ') % {'name' : 'Rosa'})
    deal2 = c6.deal_set.create(
                        deal_id=deal1.deal_id,
                        conversation = call2,
                        deal_datetime=call2.conversation_datetime, 
                        status=DealStatus.objects.get(pk=2),
                        deal_template=deal1.deal_template,
                        deal_template_name=deal1.deal_template_name,
                        deal_instance_name=deal1.deal_instance_name,
                        set=deal1.set,
                        deal_description = deal1.deal_description,
                        price = deal1.price,
                        currency = deal1.currency,                
                        sales_term = deal1.sales_term,
                        quantity = deal1.quantity                                                                    
                        )
    for item in deal1.sales_item.all():
        deal2.sales_item.add(item)
    deal2.save()

    call3 = c6.conversation_set.create(conversation_datetime=call2.conversation_datetime + timezone.timedelta(days=5, hours=3), subject=_(u'Second Follow Up Offer'), notes=_(u"After another conversation, %(name)s seems to be interested. It's a win") % {'name' : 'Rosa'})
    deal3 = c6.deal_set.create(
                        deal_id=deal2.deal_id,
                        conversation = call3,
                        deal_datetime=call3.conversation_datetime, 
                        status=DealStatus.objects.get(pk=5),
                        deal_template=deal2.deal_template,
                        deal_template_name=deal2.deal_template_name,
                        deal_instance_name=deal2.deal_instance_name,
                        set=deal2.set,
                        deal_description = deal2.deal_description,
                        price = deal2.price,
                        currency = deal2.currency,                
                        sales_term = deal2.sales_term,
                        quantity = deal2.quantity                                                                    
                        )    
    for item in deal2.sales_item.all():
        deal3.sales_item.add(item)
    deal3.save()

    call1 = c7.conversation_set.create(conversation_datetime=timezone.now(), subject='Initial Offer', notes=_(u'%(name)s doesn\'t seem too keen on the new offer. Maybe a discount would be helpful.') % {'name' : 'Hugo'})
    set_dic = c7.deal_set.filter(deal_template_id=holiday.id).aggregate(Max('set'))                            
    set_val = set_dic.get('set__max', 0)
    if not set_val:
        set_val = 0    
    deal1 = c7.deal_set.create(
                        conversation = call1,
                        deal_datetime=call1.conversation_datetime, 
                        status=DealStatus.objects.get(pk=1),                         
                        deal_template=holiday,
                        deal_template_name=holiday.deal_name,
                        set=set_val+1,
                        deal_description = holiday.deal_description,
                        price = holiday.price,        
                        currency = holiday.currency,                
                        sales_term = holiday.sales_term,
                        quantity = holiday.quantity                                                                    
                        )    
    for item in holiday.sales_item.all():
        deal1.sales_item.add(item)
    deal1.save()
    
    call2 = c7.conversation_set.create(conversation_datetime=call1.conversation_datetime + timezone.timedelta(days=7, hours=4), subject=_(u'Follow Up Offer'), notes=_(u'%(name)s would commit if there is a discount of 5%% on the deal.') % {'name' : 'Hugo'})
    deal2 = c7.deal_set.create(
                        deal_id=deal1.deal_id,
                        conversation = call2,
                        deal_datetime=call2.conversation_datetime, 
                        status=DealStatus.objects.get(pk=3),
                        deal_template=deal1.deal_template,
                        deal_template_name=deal1.deal_template_name,
                        deal_instance_name=deal1.deal_instance_name,
                        set=deal1.set,
                        deal_description = deal1.deal_description,
                        price = deal1.price - deal1.price * 0.05,
                        currency = deal1.currency,                
                        sales_term = deal1.sales_term,
                        quantity = deal1.quantity                                                                    
                        )    
    for item in deal1.sales_item.all():
        deal2.sales_item.add(item)
    deal2.save()
    
    call3 = c7.conversation_set.create(conversation_datetime=call2.conversation_datetime + timezone.timedelta(days=4, hours=3), subject=_(u'Second Follow Up Offer'), notes=_(u"After another conversation, %(name)s has accepted the offer. It's a win.") % {'name' : 'Hugo'})
    deal3 = c7.deal_set.create(
                        deal_id=deal2.deal_id,
                        conversation = call3,
                        deal_datetime=call3.conversation_datetime, 
                        status=DealStatus.objects.get(pk=5),
                        deal_template=deal2.deal_template,
                        deal_template_name=deal2.deal_template_name,
                        deal_instance_name=deal2.deal_instance_name,
                        set=deal2.set,
                        deal_description = deal2.deal_description,
                        price = deal2.price,
                        currency = deal2.currency,                
                        sales_term = deal2.sales_term,
                        quantity = deal2.quantity                                                                    
                        )    
    for item in deal2.sales_item.all():
        deal3.sales_item.add(item)
    deal3.save()

    call1 = c8.conversation_set.create(conversation_datetime=timezone.now(), subject=_(u'Initial Offer'), notes=_(u'%(name)s is interested in purchasing 25 lunch deals for her food store.') % {'name' : 'Homer'})
    set_dic = c8.deal_set.filter(deal_template_id=holiday.id).aggregate(Max('set'))                            
    set_val = set_dic.get('set__max', 0)
    if not set_val:
        set_val = 0    
    deal1 = c8.deal_set.create(
                        conversation = call1,
                        deal_datetime=call1.conversation_datetime, 
                        status=DealStatus.objects.get(pk=1),                         
                        deal_template=lunch,
                        deal_template_name=lunch.deal_name,
                        set=set_val+1,
                        deal_description = lunch.deal_description,
                        price = lunch.price,        
                        currency = lunch.currency,                
                        sales_term = lunch.sales_term,
                        quantity = lunch.quantity                                                                    
                        )    
    for item in lunch.sales_item.all():
        deal1.sales_item.add(item)
    deal1.save()
    
    call2 = c8.conversation_set.create(conversation_datetime=call1.conversation_datetime + timezone.timedelta(days=2, hours=1), subject=_(u'Follow Up Offer'), notes=_(u'Made some progress with the deal. Trying to convince %(name)s of the lunch deal quality. Deal still in progress...') % {'name' : 'Homer'})
    deal2 = c8.deal_set.create(
                        deal_id=deal1.deal_id,
                        conversation = call2,
                        deal_datetime=call2.conversation_datetime, 
                        status=DealStatus.objects.get(pk=3),
                        deal_template=deal1.deal_template,
                        deal_template_name=deal1.deal_template_name,
                        deal_instance_name=deal1.deal_instance_name,
                        set=deal1.set,
                        deal_description = deal1.deal_description,
                        price = deal1.price,
                        currency = deal1.currency,                
                        sales_term = deal1.sales_term,
                        quantity = deal1.quantity                                                                    
                        )
    for item in deal1.sales_item.all():
        deal2.sales_item.add(item)
    deal2.save()
    
    call3 = c8.conversation_set.create(conversation_datetime=call1.conversation_datetime + timezone.timedelta(days=2, hours=1), subject=_(u'Follow Up Offer'), notes=_(u"%(name)s is happy with the price. It's a win.") % {'name' : 'Homer'})
    deal3 = c8.deal_set.create(
                        deal_id=deal2.deal_id,
                        conversation = call3,
                        deal_datetime=call3.conversation_datetime, 
                        status=DealStatus.objects.get(pk=5),
                        deal_template=deal2.deal_template,
                        deal_template_name=deal2.deal_template_name,
                        deal_instance_name=deal2.deal_instance_name,
                        set=deal2.set,
                        deal_description = deal2.deal_description,
                        price = deal2.price,
                        currency = deal2.currency,                
                        sales_term = deal2.sales_term,
                        quantity = deal2.quantity                                                                    
                        )
    for item in deal2.sales_item.all():
        deal3.sales_item.add(item)
    deal3.save()
    
    call1 = c9.conversation_set.create(conversation_datetime=timezone.now(), subject=_(u'Initial Offer'), notes=_(u'%(name)s is investing into a cotton mill factory and might be a potential client.') % {'name' : 'William'})
    set_dic = c9.deal_set.filter(deal_template_id=holiday.id).aggregate(Max('set'))                            
    set_val = set_dic.get('set__max', 0)
    if not set_val:
        set_val = 0    
    deal1 = c9.deal_set.create(
                        conversation = call1,
                        deal_datetime=call1.conversation_datetime, 
                        status=DealStatus.objects.get(pk=1),                         
                        deal_template=cotton,
                        deal_template_name=cotton.deal_name,
                        set=set_val+1,
                        deal_description = cotton.deal_description,
                        price = cotton.price,        
                        currency = cotton.currency,                
                        sales_term = cotton.sales_term,
                        quantity = cotton.quantity                                                                    
                        )    
    for item in cotton.sales_item.all():
        deal1.sales_item.add(item)
    deal1.save()
    
    call2 = c9.conversation_set.create(conversation_datetime=call1.conversation_datetime + timezone.timedelta(days=1, hours=4), subject=_(u'Follow Up Offer'), notes=_(u'%(name)s doesn\'t need the 10 cotton saws. I agreed to remove it from the package and offer a 25%% discount. He needs now some time to think about it.') % {'name' : 'William'})
    deal2 = c9.deal_set.create(
                        deal_id=deal1.deal_id,
                        conversation = call2,
                        deal_datetime=call2.conversation_datetime, 
                        status=DealStatus.objects.get(pk=3),
                        deal_template=deal1.deal_template,
                        deal_template_name=deal1.deal_template_name,
                        deal_instance_name=deal1.deal_instance_name,
                        set=deal1.set,
                        deal_description = deal1.deal_description,
                        price = deal1.price - deal1.price * 0.25,
                        currency = deal1.currency,                
                        sales_term = deal1.sales_term,
                        quantity = deal1.quantity                                                                    
                        )
    deal2.sales_item.add(co2)
    deal2.sales_item.add(co3)    
    deal2.save()

    call3 = c9.conversation_set.create(conversation_datetime=call2.conversation_datetime + timezone.timedelta(days=3, hours=2), subject=_(u'Second Follow Up Offer'), notes=_(u"%(name)s is happy with the new deal and price. It's a win.") % {'name' : 'William'})
    deal3 = c9.deal_set.create(
                        deal_id=deal2.deal_id,
                        conversation = call3,
                        deal_datetime=call3.conversation_datetime, 
                        status=DealStatus.objects.get(pk=5),
                        deal_template=deal2.deal_template,
                        deal_template_name=deal2.deal_template_name,
                        deal_instance_name=deal2.deal_instance_name,
                        set=deal2.set,
                        deal_description = deal2.deal_description,
                        price = deal2.price,
                        currency = deal2.currency,                
                        sales_term = deal2.sales_term,
                        quantity = deal2.quantity                                                                    
                        )    
    for item in deal2.sales_item.all():
        deal3.sales_item.add(item)
    deal3.save()
    
    call1 = c10.conversation_set.create(conversation_datetime=timezone.now(), subject=_(u'Initial Offer'), notes=_(u'%(name)s looks for a cloud solution for her B2B business. I will try to see if our Website package might interest her.') % {'name' : 'Matthew' })
    set_dic = c10.deal_set.filter(deal_template_id=holiday.id).aggregate(Max('set'))                            
    set_val = set_dic.get('set__max', 0)
    if not set_val:
        set_val = 0    
    deal1 = c10.deal_set.create(
                        conversation = call1,
                        deal_datetime=call1.conversation_datetime, 
                        status=DealStatus.objects.get(pk=1),                         
                        deal_template=web,
                        deal_template_name=web.deal_name,
                        set=set_val+1,
                        deal_description = web.deal_description,
                        price = web.price,        
                        currency = web.currency,                
                        sales_term = web.sales_term,
                        quantity = web.quantity                                                                    
                        )    
    for item in web.sales_item.all():
        deal1.sales_item.add(item)
    deal1.save()
    
    call2 = c10.conversation_set.create(conversation_datetime=call1.conversation_datetime + timezone.timedelta(days=2, hours=1), subject=_(u'Follow Up Offer'), notes=_(u'%(name)s will consider the offer and needs some time to think about it.') % {'name' : 'Matthew'})
    deal2 = c10.deal_set.create(
                        deal_id=deal1.deal_id,
                        conversation = call2,
                        deal_datetime=call2.conversation_datetime, 
                        status=DealStatus.objects.get(pk=2),
                        deal_template=deal1.deal_template,
                        deal_template_name=deal1.deal_template_name,
                        deal_instance_name=deal1.deal_instance_name,
                        set=deal1.set,
                        deal_description = deal1.deal_description,
                        price = deal1.price,
                        currency = deal1.currency,                
                        sales_term = deal1.sales_term,
                        quantity = deal1.quantity                                                                    
                        )
    for item in deal1.sales_item.all():
        deal2.sales_item.add(item)
    deal2.save()

    call3 = c10.conversation_set.create(conversation_datetime=call2.conversation_datetime + timezone.timedelta(days=5, hours=3), subject=_(u'Second Follow Up Offer'), notes=_(u'After another conversation, %(name)s doesn\'t seem to be interested any longer. Its a loss.') % {'name' : 'Matthew'})
    deal3 = c10.deal_set.create(
                        deal_id=deal2.deal_id,
                        conversation = call3,
                        deal_datetime=call3.conversation_datetime, 
                        status=DealStatus.objects.get(pk=6),
                        deal_template=deal2.deal_template,
                        deal_template_name=deal2.deal_template_name,
                        deal_instance_name=deal2.deal_instance_name,
                        set=deal2.set,
                        deal_description = deal2.deal_description,
                        price = deal2.price,
                        currency = deal2.currency,                
                        sales_term = deal2.sales_term,
                        quantity = deal2.quantity                                                                    
                        )    
    for item in deal2.sales_item.all():
        deal3.sales_item.add(item)
    deal3.save()
    
    call1 = c11.conversation_set.create(conversation_datetime=timezone.now(), subject=_(u'Initial Offer'), notes=_(u'%(name)s has a new fashion shop and might be interested in our quality shirts and ties as a package.') % {'name' : 'Jonas'})
    set_dic = c11.deal_set.filter(deal_template_id=holiday.id).aggregate(Max('set'))                            
    set_val = set_dic.get('set__max', 0)
    if not set_val:
        set_val = 0    
    deal1 = c11.deal_set.create(
                        conversation = call1,
                        deal_datetime=call1.conversation_datetime, 
                        status=DealStatus.objects.get(pk=1),                         
                        deal_template=shirt,
                        deal_template_name=shirt.deal_name,
                        set=set_val+1,
                        deal_description = shirt.deal_description,
                        price = shirt.price,        
                        currency = shirt.currency,                
                        sales_term = shirt.sales_term,
                        quantity = shirt.quantity                                                                    
                        )    
    for item in shirt.sales_item.all():
        deal1.sales_item.add(item)
    deal1.save()
    
    call2 = c11.conversation_set.create(conversation_datetime=call1.conversation_datetime + timezone.timedelta(days=4, hours=1), subject=_(u'Follow Up Offer'), notes=_(u'I offered him a discount of 5%%. %(name)s will consider the offer and needs some time to think about it.') % {'name' : 'Michael'})
    deal2 = c11.deal_set.create(
                        deal_id=deal1.deal_id,
                        conversation = call2,
                        deal_datetime=call2.conversation_datetime, 
                        status=DealStatus.objects.get(pk=3),
                        deal_template=deal1.deal_template,
                        deal_template_name=deal1.deal_template_name,
                        deal_instance_name=deal1.deal_instance_name,
                        set=deal1.set,
                        deal_description = deal1.deal_description,
                        price = deal1.price - deal1.price * 0.05,
                        currency = deal1.currency,                
                        sales_term = deal1.sales_term,
                        quantity = deal1.quantity                                                                    
                        )
    for item in deal1.sales_item.all():
        deal2.sales_item.add(item)
    deal2.save()

    call3 = c11.conversation_set.create(conversation_datetime=call2.conversation_datetime + timezone.timedelta(days=8, hours=3), subject=_(u'Second Follow Up Offer'), notes=_(u'%(name)s is happy with discount and would like to purchase ten packages.') % {'name' : 'Michael'})
    deal3 = c11.deal_set.create(
                        deal_id=deal2.deal_id,
                        conversation = call3,
                        deal_datetime=call3.conversation_datetime, 
                        status=DealStatus.objects.get(pk=5),
                        deal_template=deal2.deal_template,
                        deal_template_name=deal2.deal_template_name,
                        deal_instance_name=deal2.deal_instance_name,
                        set=deal2.set,
                        deal_description = deal2.deal_description,
                        price = deal2.price,
                        currency = deal2.currency,                
                        sales_term = deal2.sales_term,
                        quantity = deal2.quantity                                                                    
                        )    
    for item in deal2.sales_item.all():
        deal3.sales_item.add(item)
    deal3.save()
    
    call1 = c12.conversation_set.create(conversation_datetime=timezone.now(), subject='Initial Offer', notes=_(u'%(name)s doesn\'t seem too keen on the new offer. Maybe a discount would be helpful.') % {'name' : 'Kaylee'})
    set_dic = c12.deal_set.filter(deal_template_id=holiday.id).aggregate(Max('set'))                            
    set_val = set_dic.get('set__max', 0)
    if not set_val:
        set_val = 0    
    deal1 = c12.deal_set.create(
                        conversation = call1,
                        deal_datetime=call1.conversation_datetime, 
                        status=DealStatus.objects.get(pk=1),                         
                        deal_template=holiday,
                        deal_template_name=holiday.deal_name,
                        set=set_val+1,
                        deal_description = holiday.deal_description,
                        price = holiday.price,        
                        currency = holiday.currency,                
                        sales_term = holiday.sales_term,
                        quantity = holiday.quantity                                                                    
                        )    
    for item in holiday.sales_item.all():
        deal1.sales_item.add(item)
    deal1.save()
    
    call2 = c12.conversation_set.create(conversation_datetime=call1.conversation_datetime + timezone.timedelta(days=7, hours=4), subject=_(u'Follow Up Offer'), notes=_(u'%(name)s would commit if there is a discount of 5%% on the deal.') % {'name' : 'Kaylee'})
    deal2 = c12.deal_set.create(
                        deal_id=deal1.deal_id,
                        conversation = call2,
                        deal_datetime=call2.conversation_datetime, 
                        status=DealStatus.objects.get(pk=3),
                        deal_template=deal1.deal_template,
                        deal_template_name=deal1.deal_template_name,
                        deal_instance_name=deal1.deal_instance_name,
                        set=deal1.set,
                        deal_description = deal1.deal_description,
                        price = deal1.price - deal1.price * 0.05,
                        currency = deal1.currency,                
                        sales_term = deal1.sales_term,
                        quantity = deal1.quantity                                                                    
                        )    
    for item in deal1.sales_item.all():
        deal2.sales_item.add(item)
    deal2.save()
    
    call3 = c12.conversation_set.create(conversation_datetime=call2.conversation_datetime + timezone.timedelta(days=4, hours=3), subject=_(u'Second Follow Up Offer'), notes=_(u"After another conversation, %(name)s has accepted the offer. It's a win.") % {'name' : 'Kaylee'})
    deal3 = c12.deal_set.create(
                        deal_id=deal2.deal_id,
                        conversation = call3,
                        deal_datetime=call3.conversation_datetime, 
                        status=DealStatus.objects.get(pk=5),
                        deal_template=deal2.deal_template,
                        deal_template_name=deal2.deal_template_name,
                        deal_instance_name=deal2.deal_instance_name,
                        set=deal2.set,
                        deal_description = deal2.deal_description,
                        price = deal2.price,
                        currency = deal2.currency,                
                        sales_term = deal2.sales_term,
                        quantity = deal2.quantity                                                                    
                        )    
    for item in deal2.sales_item.all():
        deal3.sales_item.add(item)
    deal3.save()
    
    call1 = c13.conversation_set.create(conversation_datetime=timezone.now(), subject=_(u'Initial Offer'), notes=_(u'%(name)s has a new fashion shop and might be interested in our quality shirts and ties as a package.') % {'name' : 'Tamara'})
    set_dic = c13.deal_set.filter(deal_template_id=holiday.id).aggregate(Max('set'))                            
    set_val = set_dic.get('set__max', 0)
    if not set_val:
        set_val = 0    
    deal1 = c13.deal_set.create(
                        conversation = call1,
                        deal_datetime=call1.conversation_datetime, 
                        status=DealStatus.objects.get(pk=1),                         
                        deal_template=shirt,
                        deal_template_name=shirt.deal_name,
                        set=set_val+1,
                        deal_description = shirt.deal_description,
                        price = shirt.price,        
                        currency = shirt.currency,                
                        sales_term = shirt.sales_term,
                        quantity = shirt.quantity                                                                    
                        )    
    for item in shirt.sales_item.all():
        deal1.sales_item.add(item)
    deal1.save()
    
    call2 = c13.conversation_set.create(conversation_datetime=call1.conversation_datetime + timezone.timedelta(days=4, hours=1), subject=_(u'Follow Up Offer'), notes=_(u'I offered him a discount of 5%%. %(name)s will consider the offer and needs some time to think about it.') % {'name' : 'Tamara'})
    deal2 = c13.deal_set.create(
                        deal_id=deal1.deal_id,
                        conversation = call2,
                        deal_datetime=call2.conversation_datetime, 
                        status=DealStatus.objects.get(pk=3),
                        deal_template=deal1.deal_template,
                        deal_template_name=deal1.deal_template_name,
                        deal_instance_name=deal1.deal_instance_name,
                        set=deal1.set,
                        deal_description = deal1.deal_description,
                        price = deal1.price - deal1.price * 0.05,
                        currency = deal1.currency,                
                        sales_term = deal1.sales_term,
                        quantity = deal1.quantity                                                                    
                        )
    for item in deal1.sales_item.all():
        deal2.sales_item.add(item)
    deal2.save()

    call3 = c13.conversation_set.create(conversation_datetime=call2.conversation_datetime + timezone.timedelta(days=8, hours=3), subject=_(u'Second Follow Up Offer'), notes=_(u'%(name)s is happy with discount and would like to purchase ten packages.') % {'name' : 'Tamara'})
    deal3 = c13.deal_set.create(
                        deal_id=deal2.deal_id,
                        conversation = call3,
                        deal_datetime=call3.conversation_datetime, 
                        status=DealStatus.objects.get(pk=5),
                        deal_template=deal2.deal_template,
                        deal_template_name=deal2.deal_template_name,
                        deal_instance_name=deal2.deal_instance_name,
                        set=deal2.set,
                        deal_description = deal2.deal_description,
                        price = deal2.price,
                        currency = deal2.currency,                
                        sales_term = deal2.sales_term,
                        quantity = deal2.quantity                                                                    
                        )    
    for item in deal2.sales_item.all():
        deal3.sales_item.add(item)
    deal3.save()

    messages.success(request, _(u'Username') + ': ' + username + ' - ' + _(u'Password') + ': ' + password + ' ' + _(u'please write down your username and password.'), extra_tags='demo')
    messages.warning(request, _(u'This test account is valid for only for 30 days and will then be deleted.'))    
    return redirect('/')
