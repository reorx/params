# coding: utf-8

import pytest
import datetime
from params.core import ParamSet, Field
from params.fields import (
    StringField,
    RegexField,
    WordField,
    EmailField,
    URLField,
    IntegerField,
    FloatField,
    ListField,
    UUIDStringField,
    DatetimeField,
    BooleanField,
)


value_error_ctx = pytest.raises(ValueError)
type_error_ctx = pytest.raises(TypeError)


def test_string():
    assert None is StringField().validate('')

    f = StringField(null_values=(None, ))
    assert '' == f.validate('')

    with value_error_ctx:
        f.validate(123)

    with value_error_ctx:
        StringField(length=-1)

    f = StringField(length=1, null=False)
    f.validate('a')
    with value_error_ctx:
        f.validate('')

    with type_error_ctx:
        StringField(length=1.1)

    with value_error_ctx:
        StringField(length=(1, ))

    with value_error_ctx:
        StringField(length=(1, 2, 3))

    with value_error_ctx:
        StringField(length=(2, 1))

    with value_error_ctx:
        StringField(length=(-1, 2))

    f = StringField(length=(1, 2), null_values=(None, ))
    f.validate('a')
    f.validate('aa')
    with value_error_ctx:
        f.validate('aaa')


@pytest.mark.parametrize('pattern, match, result', [
    (r'^\w+', 123, False),

    (r'^\w+', 'hell*', True),
    (r'^\w+', '*ello', False),

    (r'\w+$', 'hell*', False),
    (r'\w+$', '*ello', True),

    (r'^\w+$', 'hello', True),
    (r'^\w+$', '*ello', False),
    (r'^\w+$', 'hell*', False)
])
def test_regex(pattern, match, result):
    field = RegexField(pattern=pattern)
    if result:
        assert match == field.validate(match)
    else:
        with value_error_ctx:
            field.validate(match)


def test_words():
    f0 = WordField(null_values=(None, ))
    s = ''
    assert s == f0.validate(s)
    s = 'goodstr'
    assert s == f0.validate(s)
    s = 'goodstr_with_underscore'
    assert s == f0.validate(s)

    with value_error_ctx:
        f0.validate('should not contain space')
    with value_error_ctx:
        f0.validate('miscsymbols*(*^&')

    f1 = WordField(length=(4, 8))
    s = 'four'
    assert s == f1.validate(s)
    s = 'fourfour'
    assert s == f1.validate(s)

    with value_error_ctx:
        f1.validate('s')
    with value_error_ctx:
        f1.validate('longggggg')

    f2 = WordField(null=False)
    with value_error_ctx:
        f2.validate('')


@pytest.mark.parametrize('email, iseq', [
    ('', True),
    ('i@t.cn', True),
    ('longname@longdomain.cn', True),
    ('nor@mal.thr', True),
    ('nor@mal.four', True),
    ('nor@mal.fivee', True),
    ('nor@mal.sixxxx', True),
    ('nor@mal.sevennnn', False),
    ('nor@mal', False),
    ('@mal.com', False),
])
def test_email(email, iseq):
    if iseq:
    f = EmailField(null_values=(None, ))
        assert email == f.validate(email)
    else:
        pytest.raises(ValueError, f.validate, email)


@pytest.mark.parametrize('url, iseq', [
    ('http://hello.com', True),
    ('https://askdjfasdf.asdfasdf.com/', True),
    ('ftp://www.google.com', True),
    ('ssh://www.google.com', False),
    ('http://have.punc*tu*rat@ions.com', False),
    ('http://a.b.c.d.e.f.g.com', True),
    ('http://t.cn/@#$#$(*&', True),
])
def test_url(url, iseq):
    f = URLField()
    if iseq:
        assert url == f.validate(url)
    else:
        pytest.raises(ValueError, f.validate, url)


@pytest.mark.parametrize('kwargs, v, iseq', [
    ({}, 'a', False),
    ({}, '0b', False),
    ({}, '1', False),
    ({}, 10, True),
    ({'min': 3}, 2, False),
    ({'max': 99}, 100, False),
    ({'min': 0, 'max': 10}, -1, False),
    ({'min': 0, 'max': 10}, 0, True),
    ({'min': 0, 'max': 10}, 11, False),
])
def test_int(kwargs, v, iseq):
    check_int(kwargs, v, iseq)


