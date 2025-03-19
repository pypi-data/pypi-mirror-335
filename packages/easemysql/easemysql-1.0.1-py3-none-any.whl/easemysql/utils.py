def where_in(ids: list):
    _str = ''
    for _id in ids:
        _str += "'{}',".format(_id)
    return _str[:-1]
