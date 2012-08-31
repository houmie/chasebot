from django.forms.widgets import DateInput

class cb_DateInput(DateInput):
    input_type = 'date'
    
class cb_DateTimeInput(DateInput):
    input_type = 'datetime'
