from typing import Dict


class DictClass:

    def __getattr__(self, key):
        """只有未定义的属性才会到__getattr__"""
        return None

    def get(self, key, default=None):
        return getattr(self, key) or default

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)

    def __contains__(self, key):
        return bool(getattr(self, key))

    def update(self, dic: Dict):
        for k, v in dic.items():
            setattr(self, k, v)

    def items(self):
        for k, v in self.__class__.__dict__.items():
            if k.startswith("__"):
                continue
            yield k, v

        for k, v in self.__dict__.items():
            if k.startswith("__"):
                continue
            yield k, v


class ClassDict:

    def __init__(self, d: Dict):
        self._dict = d

    def get(self, *args):
        return self._dict.get(*args)

    def __getitem__(self, key):
        return self._dict.get(key, None)

    def __setitem__(self, *args):
        return self._dict.__setitem__(*args)

    def __getattr__(self, key):
        if key == "_dict":
            return super(ClassDict, self).__getattribute__("_dict")
        else:
            return self._dict.get(key, None)

    def __setattr__(self, key, value):
        if key == "_dict":
            super(ClassDict, self).__setattr__(key, value)
        else:
            self._dict["key"] = value

    def __contains__(self, key):
        return bool(getattr(self, key))
