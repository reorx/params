# coding: utf-8

import tornado_app
from tornado.testing import AsyncHTTPTestCase


app_log = 'tornado.application'

param_error_code = 400


class ParamsTest(AsyncHTTPTestCase):
    def get_app(self):
        return tornado_app.get_app()

    def test_tornado_work(self):
        resp = self.fetch('/')
        self.assertEqual(resp.body.strip(), 'hello world')

    def test_get(self):
        resp = self.fetch('/get')
        print 'resp', resp.body
        self.assertEqual(resp.code, param_error_code)

        resp = self.fetch('/get?a=1')
        self.assertEqual(resp.code, 200)

    def test_post(self):
        url = '/post'
        resp = self.fetch(url, method='POST', body='')
        print 'resp', resp.body
        self.assertEqual(resp.code, param_error_code)

        resp = self.fetch(url, method='POST', body='a=1')
        print 'resp', resp.body
        self.assertEqual(resp.code, 200)

        resp = self.fetch(url, method='POST', body='a=1&b=0')
        print 'resp', resp.body
        self.assertEqual(resp.code, param_error_code)

        resp = self.fetch(url, method='POST', body='a=1&b=2')
        print 'resp', resp.body
        self.assertEqual(resp.code, 200)

    def test_post_json(self):
        url = '/post/json'
        resp = self.fetch(url, method='POST', body='')
        print 'resp 1', resp.body
        self.assertEqual(resp.code, param_error_code)

        resp = self.fetch(url, method='POST', body='a=1')
        print 'resp 2', resp.body
        self.assertEqual(resp.code, param_error_code)

        resp = self.fetch(url, method='POST', body='{"a":"1"}')
        print 'resp 3', resp.body
        self.assertEqual(resp.code, 200)

        resp = self.fetch(url, method='POST', body='{"a":1}')
        print 'resp 4', resp.body
        self.assertEqual(resp.code, param_error_code)

    def test_raw(self):
        url = '/raw'
        resp = self.fetch(url, method='POST', body='')
        print 'resp 1', resp.body
        self.assertEqual(resp.code, param_error_code)

        resp = self.fetch(url, method='POST', body='a=n')
        print 'resp 2', resp.body
        self.assertEqual(resp.code, 200)

        resp = self.fetch(url, method='POST', body='{"a": "n"}')
        print 'resp 3', resp.body
        self.assertEqual(resp.code, param_error_code)

    def test_raw_json(self):
        url = '/raw/json'
        resp = self.fetch(url, method='POST', body='')
        print 'resp 1', resp.body
        self.assertEqual(resp.code, param_error_code)

        resp = self.fetch(url, method='POST', body='a=n')
        print 'resp 2', resp.body
        self.assertEqual(resp.code, param_error_code)

        resp = self.fetch(url, method='POST', body='{"a": "n"}')
        print 'resp 3', resp.body
        self.assertEqual(resp.code, 200)
