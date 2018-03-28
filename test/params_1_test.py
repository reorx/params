# coding: utf-8

import params
from nose.tools import assert_raises


class FooParams(params.ParamSet):
    bar = params.WordField(choices=['a', 'b', 'c'])
    quz = params.Field()


def test_param_1():
    data_pairs = [
        ({
            'bar': '',
            'quz': 'QUZ',
        }, 0),
    ]

    for data, error_num in data_pairs:
        yield check_param, data, error_num


def check_param(data, error_num):
    params = FooParams(data, raise_if_invalid=False)
    print(error_num, len(params.errors), params.errors)
    assert error_num == len(params.errors)
