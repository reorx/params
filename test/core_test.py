#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from params.core import ParamSet, Field, InvalidParams, FieldErrorInfo
from params.utils import u_


def test_field_null():
    f0 = Field(null=True)

    assert None is f0.validate(None)
    assert None is f0.validate('')
    assert None is f0.validate(u_(''))
    # 0 is not null, only '' and None are
    assert 0 is f0.validate(0)

    f1 = Field(null=False)
    with pytest.raises(ValueError):
        f1.validate(None)
    with pytest.raises(ValueError):
        f1.validate('')
    with pytest.raises(ValueError):
        f1.validate(u_(''))
    assert 0 is f1.validate(0)


def test_field_null_values():
    # change null_values
    f0 = Field(null=True, null_values=(None, 0))

    assert None is f0.validate(None)
    assert None is f0.validate(0)
    assert '' == f0.validate('')

    f1 = f0.spawn(null=False)
    with pytest.raises(ValueError):
        f1.validate(None)
    with pytest.raises(ValueError):
        f1.validate(0)
    assert '' == f0.validate('')


def test_field_choices():
    f0 = Field(null=False, choices=[1, '2', ''])

    # null=False priority is higher than choices
    with pytest.raises(ValueError):
        f0.validate('')

    f0.validate(1)
    f0.validate('2')

    with pytest.raises(ValueError):
        f0.validate('1')
    with pytest.raises(ValueError):
        f0.validate(2)


def test_field_key():
    class P(ParamSet):
        f0 = Field(key='0f')

    d = {'0f': 1, 'f0': 2}
    p = P(d)

    assert p.f0 == d['0f']


def test_field_required():
    class P(ParamSet):
        f0 = Field(required=True)
        f1 = Field()

    d = {'f0': 0, 'f1': 1}
    p = P(d)

    d = {'f1': 1}
    with pytest.raises(InvalidParams):
        p = P(d)
        print(p)


def test_field_default():
    f0_default = 1

    class P(ParamSet):
        f0 = Field(required=True, default=f0_default)
        f1 = Field()

    d = {'f0': 0}
    p = P(d)
    assert p.f0 != f0_default

    d = {'f1': 1}
    # even with default, required still means there should be value pass in
    with pytest.raises(InvalidParams):
        p = P(d)
        print(p)


def test_paramset_to_dict():
    class P(ParamSet):
        f0 = Field()
        f1 = Field(default=1)

    d = {'f0': 0, 'f1': 1, 'f2': 2}
    p = P(d)
    assert set(p.to_dict().keys()) == {'f0', 'f1'}

    d = {'f0': 0}
    p = P(d)
    # default will be involved in to_dict result
    assert set(p.to_dict().keys()) == {'f0', 'f1'}


def test_paramset_has():
    class P(ParamSet):
        f0 = Field()
        f1 = Field(default=1)

    d = {'f0': 0}
    p = P(d)
    assert p.has('f0')
    assert not p.has('f1')


def test_field_convert():
    f = Field()
    f.validate('whatever', convert=True)

    class MultiTypeField(Field):
        value_type = (bool, int)

    f = MultiTypeField()
    f.validate('True', convert=True)
    f.validate('1', convert=True)
    f.validate(False, convert=True)
    f.validate(0, convert=True)


def test_spawn():
    desc = 'foo'
    f = Field(description=desc)
    f1 = f.spawn(required=True)

    assert f.required is False
    assert f1.required is True
    assert f.description == f1.description


def test_invalid_params():
    e = InvalidParams(u'an error')
    print('InvalidParams 1: {}'.format(e))
    e = InvalidParams('an error')
    print('InvalidParams 2: {}'.format(e))
    e = InvalidParams([
        FieldErrorInfo('a', 'foo'),
        FieldErrorInfo('b', 'bar'),
    ])
    print('InvalidParams 3: {}'.format(e))

    with pytest.raises(TypeError):
        InvalidParams(['an error', 'two error'])
    with pytest.raises(TypeError):
        InvalidParams(1)
