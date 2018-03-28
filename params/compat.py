import sys


PY3 = sys.version_info.major == 3
PY2 = sys.version_info.major == 2


if PY2:
    from urllib import urlencode, quote
    from urlparse import urljoin
    import httplib
    def unicode_(s, *args):
        return unicode(s, *args)
    def decode_(s, *args):
        return s.decode(*args)
    def encode_(s, *args):
        return s.encode(*args)
    def bytes_(s):
        return s
    def str_(s):
        return s
else:
    from urllib.parse import urlencode, quote, urljoin
    import http.client as httplib
    def unicode_(s, *args):
        return s
    def decode_(s, *args):
        return s
    def encode_(s, *args):
        return s
    def bytes_(s):
        return s.encode('utf8')
    def str_(s):
        return s.decode('utf8')
