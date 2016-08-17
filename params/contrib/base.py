import inspect
from ..utils import HTTP_METHODS
from ..core import define_params, ParamSet


def get_params_cls(df):
    if inspect.isclass(df):
        if not issubclass(df, ParamSet):
            raise TypeError('must pass sub class of ParamSet')
        params_cls = df
    else:
        params_cls = define_params(df)
    return params_cls


def check_method(http_method, is_json):
    if http_method == 'GET' and is_json:
        raise ValueError('is_json=True could only be used on method other than GET')
    if http_method not in HTTP_METHODS:
        raise ValueError('method {} is not one of {}'.format(http_method, HTTP_METHODS))
    return http_method
