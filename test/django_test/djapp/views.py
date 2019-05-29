# coding: utf-8

from django.http import HttpResponse
from django.views.generic import View
import params
from params.contrib.django import use_params, use_params_class_view
from nose.tools import assert_equal


def index(request):
    return HttpResponse(request.method)


@use_params({
    'a': params.Field(required=True),
    'b': params.ListField(),
})
def funcview(request):
    assert_equal(request.params.a, '1')
    assert_equal(request.params.b, [u'x', u'y'])
    return HttpResponse(str(request.params))


class ClassView(View):
    @use_params_class_view({
        'a': params.Field(required=True),
    })
    def get(self, request):
        assert_equal(request.params.a, '1')
        return HttpResponse(str(request.params))


@use_params({
    'a': params.Field(required=True),
}, is_json=True)
def jsonview(request):
    assert_equal(request.params.a, 1)
    return HttpResponse(str(request.params))


@use_params({
    'a': params.Field(required=True),
}, is_json=True, is_list=True)
def jsonlistview(request):
    assert_equal(request.params[0].a, 1)
    return HttpResponse(str(request.params))
