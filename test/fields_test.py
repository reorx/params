# coding: utf-8

from nose.tools import assert_raises
from params.fields import (
    RegexField,
    WordField,
    EmailField,
    URLField,
    IntegerField,
    #FloatField,
    ListField,
    UUIDField,
    #DateField,
)


def test_regex():
    pairs = [
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
        field.validate(match)
    else:
        with assert_raises(ValueError):
            field.validate(match)


def test_words():
    f0 = WordField()
    f0.validate('')
    f0.validate('goodstr')
    f0.validate('goodstr_with_underscore')

    with assert_raises(ValueError):
        f0.validate('should not contain space')
    with assert_raises(ValueError):
        f0.validate('miscsymbols*(*^&')

    f1 = WordField(length=(4, 8))
    f1.validate('four')
    f1.validate('fourfour')

    with assert_raises(ValueError):
        f1.validate('s')
    with assert_raises(ValueError):
        f1.validate('longggggg')

    f2 = WordField(null=False)
    with assert_raises(ValueError):
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
        f.validate(email)
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
        f.validate(url)
    else:
        assert_raises(ValueError, f.validate, url)


def test_int():
    pairs = [
        ({}, 'a', False),
        ({}, '0b', False),
        ({}, '1', True),
        ({}, 10, True),
        ({'min': 3}, '2', False),
        ({'max': 99}, '100', False),
        ({'min': 0, 'max': 10}, '-1', False),
        ({'min': 0, 'max': 10}, '0', True),
        ({'min': 0, 'max': 10}, '11', False),
    ]
    for kwargs, v, iseq in pairs:
        yield check_int, kwargs, v, iseq


def check_int(kwargs, v, iseq):
    f = IntegerField(**kwargs)
    if iseq:
        f.validate(v)
    else:
        print v, f.min, f.max
        assert_raises(ValueError, f.validate, v)


def test_simple_list():
    list_field = ListField(choices=['a', 'b', 'c'])

    list_field.validate(['a'])
    list_field.validate(['a', 'b', 'c'])

    with assert_raises(ValueError):
        list_field.validate(['b', 'c', 'd'])
    with assert_raises(ValueError):
        list_field.validate(['z', 'a', 'b'])


def test_type_list():
    list_field = ListField(item_field=IntegerField(min=1, max=9), choices=[1, 2, 3])

    list_field.validate(['1', '2', '3'])

    with assert_raises(ValueError):
        list_field.validate(['0', '1', '2'])
    with assert_raises(ValueError):
        list_field.validate(['1', '2', '3', '4'])
    with assert_raises(ValueError):
        list_field.validate(['a', '2', '3'])


def test_uuid():
    pairs = [
        ('asdf', False),
        ('1234', False),
        ('216edfae-19c0-11e3-9e93-10604b8a89ab', True)
    ]

    for v, iseq in pairs:
        yield check_uuid, v, iseq


def check_uuid(v, iseq):
    f = UUIDField()
    if iseq:
        f.validate(v)
    else:
        with assert_raises(ValueError):
            f.validate(v)
