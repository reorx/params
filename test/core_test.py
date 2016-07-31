#!/usr/bin/env python
# -*- coding: utf-8 -*-

from nose.tools import eq_ as equal
from params.core import ParamSet, Field, InvalidParams
from nose.tools import assert_raises


def test_field_null():
    f0 = Field(null=True)

    f0.validate(None)
    f0.validate('')
    f0.validate(0)

    f1 = Field(null=False)
    with assert_raises(ValueError):
        f1.validate(None)
    with assert_raises(ValueError):
        f1.validate('')
    # 0 is not null, only '' and None are
    f1.validate(0)


def test_field_choices():
    f0 = Field(null=False, choices=[1, '2', ''])

    # null=False priority is higher than choices
    with assert_raises(ValueError):
        f0.validate('')

    f0.validate(1)
    f0.validate('2')

    with assert_raises(ValueError):
        f0.validate('1')
    with assert_raises(ValueError):
        f0.validate(2)


def test_field_key():
    class P(ParamSet):
        f0 = Field(key='0f')

    d = {'0f': 1, 'f0': 2}
    p = P(d)

    equal(p.f0, d['0f'])


def test_field_required():
    class P(ParamSet):
        f0 = Field(required=True)
        f1 = Field()

    d = {'f0': 0, 'f1': 1}
    p = P(d)

    d = {'f1': 1}
    with assert_raises(InvalidParams):
        p = P(d)
        print p


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
    with assert_raises(InvalidParams):
        p = P(d)
        print p


def test_paramset_to_dict():
    class P(ParamSet):
        f0 = Field()
        f1 = Field(default=1)

    d = {'f0': 0, 'f1': 1, 'f2': 2}
    p = P(d)
    equal(set(p.to_dict().keys()), {'f0', 'f1'})

    d = {'f0': 0}
    p = P(d)
    # default will be involved in to_dict result
    equal(set(p.to_dict().keys()), {'f0', 'f1'})


def test_paramset_has():
    class P(ParamSet):
        f0 = Field()
        f1 = Field(default=1)

    d = {'f0': 0}
    p = P(d)
    assert p.has('f0')
    assert not p.has('f1')
