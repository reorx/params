# coding: utf-8

import re
import uuid
import datetime

from .core import Field


# don't know where to find the <type '_sre.SRE_Pattern'>
_pattern_class = type(re.compile(''))


class RegexField(Field):
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

    def _validate_type(self, value):
        # Equate the type of regex pattern and the checking value
        pattern_type = type(self.regex.pattern)
        c_value = value
        if not isinstance(value, pattern_type):
            try:
                c_value = pattern_type(value)
            except Exception, e:
                raise self.format_exc(
                    'value could not be converted into type "%s"'
                    'of regex pattern, error: %s' % (pattern_type, e))
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

    regex = re.compile(r'^[\w]+$')


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


class IntegerField(Field):
    def __init__(self, *args, **kwargs):
        min = kwargs.pop('min', None)
        max = kwargs.pop('max', None)
        if min is not None:
            assert isinstance(min, int)
        if max is not None:
            assert isinstance(max, int)
        if min is not None and max is not None:
            assert min <= max

        self.min = min
        self.max = max

        super(IntegerField, self).__init__(*args, **kwargs)

    def _validate_type(self, value):
        try:
            value = int(value)
        except (ValueError, TypeError):
            raise self.format_exc(
                'could not convert value "%s" into int type' % value)

        if self.min:
            if value < self.min:
                raise self.format_exc('value is too small, min %s' % self.min)
        if self.max:
            if value > self.max:
                raise self.format_exc('vaule is too big, max %s' % self.max)

        return value


# TODO
class FloatField(Field):
    pass


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


class UUIDField(Field):
    def _validate_type(self, value):
        try:
            return uuid.UUID(value)
        except ValueError, e:
            raise self.format_exc('Invalid uuid string: %s' % e)


# TODO
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
