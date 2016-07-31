#!/usr/bin/env python
# -*- coding: utf-8 -*-

from nose.tools import eq_ as equal
from params.core import ParamSet, Field


class FakeParams(ParamSet):
    id = params.IntegerField('wat are you?', required=True, min=0)
    name = params.WordField('name should be a 1~8 length string, and is required', required=True, length=(1, 8))
    email = params.EmailField('email should be a valid email format, and is required', required=True)
    content = params.Field('content should be a 1~20 length string', length=(1, 20))


def test_param():
    data_pairs = [
        ({
            'id': '0',
            'name': 'asuka',
            'email': 'asuka@nerv.com'
        }, 0),
        ({
            'id': '2',
            'name': 'lilith',
            'email': 'l@eva.com',
            'content': 'with adon'
        }, 0),
        ({
            'id': 'a3',
            'name': 'ayanami',
            'email': 'rei@nerv.com'
        }, 1),
        ({
            'id': 'b3',
            'name': 'shinjigivebackmyayanami',
            'email': 'yikali@nerv.com'
        }, 2),
        ({
            'id': 'c4',
            'name': 'E V A',
            'email': 'eva@god',
            'content': 'Gainax launched a project to create a movie ending for the series in 1997. The company first released Death and Rebirth on March 15'
        }, 4),
        ({}, 3),
        ({
            'id': 'd5'
        }, 3),
        ({
            'id': '999'
        }, 2),
        ({
            'content': 'The project to complete the final episodes (retelling episodes 25 and 26 of the series) was completed later in 1997 and released on July 19 as The End of Evangelion. '
        }, 4)
    ]

    for data, error_num in data_pairs:
        yield check_param, data, error_num


def check_param(data, error_num):
    params = FakeParams(data, raise_if_invalid=False)
    print error_num, len(params.errors), params.errors
    assert error_num == len(params.errors)
