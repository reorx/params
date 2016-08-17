# coding: utf-8

import re
import uuid
import datetime

from .core import Field
from .utils import basestring_type

__all__ = [
    'StringField',
    'RegexField',
    'WordField',
    'EmailField',
    'URLField',
    'NumberField',
    'IntegerField',
    'FloatField',
    'ListField',
    'UUIDField',
    'DateField',
]


# don't know where to find the <type '_sre.SRE_Pattern'>
_pattern_class = type(re.compile(''))


###############################################################################
# String fields                                                               #
###############################################################################

class StringField(Field):
    def __init__(self, *args, **kwargs):
        """
        :params length: int or tuple, eg: 5, (1, 10), (8, 0)
        """
        length = kwargs.pop('length', None)
        self.length = self.format_length(length)
        super(StringField, self).__init__(*args, **kwargs)

    @staticmethod
    def format_length(length):
        if length is None:
            return length

        if isinstance(length, int):
            if length <= 0:
                raise ValueError('length min should be > 0: {}'.format(length))
        elif isinstance(length, tuple):
            if len(length) != 2:
                raise ValueError('length tuple length should be exactly 2: {}'.format(length))
            if length[0] <= 0:
                raise ValueError('length min should be > 0: {}'.format(length[0]))
            if length[0] >= length[1]:
                raise ValueError('lengh min should be < max: {}'.format(length))
        else:
            raise TypeError('length should be int or tuple: {}'.format(repr(length)))
        return length

    def validate(self, value):
        value = super(StringField, self).validate(value)

        # validate length
        if self.length:
            value = self._validate_length(value)

        return value

    def _validate_type(self, value):
        if not isinstance(value, basestring_type):
            raise ValueError('not a string type')
        return value

    def _validate_length(self, value):
        length = self.length
        value_len = len(value)

        if isinstance(length, int):
            if value_len != length:
                raise self.format_exc(
                    'Length of value should be {}, but got {}'.format(length, value_len))
        else:
            min, max = length
            if value_len < min or value_len > max:
                raise self.format_exc(
                    'Length should be >= {} and <= {}, but {}'.format(min, max, value_len))
        return value


class RegexField(StringField):
    def __init__(self, *args, **kwgs):
        # assume pattern is a raw string like r'\n'
        if 'pattern' in kwgs:
            pattern = kwgs.pop('pattern')
            self.regex = re.compile(pattern)
        assert hasattr(self, 'regex'),\
            'regex should be set if no keyword argument pattern passed'
        assert isinstance(self.regex, _pattern_class),\
            'regex should be a compiled pattern'

        super(RegexField, self).__init__(*args, **kwgs)

    def validate(self, value):
        value = super(RegexField, self).validate(value)

        c_value = value
        if not self.regex.search(c_value):
            raise self.format_exc(
                'regex pattern (%s, %s) is not match with value "%s"' %
                (self.regex.pattern, self.regex.flags, c_value))
        return value


class WordField(RegexField):
    """
    >>> v = WordField('should not contain punctuations')
    >>> s = 'oh123,'
    >>> v.validate(s)
    ValueError: should not contain punctuations
    """

    regex = re.compile(r'^[\w]*$')


# take from Django
EMAIL_REGEX = re.compile(
    # dot-atom
    r'(^[-!#$%&\'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&\'*+/=?^_`{}|~0-9A-Z]+)*'
    # quoted-string
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|'
    r'\\[\001-011\013\014\016-\177])*"'
    # domain
    r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$',
    re.IGNORECASE)


class EmailField(RegexField):
    regex = EMAIL_REGEX


URL_REGEX = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'
    r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)


class URLField(RegexField):
    regex = URL_REGEX


###############################################################################
# Number fields                                                               #
###############################################################################

class NumberField(Field):
    def __init__(self, *args, **kwargs):
        min = kwargs.pop('min', None)
        max = kwargs.pop('max', None)
        if min is not None and not isinstance(min, self.value_type):
            raise TypeError('min must be type {}, got {}'.format(self.value_type, type(min)))
        if max is not None and not isinstance(max, self.value_type):
            raise TypeError('max must be type {}, got {}'.format(self.value_type, type(max)))
        if min is not None and max is not None and min >= max:
            raise ValueError('min must < max, got {} ~ {}'.format(min, max))

        self.min = min
        self.max = max

        super(NumberField, self).__init__(*args, **kwargs)

    def validate(self, value):
        value = super(NumberField, self).validate(value)

        # validate min-max
        value = self._validate_min_max(value)

        return value

    def _validate_min_max(self, value):
        if self.min is not None:
            if value < self.min:
                raise self.format_exc('value is too small, min %s' % self.min)
        if self.max is not None:
            if value > self.max:
                raise self.format_exc('vaule is too big, max %s' % self.max)

        return value


class IntegerField(NumberField):
    value_type = int

    def _validate_type(self, value):
        try:
            value = int(value)
        except (ValueError, TypeError):
            raise self.format_exc(
                'could not convert value "%s" into int type' % value)
        return value


class FloatField(NumberField):
    value_type = float

    def _validate_type(self, value):
        try:
            value = float(value)
        except (ValueError, TypeError):
            raise self.format_exc(
                'could not convert value "%s" into float type' % value)
        return value


###############################################################################
# List fields                                                                 #
###############################################################################

class ListField(Field):
    with_choices = False

    def __init__(self, *args, **kwargs):
        self.item_field = kwargs.pop('item_field', None)
        super(ListField, self).__init__(*args, **kwargs)

    def _validate_type(self, value):
        if not isinstance(value, list):
            # raise self.format_exc('Not a list')
            value = [value]

        if self.item_field:
            formatted_value = []
            for i in value:
                formatted_value.append(self.item_field.validate(i))
            value = formatted_value

        bad_values = []
        if self.choices:
            for i in value:
                if i not in self.choices:
                    bad_values.append(i)
        if bad_values:
            raise self.format_exc('%s is/are not allowed' % bad_values)

        return value


###############################################################################
# Other type fields                                                           #
###############################################################################

class UUIDField(Field):
    def _validate_type(self, value):
        try:
            return uuid.UUID(value)
        except ValueError, e:
            raise self.format_exc('Invalid uuid string: %s' % e)


class DateField(Field):
    def __init__(self, *args, **kwargs):
        datefmt = kwargs.pop('datefmt', None)
        assert datefmt, '`datefmt` argument should be passed for DateField'
        self.datefmt = datefmt
        super(DateField, self).__init__(*args, **kwargs)

    def _validate_type(self, value):
        try:
            value = datetime.datetime.strptime(value, self.datefmt)
        except ValueError:
            raise self.format_exc(
                'Could not convert %s to datetime object by format %s' %
                (value, self.datefmt))
        return value
