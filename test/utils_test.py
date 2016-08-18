from params.utils import unicode_copy


def test_unicode_copy():
    # str
    a = 'a'
    b = unicode_copy(a)
    assert isinstance(b, unicode)
    assert a == str(b)

    # dict
    a = {
        'a': 'b'
    }
    b = unicode_copy(a)
    assert isinstance(b.keys()[0], str)
    assert isinstance(b['a'], unicode)
    assert a['a'] == str(b['a'])

    # list
    a = ['a']
    b = unicode_copy(a)
    assert isinstance(b[0], unicode)
    assert a[0] == str(b[0])
