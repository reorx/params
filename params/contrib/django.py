#!/usr/bin/env python
# coding: utf-8

from __future__ import absolute_import

import six
import json
from functools import wraps
from ..core import InvalidParams
from .base import get_params_cls, check_method


def use_params(df, class_view=False, is_json=False, raise_if_invalid=True, is_list=False):
    if is_json:
        convert_fields = False
    else:
        convert_fields = True

    params_cls = get_params_cls(df)
    if is_list and not is_json:
        raise ValueError('is_json must be True when is_list is True')

    if class_view:
        def decorator(view_method):
            # For class view, we can check http method before view method is called
            check_method(view_method.__name__.upper(), is_json)

            @wraps(view_method)
            def func(self, request, *args, **kwargs):
                raw = get_raw(request, is_json)
                if is_list:
                    if not isinstance(raw, list):
                        raise InvalidParams('request body must be of type list, got: {}'.format(type(raw)))
                    request.params = [params_cls(x, convert_fields=convert_fields, raise_if_invalid=raise_if_invalid) for x in raw]
                else:
                    request.params = params_cls(raw, convert_fields=convert_fields, raise_if_invalid=raise_if_invalid)
                return view_method(self, request, *args, **kwargs)

            return func
    else:
        def decorator(view_func):

            @wraps(view_func)
            def func(request, *args, **kwargs):
                raw = get_raw(request, is_json)
                if is_list:
                    if not isinstance(raw, list):
                        raise InvalidParams('request body must be of type list, got: {}'.format(type(raw)))
                    request.params = [params_cls(x, convert_fields=convert_fields, raise_if_invalid=raise_if_invalid) for x in raw]
                else:
                    request.params = params_cls(raw, convert_fields=convert_fields, raise_if_invalid=raise_if_invalid)
                return view_func(request, *args, **kwargs)

            return func

    return decorator


def use_params_class_view(df, is_json=False, raise_if_invalid=True, is_list=False):
    return use_params(df, class_view=True, is_json=is_json, raise_if_invalid=raise_if_invalid, is_list=is_list)


def get_raw(request, is_json=False):
    http_method = check_method(request.method, is_json)
    if is_json:
        raw = _get_json(request)
    else:
        # only handle GET and POST because django only have these two attrs on request
        # NOTE can also use QueryDict(request.body) for PUT, DELETE, but that will take
        # more uncessary complexity
        if http_method == 'GET':
            _raw = request.GET
        elif http_method == 'POST':
            _raw = request.POST
        else:
            _raw = {}
        # convert django <QueryDict> to dict, when <QueryDict>
        # is like <QueryDict {'a': ['1'], 'b': ['x', 'y']}>,
        # iteritems will make 'a' return '1', 'b' return 'y',
        # we should convert it to a normal dict so that 'b' keeps
        # ['x', 'y']
        raw = {}
        for k, v in six.iterlists(_raw):
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
