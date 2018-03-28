# coding: utf-8

import params
import uuid
from nose.tools import assert_raises


userdb = ['asuka', 'lilith', 'ayanami']


class UserParams(params.ParamSet):
    id = params.UUIDStringField(
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
    is_staff = params.BooleanField(default=True)
    is_admin = params.BooleanField()

    def validate_name(self, value):
        if value not in userdb:
            raise ValueError('user not in db')
        return value

    def validate_name_with_email(self):
        """name must be in email"""
        name = self.data.get('name')
        email = self.data.get('email')
        if not name or not email:
            return

        if name not in email:
            raise ValueError('name must be in email')


def guuid():
    return str(uuid.uuid4())


def test_param():
    data_pairs = [
        ({
            'id': guuid(),
            'name': u'asuka',
            'email': 'asuka@nerv.com',
        }, 0),
        ({
            'id': '123',  # x
            'name': 'lilith',
            'email': u'lilith001@eva.com',
            'age': 10,
        }, 1),
        ({
            'id': 'a3',  # x
            'name': 'ayanami',
            'email': 'rei@nerv.com',  # x
            'age': 'unknown',  # x
        }, 3),
        ({
            'id': 'b3',  # x
            'name': 'hikali',  # x
            'email': 'hikali@nerv',  # x
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
    print(error_num, len(params.errors), params.errors)
    assert error_num == len(params.errors)


def test_param_boollean():
    d = {
        'id': guuid(),
        'name': u'asuka',
        'email': 'asuka@nerv.com',
    }
    p = UserParams(d)
    assert p.is_staff is True
    assert p.is_admin is None

    d = {
        'id': guuid(),
        'name': u'asuka',
        'email': 'asuka@nerv.com',
        'is_staff': False,
        'is_admin': True,
    }
    p = UserParams(d)
    assert p.is_staff is False
    assert p.is_admin is True


def test_wrong_validate_function():
    class DemoParams(params.ParamSet):
        a = params.Field(null=False)

        def validate_a(self, value):
            pass

    DemoParams({})

    with assert_raises(AssertionError):
        DemoParams({'a': 1})


def test_keys():
    class DemoParams(params.ParamSet):
        a_b = params.Field(key='a-b')

    assert DemoParams.keys() == ['a-b']


def test_setattr():
    class DemoParams(params.ParamSet):
        a = params.Field()

    p = DemoParams({})
    with assert_raises(AttributeError):
        p.a = 1

    p.whatever = 2
