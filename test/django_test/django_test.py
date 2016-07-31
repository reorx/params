# coding: utf-8

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'djapp.settings'
import django
django.setup()

import json
from django.test import Client
from nose.tools import eq_ as equal
from nose.tools import assert_raises
from params import InvalidParams


def test_client():
    c = Client()
    resp = c.get('/')
    equal(resp.content, 'GET')


def test_funcview():
    c = Client()

    with assert_raises(InvalidParams):
        c.get('/func')

    resp = c.get('/func?a=1')
    print resp.content


def test_classview():
    c = Client()

    with assert_raises(InvalidParams):
        c.get('/class')

    resp = c.get('/class?a=1')
    print resp.content


def test_jsonview():
    c = Client()

    # GET on json=True is not allowed
    with assert_raises(ValueError):
        c.get('/json')

    d = {'a': 1}
    with assert_raises(InvalidParams):
        c.post('/json', d)

    resp = c.post('/json', json.dumps(d), content_type='application/json')
    print resp.content
