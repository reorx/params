# coding: utf-8

import copy
from .utils import unicode_copy


# TODO: use ValueError instead ValidationError

class ValidationError(Exception):
    """
    error occur when validating values
    """
    def __init__(self, description=None, error_message=None):
        self.description = description
        self.error_message = error_message

    def __unicode__(self):
        # return '%s (%s)' % (self.description, self.error_message) if self.error_message else self.description
        return self.description or self.error_message

    def __repr__(self):
        return str(self)


class ParamsInvalidError(Exception):
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

    def __init__(self, description=None, key=None, required=False,
                 length=None, choices=None, default=None, null=True):
        self.description = description  # default message
        self.required = required  # used with ParamSet
        self.choices = choices
        self.key = key
        self.default = default
        self.null = null

        self.min_length = None
        assert length is None or isinstance(length, (int, tuple))
        if isinstance(length, int):
            assert length > 0
        if isinstance(length, tuple):
            assert len(length) == 2 and length[0] > 0
            if length[1] == 0:
                self.min_length = length[0]
            else:
                assert length[1] > length[0]
        self.length = length

    # @property
    # def name(self):
    #     raise NotImplementedError

    def raise_exc(self, error_message=None):
        raise ValidationError(self.description, error_message)

    def _validate_length(self, value):
        length = self.length
        value_len = len(value)

        if isinstance(length, int):
            if value_len != length:
                self.raise_exc(
                    'Length of value should be %s, but %s' %
                    (length, value_len))
        else:
            if self.min_length:
                if value_len < self.min_length:
                    self.raise_exc(
                        'Length of value should be larger than %s' %
                        self.min_length)
            else:
                min, max = length
                if value_len < min or value_len > max:
                    self.raise_exc(
                        'Length should be >= %s and <= %s, but %s' %
                        (min, max, value_len))
        return value

    def _validate_choices(self, value):
        if value not in self.choices:
            self.raise_exc(
                'value "%s" is not one of %s' % (value, self.choices))
        return value

    def _validate_type(self, value):
        """Override this method to implement type specified validation"""
        return value

    def validate(self, value):
        # If null is allowed, skip other validates
        if not value:
            if self.null:
                return value
            else:
                self.raise_exc('empty value is not allowed')

        if self.length:
            self._validate_length(value)

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
                except ValidationError, e:
                    self.errors.append((key, e))
                else:
                    self.data[key] = value
            else:
                if field.required:
                    try:
                        field.raise_exc('%s is required' % key)
                    except ValidationError, e:
                        self.errors.append((key, e))
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
                        except ValidationError, e:
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
                    except ValidationError, e:
                        self.errors.append(e)
        if raise_if_invalid:
            if self.errors:
                raise ParamsInvalidError(self.errors)

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
