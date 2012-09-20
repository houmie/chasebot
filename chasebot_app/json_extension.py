from django.core.serializers import serialize
from django.utils.simplejson import loads, JSONEncoder
from django.db.models.query import QuerySet
import simplejson
from django.db.models.base import Model

class DjangoJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, QuerySet):
            # `default` must return a python serializable
            # structure, the easiest way is to load the JSON
            # string produced by `serialize` and return it
            return loads(serialize('json', obj))
        return JSONEncoder.default(self,obj)

# partial function, we can now use dumps(my_dict) instead
# of dumps(my_dict, cls=DjangoJSONEncoder)
# dumps = curry(dumps, cls=DjangoJSONEncoder)


def toJSON(obj):
    if isinstance(obj, QuerySet):
        return simplejson.dumps(obj, cls=DjangoJSONEncoder)
    if isinstance(obj, Model):
        #do the same as above by making it a queryset first
        set_obj = [obj]
        set_str = simplejson.dumps(simplejson.loads(serialize('json', set_obj)))
        #eliminate brackets in the beginning and the end 
        #str_obj = set_str[1:len(set_str)-2]
    return set_str