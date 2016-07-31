# coding: utf-8

import params
import uuid


class UserParams(params.ParamSet):
    id = params.UUIDField(
        required=True)
    name = params.WordField(
        'name should be a 1~8 length string, and is required',
        required=True, length=(1, 8))
    email = params.EmailField(
        'email should be a valid email format, and is required',
        required=True)
    age = params.IntegerField(
        'age should be a 10~30 int',
        min=10, max=30)


def guuid():
    return str(uuid.uuid4())


def test_param():
    data_pairs = [
        ({
            'id': guuid(),
            'name': 'asuka',
            'email': 'asuka@nerv.com',
        }, 0),
        ({
            'id': '123',  # x
            'name': 'lilith',
            'email': 'l@eva.com',
            'age': 10,
        }, 1),
        ({
            'id': 'a3',  # x
            'name': 'ayanami',
            'email': 'rei@nerv.com',
            'age': 'unknown',  # x
        }, 2),
        ({
            'id': 'b3',  # x
            'name': 'shinjigivebackmyayanami',  # x
            'email': 'yikali@nerv',  # x
            'age': 30,
        }, 3),
        ({
            'id': 'c4',  # x
            'name': 'wtfissooooolong',  # x
            'email': 'eva@god',  # x
            'age': 0,  # x
        }, 4),
        ({}, 3),
    ]

    for data, error_num in data_pairs:
        yield check_param, data, error_num


def check_param(data, error_num):
    params = UserParams(data, raise_if_invalid=False)
    print error_num, len(params.errors), params.errors
    assert error_num == len(params.errors)
