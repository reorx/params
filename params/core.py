# coding: utf-8

import copy
from six import with_metaclass
from .utils import unicode_copy, to_unicode, basestring_type
from .compat import PY2, unicode_ as u_

__all__ = [
    'InvalidParams',
    'Field',
    'ParamSet',
    'define_params',
]


default_null_values = ('', u_(''), None, )


class FieldErrorInfo(object):
    key = None
    message = None

    def __init__(self, key, message):
        self.key = key
        self.message = message

    def __unicode__(self):
        if self.key:
            return u_('{}: {}').format(self.key, self.message)
        else:
            return u_(self.message)

    if PY2:
        def __str__(self):
            return self.__unicode__().encode('utf8')
    else:
        def __str__(self):
            return self.__unicode__()

    def __repr__(self):
        return 'FieldErrorInfo(key={} message={})'.format(self.key, self.message)


class InvalidParams(Exception):
    def __init__(self, errors):
        """errors is list contains key, value pairs"""
        if isinstance(errors, list):
            for i in errors:
                if not isinstance(i, FieldErrorInfo):
                    raise TypeError('errors item must be instance of FieldErrorInfo, got {} ({})'.format(type(i), i))
        # Deprecated, this block only exists for compatibility,
        # you should not pass str as errors
        elif isinstance(errors, basestring_type):
            errors = [
                FieldErrorInfo(None, to_unicode(errors))
            ]
        else:
            raise TypeError('errors must be list or str')
        self.errors = errors

    def __unicode__(self):
        if isinstance(self.errors, basestring_type):
            return self.errors
        else:
            return u_('\n').join(e.__unicode__() for e in self.errors)

    if PY2:
        def __str__(self):
            return self.__unicode__().encode('utf8')
    else:
        def __str__(self):
            return self.__unicode__()


class Field(object):
    name = None
    value_type = None
    extra_validation_methods = []

    def __init__(
            self, description=None,
            null=True, choices=None,
            key=None, required=False, default=None, force_convert=False,
            null_values=default_null_values,
    ):
        """
        null, choices, work on Field.validate
        key, required, default, work on ParamSet.validate
        """
        self.description = description  # default message
        self.null = null
        if not isinstance(null_values, tuple):
            raise TypeError('null_values must be a tuple')
        self.null_values = null_values
        self.choices = choices

        self.key = key
        self.required = required
        if self.value_type is not None and default is not None:
            if not isinstance(default, self.value_type):
                raise TypeError('default value should be of type {}'.format(self.value_type))
        self.default = default
        self.force_convert = force_convert

    # @property
    # def name(self):
    #     raise NotImplementedError

    def format_exc(self, error_message=None, error_class=ValueError):
        return error_class(self.description or error_message)

    def _validate_choices(self, value):
        if value not in self.choices:
            raise self.format_exc(
                'value "%s" is not one of %s' % (value, self.choices))

    def _validate_type(self, value):
        """Override this method to implement type specified validation"""
        if self.value_type is None:
            return

        if not isinstance(value, self.value_type):
            raise TypeError('{} is not of type {}'.format(value, self.value_type))

    def _convert_type(self, value):
        """Override this method to implement type specified conversion"""
        if self.value_type is None:
            return value

        if isinstance(self.value_type, tuple):
            types = self.value_type
        else:
            types = (self.value_type, )

        success = False
        error = ''
        conv_value = value
        for typ in types:
            try:
                conv_value = typ(value)
            except Exception as e:
                error = '{}; {}'.format(e, error)
            else:
                success = True
                break

        if success:
            return conv_value
        else:
            raise TypeError('could not convert {} to type {}: {}'.format(value, self.value_type, error))

    def is_null(self, value):
        return value in self.null_values

    def validate(self, value, convert=False):
        if self.is_null(value):
            # If null is allowed, skip other validates
            if self.null:
                return None
            else:
                raise self.format_exc('empty value {!r} is not allowed'.format(value))

        if convert or self.force_convert:
            value = self._convert_type(value)

        self._validate_type(value)

        # Validate choices after type, so that the value has been converted
        if self.choices:
            self._validate_choices(value)

        for method_name in self.extra_validation_methods:
            getattr(self, method_name)(value)

        return value

    def __get__(self, owner, cls):
        return owner.data.get(self.key, self.default)

    def __set__(self, owner, value):
        raise AttributeError('You can not set value to a param field')

    def spawn(self, **kwargs):
        new = copy.copy(self)
        # set key to None and init key by each field
        new.key = None
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

        for k, v in attrs.items():
            # TODO Assert not reserved attribute name
            if isinstance(v, Field):
                v.name = k
                if not v.key:
                    v.key = k
                fields[k] = v
        attrs['_fields'] = fields
        return type.__new__(cls, name, bases, attrs)


