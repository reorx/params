from ..utils import HTTP_METHODS


def check_method(http_method, is_json):
    if http_method == 'GET' and is_json:
        raise ValueError('is_json=True could only be used on method other than GET')
    if http_method not in HTTP_METHODS:
        raise ValueError('method {} is not one of {}'.format(http_method, HTTP_METHODS))
    return http_method
