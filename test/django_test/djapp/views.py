# coding: utf-8

from django.http import HttpResponse
from django.views.generic import View
import params
from params.contrib.django import use_params, use_params_class_view


def index(request):
    return HttpResponse(request.method)


@use_params({
    'a': params.Field(required=True),
})
def funcview(request):
    assert request.params.a == '1'
    return HttpResponse(str(request.params))


class ClassView(View):
    @use_params_class_view({
        'a': params.Field(required=True),
    })
    def get(self, request):
        assert request.params.a == '1'
        return HttpResponse(str(request.params))


@use_params({
    'a': params.Field(required=True),
}, json=True)
def jsonview(request):
    assert request.params.a == 1
    return HttpResponse(str(request.params))
