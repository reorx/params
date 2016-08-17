# coding: utf-8

import tornado_app
from tornado.testing import AsyncHTTPTestCase, ExpectLog


app_log = 'tornado.application'


class ParamsTest(AsyncHTTPTestCase):
    def get_app(self):
        return tornado_app.get_app()

    def test_tornado_work(self):
        resp = self.fetch('/')
        self.assertEqual(resp.body.strip(), 'hello world')

    def test_get(self):
        with ExpectLog(app_log, 'Uncaught exception', required=True):
            resp = self.fetch('/get')
            print 'resp', resp.body

        resp = self.fetch('/get?a=1')
        self.assertEqual(resp.code, 200)

    def test_post(self):
        with ExpectLog(app_log, 'Uncaught exception', required=True):
            resp = self.fetch('/post', method='POST', body='')
            print 'resp', resp.body

        resp = self.fetch('/post', method='POST', body='a=1')
        print 'resp', resp.body
        self.assertEqual(resp.code, 200)

        with ExpectLog(app_log, 'Uncaught exception', required=True):
            resp = self.fetch('/post', method='POST', body='a=1&b=0')
            print 'resp', resp.body

        resp = self.fetch('/post', method='POST', body='a=1&b=2')
        print 'resp', resp.body
        self.assertEqual(resp.code, 200)

    def test_post_json(self):
        with ExpectLog(app_log, 'Uncaught exception', required=True):
            resp = self.fetch('/post/json', method='POST', body='')
            print 'resp 1', resp.body

        with ExpectLog(app_log, 'Uncaught exception', required=True):
            resp = self.fetch('/post/json', method='POST', body='a=1')
            print 'resp 2', resp.body

        resp = self.fetch('/post/json', method='POST', body='{"a":"1"}')
        print 'resp 3', resp.body
        self.assertEqual(resp.code, 200)

        with ExpectLog(app_log, 'Uncaught exception', required=True):
            resp = self.fetch('/post/json', method='POST', body='{"a":1}')
            print 'resp 4', resp.body