class ParamSet(with_metaclass(ParamSetMeta, object)):
    convert_fields = False
    no_additional_keys = False

    @classmethod
    def keys(cls):
        return [i.key for i in cls._fields.values()]

    def __init__(self, raw_data, raise_if_invalid=True, convert_fields=False):
        self._raw_data = unicode_copy(raw_data)
        self.data = {}
        self.errors = []
        self.convert_fields = convert_fields

        self.validate(raise_if_invalid=raise_if_invalid)

    def validate(self, raise_if_invalid=True):
        if not isinstance(self._raw_data, dict):
            raise InvalidParams('params data is not a dict')

        field_keys = []
        for name, field in self.__class__._fields.items():
            key = field.key
            field_keys.append(key)
            if key in self._raw_data:

                value = self._raw_data[key]

                try:
                    value = field.validate(value, convert=self.convert_fields)
                except (TypeError, ValueError) as e:
                    self.errors.append(FieldErrorInfo(key, str(e)))
                else:
                    self.data[key] = value
            else:
                if field.required:
                    self.errors.append(FieldErrorInfo(key, field.format_exc('%s is required' % key)))
                # elif field.default is not None:
                #     self.data[key] = field.default

        for k in self._raw_data:
            if self.no_additional_keys and k not in field_keys:
                self.errors.append(FieldErrorInfo(k, 'additional key {} is not allowed'.format(k)))

        # first loop, validate each field independently
        non_field_validate_funcs = []
        for attr_name in dir(self):
            if attr_name.startswith('validate_'):
                field_name = attr_name[len('validate_'):]

                if field_name in self._fields:
                    field = self._fields[field_name]
                    key = field.key
                    if key in self.data:
                        try:
                            value = getattr(self, attr_name)(self.data[key])
                        except ValueError as e:
                            self.errors.append(FieldErrorInfo(key, str(e)))
                        if field.null is not True:
                            assert value is not None, (
                                'Forget to return value after validation?'
                                'Or this is caused by your explicitly returns'
                                'None, which is not allowed in the mechanism.')
                        self.data[key] = value
                else:
                    non_field_validate_funcs.append(getattr(self, attr_name))

        # second loop, validate logic functions
        for func in non_field_validate_funcs:
            try:
                func()
            except ValueError as e:
                self.errors.append(FieldErrorInfo(None, str(e)))

        if raise_if_invalid:
            if self.errors:
                raise InvalidParams(self.errors)

    def has(self, name):
        return name in self.data

    def to_dict(self, include_none=False):
        """Convert the ParamSet instance to a dict, if `include_none` is True,
        the result will represent both data and schema.
        """
        d = {}
        for f in self.__class__._fields.values():
            value = getattr(self, f.name)
            if value is not None or (value is None and include_none):
                d[f.key] = value
        return d

    def get_raw(self, key, default=NotImplemented):
        if default is NotImplemented:
            return self._raw_data[key]
        return self._raw_data.get(key, default)

    def __unicode__(self):
        return u_('<%s: %s; errors=%s>') % (
            self.__class__.__name__,
            u_(',').join([u_('%s=%s') % (k, repr(v)) for k, v in self.data.items()]),
            self.errors)

    if PY2:
        def __str__(self):
            return self.__unicode__().encode('utf8')
    else:
        def __str__(self):
            return self.__unicode__()


def define_params(kwargs, datatype='form'):
    param_class = type('AutoCreatedParams', (ParamSet, ), kwargs)
    return param_class
