import sys
import json


class ToStrJSONEncoder(json.JSONEncoder):
    def default(self, o):
        return repr(o)


def obj2str(obj):
    def walk(_obj):
        try:
            _json = getattr(_obj, '__json__', None)
        except:
            _json = None
        if callable(_json):
            _obj = _json()
        if isinstance(_obj, dict):
            result = {}
            for k, v in _obj.items():
                result[k] = walk(v)
            return result
        else:
            return _obj

    return json.dumps(walk(obj), indent=2, ensure_ascii=False, sort_keys=True, cls=ToStrJSONEncoder)


def get_data_or_value(data, expression=None):
    if expression:
        from jsonpath_ng import parse
        rl = parse(expression).find(data)
        if rl:
            result = rl[0].value
        else:
            result = None
        if isinstance(result, (dict, list)):
            v = obj2str(result)
        else:
            v = str(result)
    else:
        v = obj2str(data)
    return v


def pprint(obj, *args, **kwargs):
    print(obj2str(obj), *args, **kwargs)


def print_data_or_value(data, expression=None):
    sys.stdout.write(get_data_or_value(data, expression))
    sys.stdout.flush()
