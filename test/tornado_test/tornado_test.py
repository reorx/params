# coding: utf-8

try:
    import tornado
except ImportError:
    from nose.plugins.skip import SkipTest
    raise SkipTest('no module tornado')

import tornado_app
from tornado.testing import AsyncHTTPTestCase
from nose.tools import assert_raises
import params
from params.contrib.tornado import use_params, use_raw
from params.compat import str_


app_log = 'tornado.application'

param_error_code = 400


class ParamsTest(AsyncHTTPTestCase):
    def get_app(self):
        return tornado_app.get_app()

    def test_tornado_work(self):
        resp = self.fetch('/')
        self.assertEqual(str_(resp.body.strip()), 'hello world')

    def test_get(self):
        resp = self.fetch('/get')
        print('resp 1', resp.body)
        self.assertEqual(resp.code, param_error_code)

        resp = self.fetch('/get?a=1')
        print('resp 2', resp.body)
        self.assertEqual(resp.code, 200)

    def test_post(self):
        url = '/post'
        resp = self.fetch(url, method='POST', body='')
        print('resp', resp.body)
        self.assertEqual(resp.code, param_error_code)

        resp = self.fetch(url, method='POST', body='a=1')
        print('resp', resp.body)
        self.assertEqual(resp.code, 200)

        resp = self.fetch(url, method='POST', body='a=1&b=0')
        print('resp', resp.body)
        self.assertEqual(resp.code, param_error_code)

        resp = self.fetch(url, method='POST', body='a=1&b=b')
        print('resp', resp.body)
        self.assertEqual(resp.code, 200)

    def test_post_json(self):
        url = '/post/json'
        resp = self.fetch(url, method='POST', body='')
        print('resp 1', resp.body)
        self.assertEqual(resp.code, param_error_code)

        resp = self.fetch(url, method='POST', body='a=1')
        print('resp 2', resp.body)
        self.assertEqual(resp.code, param_error_code)

        resp = self.fetch(url, method='POST', body='{"a":"1"}')
        print('resp 3', resp.body)
        self.assertEqual(resp.code, param_error_code)

        resp = self.fetch(url, method='POST', body='{"a":1}')
        print('resp 4', resp.body)
        self.assertEqual(resp.code, 200)

    def test_raw(self):
        url = '/raw'
        resp = self.fetch(url, method='POST', body='')
        print('resp 1', resp.body)
        self.assertEqual(resp.code, param_error_code)

        resp = self.fetch(url, method='POST', body='a=n')
        print('resp 2', resp.body)
        self.assertEqual(resp.code, 200)

        resp = self.fetch(url, method='POST', body='{"a": "n"}')
        print('resp 3', resp.body)
        self.assertEqual(resp.code, param_error_code)

    def test_raw_json(self):
        url = '/raw/json'
        resp = self.fetch(url, method='POST', body='')
        print('resp 1', resp.body)
        self.assertEqual(resp.code, param_error_code)

        resp = self.fetch(url, method='POST', body='a=n')
        print('resp 2', resp.body)
        self.assertEqual(resp.code, param_error_code)

        resp = self.fetch(url, method='POST', body='{"a": "n"}')
        print('resp 3', resp.body)
        self.assertEqual(resp.code, 200)


def test_invalid_http_method():
    from tornado.web import RequestHandler

    with assert_raises(ValueError):
        class DemoHandler(RequestHandler):
            @use_params({
                'a': params.Field(),
            })
            def wtf(self):
                pass
