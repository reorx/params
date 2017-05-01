#!/usr/bin/env python
# coding: utf-8

from __future__ import absolute_import

import json
from functools import wraps
from ..core import InvalidParams
from .base import get_params_cls, check_method


def use_params(df, class_view=False, is_json=False, raise_if_invalid=True):
    convert = not is_json
    params_cls = get_params_cls(df)

    if class_view:
        def decorator(view_method):
            # For class view, we can check http method before view method is called
            check_method(view_method.__name__.upper(), is_json)

            @wraps(view_method)
            def func(self, request, *args, **kwargs):
                raw = get_raw(request, is_json)
                request.params = params_cls(raw, convert=convert, raise_if_invalid=raise_if_invalid)
                return view_method(self, request, *args, **kwargs)

            return func
    else:
        def decorator(view_func):

            @wraps(view_func)
            def func(request, *args, **kwargs):
                raw = get_raw(request, is_json)
                request.params = params_cls(raw, convert=convert, raise_if_invalid=raise_if_invalid)
                return view_func(request, *args, **kwargs)

            return func

    return decorator


def use_params_class_view(df, is_json=False, raise_if_invalid=True):
    return use_params(df, class_view=True, is_json=is_json, raise_if_invalid=raise_if_invalid)


def get_raw(request, is_json=False):
    http_method = check_method(request.method, is_json)
    if is_json:
        raw = _get_json(request)
    else:
        _raw = getattr(request, http_method)
        # convert django <QueryDict> to dict, when <QueryDict>
        # is like <QueryDict {'a': ['1'], 'b': ['x', 'y']}>,
        # iteritems will make 'a' return '1', 'b' return 'y',
        # we should convert it to a normal dict so that 'b' keeps
        # ['x', 'y']
        raw = {}
        for k, v in _raw.iterlists():
            if not v:
                continue
            if len(v) == 1:
                raw[k] = v[0]
            else:
                raw[k] = v
    return raw


def _get_json(request):
    try:
        raw = json.loads(request.body)
    except Exception as e:
        raise InvalidParams('Could not parse body as json: {}'.format(e))
    return raw
