from typing import TypeVar as _TypeVar
from collections.abc import MutableMapping as _MutableMapping, Iterable as _Iterable

_KT = _TypeVar('_KT')
_VT = _TypeVar('_VT')
_T = _TypeVar('_T')
class CaseInsensitiveDict(dict[_KT, _VT]):
    def __init__(self, *args:_MutableMapping[_KT, _VT], **kwargs:_VT):
        super().__init__(*args, **kwargs)
        self._init_keys()

    def _init_keys(self):
        for key in list(self.keys()):
            if(self._normalizeKey(key) == key): #if the key provided already is normalized then skip
                continue
            value = super().pop(key)
            self.__setitem__(key, value)
            
    def _normalizeKey(self, key: _KT) -> _KT:
        if(isinstance(key, str)):
            return key.upper()
        return key

    def __setitem__(self, key: _KT, value: _VT):
        super().__setitem__(self._normalizeKey(key), value)

    def __getitem__(self, key: _KT) -> _VT:
        return super().__getitem__(self._normalizeKey(key))

    def __delitem__(self, key: _KT):
        return super().__delitem__(self._normalizeKey(key))

    def __contains__(self, key: _KT) -> bool:
        return super().__contains__(self._normalizeKey(key))

    def get(self, key:_KT, default:_T=None) -> _VT|_T:
        return super().get(self._normalizeKey(key), default)

    def pop(self, key:_KT, default:_T=None) -> _VT|_T:
        return super().pop(self._normalizeKey(key), default)

    def update(self, m:_MutableMapping[_KT, _VT]|_Iterable[tuple[_KT, _VT]]=None, **kwargs:_VT):
        if m is not None:
            if isinstance(m, _MutableMapping):
                for key in m:
                    self.__setitem__(key, m[key])
            else:
                for key, value in m:
                    self.__setitem__(key, value)
        for key in kwargs:
            self.__setitem__(key, kwargs[key])