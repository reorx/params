#!/usr/bin/env python
# coding: utf-8

from __future__ import absolute_import
import functools
from ..utils import json_decode
from ..core import ParamsInvalidError


def simple_params(datatype='form'):
    assert datatype in ('form', 'json')

    def decorator(method):
        @functools.wraps(method)
        def wrapper(hdr, *args, **kwgs):
            if 'json' == datatype:
                try:
                    params = json_decode(hdr.request.body)
                except Exception, e:
                    raise ParamsInvalidError('JSON decode failed: %s' % e)
            else:
                params = dict((k, v[0])
                              for k, v in hdr.request.arguments.iteritems())

            hdr.params = params
            return method(hdr, *args, **kwgs)
        return wrapper
    return decorator


def validation_required(cls, method):
    @functools.wraps(method)
    def wrapper(hdr, *args, **kwgs):
        if 'json' == cls.__datatype__:
            try:
                arguments = json_decode(hdr.request.body)
            except Exception, e:
                raise ParamsInvalidError('JSON decode failed: %s' % e)
        else:
            arguments = hdr.request.arguments
        # Instantiate ParamSet
        print 'cls', cls.__datatype__
        params = cls(**arguments)
        if params.errors:
            raise ParamsInvalidError(params.errors)
        hdr.params = params
        return method(hdr, *args, **kwgs)
    return wrapper
