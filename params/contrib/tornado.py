#!/usr/bin/env python
# coding: utf-8

from __future__ import absolute_import

from functools import wraps
from ..utils import json_decode, to_unicode
from ..core import InvalidParams
from .base import get_params_cls, check_method


def use_params(df, is_json=False, raise_if_invalid=True):
    # if it's json, do not convert, for json is type specified.
    # if not json, which means it's urlencode, then convert is needed.
    convert = not is_json
    params_cls = get_params_cls(df)

    def decorator(view_method):
        http_method = check_method(view_method.__name__.upper(), is_json)

        @wraps(view_method)
        def func(self, *args, **kwargs):
            raw = get_raw(self, http_method, is_json)
            self.params = params_cls(raw, convert=convert, raise_if_invalid=raise_if_invalid)
            return view_method(self, *args, **kwargs)

        return func

    return decorator


def use_raw(is_json=False):
    def decorator(view_method):
        http_method = check_method(view_method.__name__.upper(), is_json)

        @wraps(view_method)
        def func(self, *args, **kwargs):
            raw = get_raw(self, http_method, is_json)
            self.params = raw
            return view_method(self, *args, **kwargs)

        return func

    return decorator


def get_raw(hdr, http_method, is_json):
    if is_json:
        try:
            raw = json_decode(hdr.request.body)
        except Exception as e:
            raise InvalidParams('JSON decode failed: %s' % e)
    else:
        raw = {}
        # format arguments
        for k, v in hdr.request.arguments.iteritems():
            if len(v) > 1:
                raw[k] = map(to_unicode, v)
            else:
                raw[k] = to_unicode(v[0])
    return raw
