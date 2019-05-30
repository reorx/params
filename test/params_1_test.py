# coding: utf-8

import pytest
import params


class FooParams(params.ParamSet):
    bar = params.WordField(choices=['a', 'b', 'c'])
    quz = params.Field()


@pytest.mark.parametrize('data, error_num', [
    ({
        'bar': '',
        'quz': 'QUZ',
    }, 0),
])
def test_param_1(data, error_num):
    params = FooParams(data, raise_if_invalid=False)
    print(error_num, len(params.errors), params.errors)
    assert error_num == len(params.errors)
