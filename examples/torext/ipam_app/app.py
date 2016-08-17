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


mac_field = params.RegexField(
    description='not a valid mac address',
    pattern=r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')


@app.route('/register')
class RegisterHandler(BaseHandler):
    @use_params({
        'hostname': params.StringField(required=True),
        'ip_addr': IPField(required=True),
        'mac_addr': mac_field.spawn(required=True),
    })
    def post(self):
        print self.params.hostname
        print self.params.ip_addr
        print self.params.mac_addr
        self.write_json(self.params.data)


@app.route('/resolves')
class ResolvesHandler(BaseHandler):
    class PostParams(params.ParamSet):
        hostname = params.StringField(required=True)
        ip_addr = IPField(required=True)

        def validate_hostname(self, value):
            try:
                ipaddress.ip_address(value)
            except ValueError:
                return value
            else:
                raise ValueError('hostname could not be an ip address')

    @use_params(PostParams)
    def post(self):
        print self.params.hostname
        print self.params.ip_addr
        self.write_json(self.params.data)


@app.route('/macs/([\w:-]+)')
class MacsItemHandler(BaseHandler):
    def get(self, mac):
        try:
            mac_field.validate(mac)
        except ValueError as e:
            raise params.InvalidParams('invalid mac: {}'.format(e))
        print mac
        self.write(mac)


if __name__ == '__main__':
    app.command_line_config()
    app.run()
