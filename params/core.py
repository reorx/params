# coding: utf-8

import copy
from .utils import is_empty_string, unicode_copy

__all__ = [
    'InvalidParams',
    'Field',
    'ParamSet',
    'define_params',
]


class InvalidParams(Exception):
    def __init__(self, errors):
        """errors is list contains key, value pairs"""
        if not isinstance(errors, list):
            raise TypeError('errors must be a list')
        self.errors = errors

    def __unicode__(self):
        return u'Invalid params: ' + u'\n'.join(u'{}: {}'.format(k, e) for k, e in self.errors)

    def __str__(self):
        return unicode(self).encode('utf8')


class Field(object):
    name = None
    with_choices = True

    def __init__(
            self, description=None,
            null=True, choices=None,
            key=None, required=False, default=None):
        """
        null, choices, work on Field.validate
        key, required, default, work on ParamSet.validate
        """
        self.description = description  # default message
        self.null = null
        self.choices = choices

        self.key = key
        self.required = required
        self.default = default

    # @property
    # def name(self):
    #     raise NotImplementedError

    def format_exc(self, error_message=None):
        raise ValueError(error_message or self.description)

    def _validate_choices(self, value):
        if value not in self.choices:
            raise self.format_exc(
                'value "%s" is not one of %s' % (value, self.choices))
        return value

    def _validate_type(self, value):
        """Override this method to implement type specified validation"""
        return value

    def validate(self, value):
        if is_empty_string(value) or value is None:
            # If null is allowed, skip other validates
            if self.null:
                return value
            else:
                raise self.format_exc('empty value is not allowed')

        value = self._validate_type(value)

        # Validate choices after type, so that the value has been converted
        if self.with_choices and self.choices:
            self._validate_choices(value)

        return value

    def __get__(self, owner, cls):
        return owner.data.get(self.key, self.default)

    def __set__(self, owner, value):
        raise AttributeError('You can not set value to a param field')

    def spawn(self, **kwargs):
        new = copy.copy(self)
        new.__dict__.update(kwargs)
        # for k, v in kwargs.iteritems():
        #     setattr(new, k, v)
        return new


class ParamSetMeta(type):
    def __new__(cls, name, bases, attrs):
        fields = {}

        # Inherit support
        for base in bases:
            if hasattr(base, '_fields'):
                fields.update(base._fields)

        for k, v in attrs.iteritems():
            # TODO Assert not reserved attribute name
            if isinstance(v, Field):
                v.name = k
                if not v.key:
                    v.key = k
                fields[k] = v
        attrs['_fields'] = fields
        return type.__new__(cls, name, bases, attrs)


class ParamSet(object):
    __metaclass__ = ParamSetMeta

    @classmethod
    def keys(cls):
        return [i.key for i in cls._fields.itervalues()]

    def __init__(self, raw_data, raise_if_invalid=True):
        self._raw_data = unicode_copy(raw_data)
        self.data = {}
        self.errors = []

        self.validate(raise_if_invalid=raise_if_invalid)

    def validate(self, raise_if_invalid=False):
        for name, field in self.__class__._fields.iteritems():
            key = field.key
            if key in self._raw_data:

                value = self._raw_data[key]

                try:
                    value = field.validate(value)
                except ValueError, e:
                    self.errors.append((key, e))
                else:
                    self.data[key] = value
            else:
                if field.required:
                    self.errors.append((key, field.format_exc('%s is required' % key)))
                # elif field.default is not None:
                #     self.data[key] = field.default

        for attr_name in dir(self):
            if attr_name.startswith('validate_'):
                field_name = attr_name[len('validate_'):]

                if field_name in self._fields:
                    field = self._fields[field_name]
                    key = field.key
                    if key in self.data:
                        try:
                            value = getattr(self, attr_name)(self.data[key])
                        except ValueError, e:
                            self.errors.append((key, e))
                        if field.null is not True:
                            assert value is not None, (
                                'Forget to return value after validation?'
                                'Or this is caused by your explicitly returns'
                                'None, which is not allowed in the mechanism.')
                        self.data[key] = value
                else:
                    try:
                        getattr(self, attr_name)()
                    except ValueError, e:
                        self.errors.append(e)
        if raise_if_invalid:
            if self.errors:
                raise InvalidParams(self.errors)

    def kwargs(self, *args):
        d = {}
        for k in args:
            v = getattr(self, k)
            if v is not None:
                d[k] = v
        return d

    def has(self, name):
        return name in self.data

    def to_dict(self, include_none=False):
        """Convert the ParamSet instance to a dict, if `include_none` is True,
        the result will represent both data and schema.
        """
        d = {}
        for f in self.__class__._fields.itervalues():
            value = getattr(self, f.name)
            if value is not None or (value is None and include_none):
                d[f.key] = value
        return d

    def __str__(self):
        return self.__unicode__().encode('utf8')

    def __unicode__(self):
        return u'<%s: %s; errors=%s>' % (
            self.__class__.__name__,
            u','.join([u'%s=%s' % (k, repr(v)) for k, v in self.data.iteritems()]),
            self.errors)


def define_params(kwargs, datatype='form'):
    param_class = type('AutoCreatedParams', (ParamSet, ), kwargs)
    return param_class
