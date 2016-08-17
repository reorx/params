# coding: utf-8

import ipaddress
from torext import TorextApp
from torext.handlers import BaseHandler as _BaseHandler
import params
from params.contrib.tornado import use_params

app = TorextApp()


class IPField(params.Field):
    def validate(self, value):
        try:
            ipaddress.ip_address(value)
        except ValueError:
            raise self.format_exc('{} is not a valid ip address'.format(value))
        return value


class BaseHandler(_BaseHandler):
    EXCEPTION_HANDLERS = {
        params.InvalidParams: '_handle_invalid_params',
    }

    def _handle_invalid_params(self, e):
        self.set_status(400)
        self.write_json({
            'error': str(e)
        })


@app.route('/register')
class RegisterHandler(BaseHandler):
    @use_params({
        'hostname': params.StringField(required=True),
        'ip_addr': IPField(required=True),
        'mac_addr': params.RegexField(pattern=r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
    })
    def post(self):
        print self.params.hostname
        print self.params.ip_addr
        print self.params.mac_addr


if __name__ == '__main__':
    app.command_line_config()
    app.run()
