from django.db.models import F, Q, Field
from django.db.models.fields.related import ReverseSingleRelatedObjectDescriptor
from django.utils.functional import cached_property


def _get_value_or_field(other):
    if isinstance(other, NaturalQueryDescriptor):
        other = F(other.name)
    return other


def create_query_object(constructed_lookup, other):
    return Q(**{constructed_lookup: other})


class NaturalQueryDescriptorBase(object):
    def __init__(self, name):
        if isinstance(name, Field):
            self.name = name.name
        else:
            self.name = name

    def _transform_operator_to_query_object(self, lookup_type, other):
        other = _get_value_or_field(other)
        constructed_lookup = self._construct_lookup(lookup_type)
        return create_query_object(constructed_lookup, other)

    def _construct_lookup(self, lookup_type):
        return '%s__%s' % (self.name, lookup_type)


class NaturalQueryDescriptor(NaturalQueryDescriptorBase):
    def __eq__(self, other):
        return self._transform_operator_to_query_object('exact', other)

    def __gt__(self, other):
        return self._transform_operator_to_query_object('gt', other)

    def __ge__(self, other):
        return self._transform_operator_to_query_object('gte', other)

    def __lt__(self, other):
        return self._transform_operator_to_query_object('lt', other)

    def __le__(self, other):
        return self._transform_operator_to_query_object('lte', other)

    def __ne__(self, other):
        return ~self._transform_operator_to_query_object('exact', other)

    def __invert__(self):
        return ~Q(self.name)

    def __add__(self, other):
        return F(self.name) + other

    def __sub__(self, other):
        return F(self.name) - other

    def __mul__(self, other):
        return F(self.name) * other

    def __div__(self, other):
        return F(self.name) / other

    def __truediv__(self, other):
        return F(self.name) / other

    def __radd__(self, other):
        return F(self.name) + other

    def __rsub__(self, other):
        return other - F(self.name)

    def __rmul__(self, other):
        return F(self.name) * other

    def __rdiv__(self, other):
        return other / F(self.name)

    def __pow__(self, power, modulo=None):
        return pow(F(self.name), power, modulo)

    def __mod__(self, other):
        return F(self.name) % other

    def __rmod__(self, other):
        return other % F(self.name)

    def iexact(self, other):
        return self._transform_operator_to_query_object('iexact', other)

    def contains(self, other):
        return self._transform_operator_to_query_object('contains', other)

    def icontains(self, other):
        return self._transform_operator_to_query_object('icontains', other)

    def startswith(self, other):
        return self._transform_operator_to_query_object('startswith', other)

    def istartswith(self, other):
        return self._transform_operator_to_query_object('istartswith', other)

    def endswith(self, other):
        return self._transform_operator_to_query_object('endswith', other)

    def iendswith(self, other):
        return self._transform_operator_to_query_object('iendswith', other)

    def search(self, other):
        return self._transform_operator_to_query_object('search', other)

    def regex(self, other):
        return self._transform_operator_to_query_object('regex', other)

    def iregex(self, other):
        return self._transform_operator_to_query_object('iregex', other)

    def in_values(self, *args):
        args = list(args)
        for i, arg in enumerate(args):
            if isinstance(arg, NaturalQueryDescriptor):
                args[i] = F(arg.name)
        args = tuple(args)
        return self._transform_operator_to_query_object('in', args)

    def between(self, low, high):
        if isinstance(low, NaturalQueryDescriptor):
            low = F(low.name)
        if isinstance(high, NaturalQueryDescriptor):
            high = F(high.name)
        return self._transform_operator_to_query_object('range', (low, high))


class ReverseSingleRelatedObjectNaturalQueryDescriptor(ReverseSingleRelatedObjectDescriptor, NaturalQueryDescriptor):
    pass


class PrimaryKeyNaturalQueryDescriptor(NaturalQueryDescriptor):
    def __init__(self):
        super(PrimaryKeyNaturalQueryDescriptor, self).__init__('pk')

    def __get__(self, instance, owner):
        if not instance:
            return self

        return instance._get_pk_val()

    def __set__(self, instance, value):
        return instance._set_pk_val(value)


class DatePartNaturalQueryDescriptor(NaturalQueryDescriptorBase):
    def __init__(self, name, date_part):
        super(DatePartNaturalQueryDescriptor, self).__init__(name)

        self.date_part = date_part

    def __eq__(self, other):
        return self._transform_operator_to_query_object(self.date_part, other)

    def __ne__(self, other):
        return ~self._transform_operator_to_query_object(self.date_part, other)

    def __add__(self, other):
        return F(self._construct_lookup(self.date_part)) + other

    def __sub__(self, other):
        return F(self._construct_lookup(self.date_part)) - other

    def __mul__(self, other):
        return F(self._construct_lookup(self.date_part)) * other

    def __div__(self, other):
        return F(self._construct_lookup(self.date_part)) / other

    def __truediv__(self, other):
        return F(self._construct_lookup(self.date_part)) / other

    def __radd__(self, other):
        return F(self._construct_lookup(self.date_part)) + other

    def __rsub__(self, other):
        return other - F(self._construct_lookup(self.date_part))

    def __rmul__(self, other):
        return F(self._construct_lookup(self.date_part)) * other

    def __rdiv__(self, other):
        return other / F(self._construct_lookup(self.date_part))

    def __pow__(self, power, modulo=None):
        return pow(F(self._construct_lookup(self.date_part)), power, modulo)

    def __mod__(self, other):
        return F(self._construct_lookup(self.date_part)) % other

    def __rmod__(self, other):
        return other % F(self._construct_lookup(self.date_part))


class DateNaturalQueryDescriptor(NaturalQueryDescriptor):
    def _construct_natural_query_descriptor_for_date_part(self, date_part):
        return DatePartNaturalQueryDescriptor(self.name, date_part)

    @cached_property
    def year(self):
        return self._construct_natural_query_descriptor_for_date_part('year')

    @cached_property
    def month(self):
        return self._construct_natural_query_descriptor_for_date_part('month')

    @cached_property
    def day(self):
        return self._construct_natural_query_descriptor_for_date_part('day')

    @cached_property
    def week_day(self):
        return self._construct_natural_query_descriptor_for_date_part('week_day')


class DateTimeNaturalQueryDescriptor(DateNaturalQueryDescriptor):
    @cached_property
    def hour(self):
        return self._construct_natural_query_descriptor_for_date_part('hour')

    @cached_property
    def minute(self):
        return self._construct_natural_query_descriptor_for_date_part('minute')

    @cached_property
    def second(self):
        return self._construct_natural_query_descriptor_for_date_part('second')