@pytest.mark.parametrize('kwargs, v, iseq', [
    ({}, 'a', False),
    ({}, '1', True),
    ({}, '1.1', False),
])
def test_int_convert(kwargs, v, iseq):
    check_int(kwargs, v, iseq, True)


def check_int(kwargs, v, iseq, convert=False):
    f = IntegerField(**kwargs)
    if iseq:
        assert int(v) == f.validate(v, convert=convert)
    else:
        print(v, f.min, f.max)
        pytest.raises(ValueError, f.validate, v, convert=convert)


def test_float():
    f = FloatField()
    f.validate(1.1)

    f = FloatField(min=0.0, max=2.0)

    f.validate(0)
    f.validate('0', convert=True)
    f.validate(0.0)
    f.validate('0.0', convert=True)
    f.validate(1.1)
    f.validate('1.1', convert=True)
    f.validate(2)
    f.validate(2.0)
    with value_error_ctx:
        f.validate(2.1)
    f.validate(None)


def test_float_convert():
    f = FloatField(min=1.0, max=2.0)

    with value_error_ctx:
        f.validate('a', convert=True)

    f.validate('1', convert=True)

    with value_error_ctx:
        f.validate('3.0', convert=True)

    f.validate('1.0', convert=True)


def test_simple_list():
    list_field = ListField(choices=['a', 'b', 'c'])

    l = ['a']
    assert l == list_field.validate(l)
    l = ['a', 'b', 'c']
    assert l == list_field.validate(l)

    with value_error_ctx:
        list_field.validate(['b', 'c', 'd'])
    with value_error_ctx:
        list_field.validate(['z', 'a', 'b'])


def test_paramset_list():
    class ItemParams(ParamSet):
        a = Field(required=True)

    list_field = ListField(item_class=ItemParams)

    with value_error_ctx:
        list_field.validate(['a', 'b'])

    list_field.validate([{'a': 1}])


def test_type_list_convert():
    list_field = ListField(item_field=IntegerField(min=1, max=9), choices=[1, 2, 3])

    assert [1 == 2, 3], list_field.validate(['1', '2', '3'], convert=True)

    with value_error_ctx:
        list_field.validate(['0', '1', '2'], convert=True)
    with value_error_ctx:
        list_field.validate(['1', '2', '3', '4'], convert=True)
    with value_error_ctx:
        list_field.validate(['a', '2', '3'], convert=True)


@pytest.mark.parametrize('v, iseq', [
    ('asdf', False),
    ('1234', False),
    ('216edfae-19c0-11e3-9e93-10604b8a89ab', True)
])
def test_uuid(v, iseq):
    f = UUIDStringField()
    if iseq:
        assert v == f.validate(v)
    else:
        with value_error_ctx:
            f.validate(v)


def test_datetime():
    with pytest.raises(KeyError):
        f = DatetimeField()

    f = DatetimeField(format='%Y-%m-%d')

    with value_error_ctx:
        f.validate('2011-11-11')

    f.validate(datetime.datetime.now())


def test_datetime_convert():
    f = DatetimeField(format='%Y-%m-%d')

    f.validate('2011-11-11', convert=True)
    with value_error_ctx:
        f.validate('2011-11', convert=True)
    with value_error_ctx:
        f.validate('2011-11-11 10:10', convert=True)
    with value_error_ctx:
        f.validate('2011-13-11', convert=True)

    f1 = DatetimeField(format='%Y-%m-%d', force_convert=True)
    f1.validate('2011-11-11')


def test_boollean():
    with pytest.raises(TypeError):
        f = BooleanField(default='a')

    f = BooleanField()

    v = f.validate(True)
    assert v is True
    v = f.validate(False)
    assert v is False

    # string to bool
    for i in ['True', 'true', '1']:
        v = f.validate(i, convert=True)
        assert v == True
    for i in ['False', 'false', '0']:
        v = f.validate(i, convert=True)
        assert v == False
    with pytest.raises(ValueError):
        v = f.validate('wtf', convert=True)
