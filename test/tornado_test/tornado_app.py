#!/usr/bin/env python

import sys
import tornado.httpserver
import tornado.ioloop
import tornado.options
from tornado.web import RequestHandler, Application
from tornado.options import define, options
from tornado.log import enable_pretty_logging
import params
from params.contrib.tornado import use_params, use_raw


class BaseHandler(RequestHandler):
    def _handle_request_exception(self, e):
        #from tornado.web import Finish, app_log, gen_log, HTTPError, httputil
        from tornado.web import app_log, gen_log, HTTPError, httputil

        #if isinstance(e, Finish):
        #    # Not an error; just finish the request without logging.
        #    if not self._finished:
        #        self.finish(*e.args)
        #    return

        ## add
        if isinstance(e, params.InvalidParams):
            self.set_status(400)
            self.finish({'error': str(e)})
            return
        ## end

        try:
            self.log_exception(*sys.exc_info())
        except Exception:
            # An error here should still get a best-effort send_error()
            # to avoid leaking the connection.
            app_log.error("Error in exception logger", exc_info=True)
        if self._finished:
            # Extra errors after the request has been finished should
            # be logged, but there is no reason to continue to try and
            # send a response.
            return
        if isinstance(e, HTTPError):
            if e.status_code not in httputil.responses and not e.reason:
                gen_log.error("Bad HTTP status code: %d", e.status_code)
                self.send_error(500, exc_info=sys.exc_info())
            else:
                self.send_error(e.status_code, exc_info=sys.exc_info())
        else:
            self.send_error(500, exc_info=sys.exc_info())


class HomeHandler(BaseHandler):
    def get(self):
        self.write('hello world')

    def post(self):
        self.write(self.request.arguments)


class GetHandler(BaseHandler):
    @use_params({
        'a': params.IntegerField(required=True),
    })
    def get(self):
        print('params', self.params)
        if self.params.a != 1:
            raise params.InvalidParams('a != 1')
        return self.write(str(self.params))


class PostHandler(BaseHandler):
    class PostParams(params.ParamSet):
        a = params.IntegerField(required=True)
        b = params.Field()

    @use_params(PostParams)
    def post(self):
        print('params', self.params)
        if self.params.a != 1:
            raise params.InvalidParams('a != 1')
        if self.params.b and self.params.b != 'b':
            raise params.InvalidParams('b != b')
        return self.write(str(self.params))


class PostJsonHandler(BaseHandler):
    @use_params({
        'a': params.IntegerField(required=True),
        'b': params.Field(),
    }, is_json=True)
    def post(self):
        print('params', self.params)
        if self.params.a != 1:
            raise params.InvalidParams('a != 1')
        if self.params.b and self.params.b != 'b':
            raise params.InvalidParams('b != b')
        return self.write(str(self.params))


class RawHandler(BaseHandler):
    @use_raw()
    def post(self):
        print('params', self.params)
        if 'a' not in self.params:
            raise params.InvalidParams('no a')
        return self.write(str(self.params))


class RawJsonHandler(BaseHandler):
    @use_raw(is_json=True)
    def post(self):
        print('params', self.params)
        if 'a' not in self.params:
            raise params.InvalidParams('no a')
        return self.write(str(self.params))


def get_app():
    enable_pretty_logging()
    application = Application([
        (r'/', HomeHandler),
        (r'/get', GetHandler),
        (r'/post', PostHandler),
        (r'/post/json', PostJsonHandler),
        (r'/raw', RawHandler),
        (r'/raw/json', RawJsonHandler),
    ])
    return application


def main():
    define('port', default=8888, help='run on the given port', type=int)
    tornado.options.parse_command_line()
    application = get_app()
    print('starting tornado app on port {}'.format(options.port))
    for host, rules in application.handlers:
        for i in rules:
            print(i.regex.pattern)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
