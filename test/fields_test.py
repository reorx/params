# coding: utf-8

import datetime
from nose.tools import eq_ as equal
from nose.tools import assert_raises
from params.fields import (
    #Field,
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


value_error_ctx = assert_raises(ValueError)
type_error_ctx = assert_raises(TypeError)


def test_string():

    f = StringField()
    f.validate('')

    with value_error_ctx:
        f.validate(123)

    with value_error_ctx:
        StringField(length=-1)

    f = StringField(length=1)
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

    f = StringField(length=(1, 2))
    f.validate('a')
    f.validate('aa')
    with value_error_ctx:
        f.validate('aaa')


def test_regex():
    pairs = [
        (r'^\w+', 123, False),

        (r'^\w+', 'hell*', True),
        (r'^\w+', '*ello', False),

        (r'\w+$', 'hell*', False),
        (r'\w+$', '*ello', True),

        (r'^\w+$', 'hello', True),
        (r'^\w+$', '*ello', False),
        (r'^\w+$', 'hell*', False)
    ]

    for pattern, match, result in pairs:
        yield check_regex, pattern, match, result


def check_regex(pattern, match, result):
    field = RegexField(pattern=pattern)
    if result:
        equal(match, field.validate(match))
    else:
        with value_error_ctx:
            field.validate(match)


def test_words():
    f0 = WordField()
    s = ''
    equal(s, f0.validate(s))
    s = 'goodstr'
    equal(s, f0.validate(s))
    s = 'goodstr_with_underscore'
    equal(s, f0.validate(s))

    with value_error_ctx:
        f0.validate('should not contain space')
    with value_error_ctx:
        f0.validate('miscsymbols*(*^&')

    f1 = WordField(length=(4, 8))
    s = 'four'
    equal(s, f1.validate(s))
    s = 'fourfour'
    equal(s, f1.validate(s))

    with value_error_ctx:
        f1.validate('s')
    with value_error_ctx:
        f1.validate('longggggg')

    f2 = WordField(null=False)
    with value_error_ctx:
        f2.validate('')


def test_email():
    pairs = [
        ('i@t.cn', True),
        ('longname@longdomain.cn', True),
        ('nor@mal.thr', True),
        ('nor@mal.four', True),
        ('nor@mal.fivee', True),
        ('nor@mal.sixxxx', True),
        ('nor@mal.sevennnn', False),
        ('nor@mal', False),
        ('@mal.com', False),
    ]
    for email, iseq in pairs:
        yield check_email, email, iseq


def check_email(email, iseq):
    f = EmailField()
    if iseq:
        equal(email, f.validate(email))
    else:
        assert_raises(ValueError, f.validate, email)


def test_url():
    pairs = [
        ('http://hello.com', True),
        ('https://askdjfasdf.asdfasdf.com/', True),
        ('ftp://www.google.com', True),
        ('ssh://www.google.com', False),
        ('http://have.punc*tu*rat@ions.com', False),
        ('http://a.b.c.d.e.f.g.com', True),
        ('http://t.cn/@#$#$(*&', True),
    ]
    for url, iseq in pairs:
        yield check_url, url, iseq


def check_url(url, iseq):
    f = URLField()
    if iseq:
        equal(url, f.validate(url))
    else:
        assert_raises(ValueError, f.validate, url)


def test_int():
    pairs = [
        ({}, 'a', False),
        ({}, '0b', False),
        ({}, '1', False),
        ({}, 10, True),
        ({'min': 3}, 2, False),
        ({'max': 99}, 100, False),
        ({'min': 0, 'max': 10}, -1, False),
        ({'min': 0, 'max': 10}, 0, True),
        ({'min': 0, 'max': 10}, 11, False),
    ]
    for kwargs, v, iseq in pairs:
        yield check_int, kwargs, v, iseq


def test_int_convert():
    pairs = [
        ({}, 'a', False),
        ({}, '1', True),
        ({}, '1.1', False),
    ]
    for kwargs, v, iseq in pairs:
        yield check_int, kwargs, v, iseq, True


def check_int(kwargs, v, iseq, convert=False):
    f = IntegerField(**kwargs)
    if iseq:
        equal(int(v), f.validate(v, convert=convert))
    else:
        print v, f.min, f.max
        assert_raises(ValueError, f.validate, v, convert=convert)


def test_float():
    f = FloatField()
    # with value_error_ctx:
    #     f.validate(1)

    f.validate(1.1)

    with type_error_ctx:
        FloatField(min=1)

    with type_error_ctx:
        FloatField(max=2)


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
    equal(l, list_field.validate(l))
    l = ['a', 'b', 'c']
    equal(l, list_field.validate(l))

    with value_error_ctx:
        list_field.validate(['b', 'c', 'd'])
    with value_error_ctx:
        list_field.validate(['z', 'a', 'b'])


def test_type_list_convert():
    list_field = ListField(item_field=IntegerField(min=1, max=9), choices=[1, 2, 3])

    equal([1, 2, 3], list_field.validate(['1', '2', '3'], convert=True))

    with value_error_ctx:
        list_field.validate(['0', '1', '2'], convert=True)
    with value_error_ctx:
        list_field.validate(['1', '2', '3', '4'], convert=True)
    with value_error_ctx:
        list_field.validate(['a', '2', '3'], convert=True)


def test_uuid():
    pairs = [
        ('asdf', False),
        ('1234', False),
        ('216edfae-19c0-11e3-9e93-10604b8a89ab', True)
    ]

    for v, iseq in pairs:
        yield check_uuid, v, iseq


def check_uuid(v, iseq):
    f = UUIDStringField()
    if iseq:
        equal(v, f.validate(v))
    else:
        with value_error_ctx:
            f.validate(v)


def test_datetime():
    with assert_raises(KeyError):
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
    with assert_raises(TypeError):
        f = BooleanField(default='a')

    f = BooleanField()

    v = f.validate(True)
    assert v is True
    v = f.validate(False)
    assert v is False

    # string to bool
    for i in ['True', 'true', '1']:
        v = f.validate(i, convert=True)
        equal(v, True)
    for i in ['False', 'false', '0']:
        v = f.validate(i, convert=True)
        equal(v, False)
    with assert_raises(ValueError):
        v = f.validate('wtf', convert=True)
