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
    'IntegerField',
    'FloatField',
    'ListField',
    'UUIDStringField',
    'DatetimeField',
    'BooleanField',
]


# don't know where to find the <type '_sre.SRE_Pattern'>
_pattern_class = type(re.compile(''))


###############################################################################
# String fields                                                               #
###############################################################################

class StringField(Field):
    value_type = basestring_type

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

    def validate(self, value, **kwargs):
        value = super(StringField, self).validate(value, **kwargs)

        # validate length
        if self.length:
            value = self._validate_length(value)

        return value

    def _convert_type(self, value):
        # because basestring could not be used to convert value, this method is overrided
        if isinstance(value, str):
            try:
                return value.decode('utf8')
            except UnicodeDecodeError:
                raise ValueError('could not convert {} to unicode'.format(repr(value)))
        else:
            return unicode(value)

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

    def validate(self, value, **kwargs):
        value = super(RegexField, self).validate(value, **kwargs)

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


# taken from Django
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

class BaseNumberField(Field):
    """This class is only used as base class"""
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

        super(BaseNumberField, self).__init__(*args, **kwargs)

    def validate(self, value, **kwargs):
        value = super(BaseNumberField, self).validate(value, **kwargs)

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


class IntegerField(BaseNumberField):
    value_type = int


class FloatField(BaseNumberField):
    value_type = float


###############################################################################
# List fields                                                                 #
###############################################################################

class ListField(Field):
    value_type = list

    def __init__(self, *args, **kwargs):
        self.item_field = kwargs.pop('item_field', None)
        super(ListField, self).__init__(*args, **kwargs)

    def _convert_type(self, value):
        if not isinstance(value, list):
            value = [value]

        if self.item_field:
            formatted_value = []
            for i in value:
                try:
                    item_value = self.item_field.validate(i, convert=True)
                except ValueError as e:
                    raise self.format_exc(
                        '{} in list could not be convert to type {}: {}'.format(i, self.item_field, e))
                else:
                    formatted_value.append(item_value)

            value = formatted_value

        return value

    def _validate_type(self, value):
        if not isinstance(value, list):
            raise self.format_exc('Not a list')

        if self.item_field:
            for i in value:
                try:
                    self.item_field.validate(i)
                except ValueError as e:
                    raise self.format_exc(
                        '{} in list is not of type {}: {}'.format(i, self.item_field, e))

    def _validate_choices(self, value):
        bad_values = []
        if self.choices:
            for i in value:
                if i not in self.choices:
                    bad_values.append(i)
        if bad_values:
            raise self.format_exc('%s is/are not allowed' % bad_values)


###############################################################################
# Other type fields                                                           #
###############################################################################

class UUIDStringField(StringField):
    def _validate_type(self, value):
        try:
            uuid.UUID(value)
        except ValueError as e:
            raise self.format_exc('Invalid uuid string: %s' % e)


class DatetimeField(Field):
    value_type = datetime.datetime

    def __init__(self, *args, **kwargs):
        format = kwargs.pop('format', None)
        if not format:
            raise KeyError('`format` argument is required for DatetimeField')
        self.format = format
        super(DatetimeField, self).__init__(*args, **kwargs)

    def _convert_type(self, value):
        try:
            value = datetime.datetime.strptime(value, self.format)
        except ValueError:
            raise self.format_exc(
                'Could not convert {} to datetime object by format {}'.format(
                    value, self.format)
            )
        return value


class BooleanField(Field):
    value_type = bool

    true_strs = ['True', 'true', '1']
    false_strs = ['False', 'false', '0']

    def _convert_type(self, value):
        if isinstance(value, basestring):
            if isinstance(value, unicode):
                value = value.encode('utf8')
            if value in self.true_strs:
                return True
            elif value in self.false_strs:
                return False
            else:
                self.format_exc('could not convert {} to bool'.format(value))
        return value
