#!/usr/bin/env python
# coding: utf-8

from __future__ import absolute_import
import json as libjson
from functools import wraps
from ..core import define_params, InvalidParams


def use_params(df, class_view=False, json=False):
    params_cls = define_params(df)

    if class_view:
        def decorator(view_method):
            # For class view, we can check http method before view method is called
            _check_method(view_method.__name__.upper(), json)

            @wraps(view_method)
            def func(self, request, *args, **kwargs):
                request.params = get_params(params_cls, request, json)
                return view_method(self, request, *args, **kwargs)

            return func
    else:
        def decorator(view_func):

            @wraps(view_func)
            def func(request, *args, **kwargs):
                request.params = get_params(params_cls, request, json)
                return view_func(request, *args, **kwargs)

            return func

    return decorator


def get_params(params_cls, request, json=False):
    http_method = _check_method(request.method, json)
    if json:
        raw = _get_json(request)
    else:
        raw = getattr(request, http_method)
    params = params_cls(raw)
    return params


def _get_json(request):
    try:
        raw = libjson.loads(request.body)
    except Exception as e:
        raise InvalidParams('Could not parse body as json: {}'.format(e))
    return raw


def _check_method(http_method, json):
    if http_method == 'GET' and json:
        raise ValueError('json=True could only be used on method other than GET')
    return http_method
