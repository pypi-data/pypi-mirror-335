import operator


class Proxy:
    """
    Example Usage:

        class Real:
            def __init__(self):
                self.prop1 = 'prop1_val'
            def method1(self):
                return "method1_val"

        class ProxyWrapped(Proxy):
            prop1 = 'proxy_prop1_val' #both get/set operations are overriden when declared at proxy level
            def method1(self):
                return "proxy_method1_val"

        proxyObj:Real = ProxyWrapped(Real())
        proxyObj.prop1 # "proxy_prop1_val"
    """
    def __init__(self, target):
        self.__target__ = target

    def __HasAttribute__(self, name):
        """checks at top level if proxy class itself has an attribute"""
        try:
            object.__getattribute__(self, name) #check if exists on proxy level
            return True
        except AttributeError:
            return False

    def __getattribute__(self, name: str):
        """
        Intercept property access
        """

        try:
            return object.__getattribute__(self, name)
        except AttributeError: pass

        target = object.__getattribute__(self, "__target__")
        return getattr(target, name)

    def __setattr__(self, name:str, value):
        """
        Intercept property assignment
        If property already exists in proxy class then it takes precedence.
        """

        if name == '__target__' or self.__HasAttribute__(name):
            object.__setattr__(self, name, value)
        else:
            setattr(self.__target__, name, value)

    def __delattr__(self, name:str):
        """Intercept property deletion"""
        if(self.__HasAttribute__(name)):
            object.__delattr__(self, name)
        else:
            delattr(self.__target__, name)

    def __getitem__(self, key):
        """Intercept index access"""
        return self.__target__[key]

    def __setitem__(self, key, value):
        """Intercept index assignment"""
        self.__target__[key] = value

    def __delitem__(self, key):
        """Intercept index deletion"""
        del self.__target__[key]

    def __call__(self, *args, **kwargs):
        """
        Intercept calls on instantiated proxy, such as wrapping a classtype and instatiating from it...
        >>> wrappedClass = Proxy(SomeClassType)
        >>> wrappedClass(*args, **kwargs) #init of the proxy would trigger this
        """
        return self.__target__(*args, **kwargs)

    def __repr__(self):
        return f"<Proxy {repr(self.__target__)}>"

    # Forwarding common magic methods
    def __len__(self):
        return len(self.__target__)
    def __str__(self):
        return str(self.__target__)
    def __iter__(self):
        return iter(self.__target__)
    def __contains__(self, item):
        return item in self.__target__
    def __bool__(self):
        return bool(self.__target__)
    def __hash__(self):
        return hash(self.__target__)
    def __enter__(self):
        return self.__target__.__enter__()
    def __exit__(self, *args, **kwargs):
        return self.__target__.__exit__(*args, **kwargs)
    def __lt__(self, other):
        return self.__target__ < other
    def __le__(self, other):
        return self.__target__ <= other
    def __eq__(self, other):
        return self.__target__ == other
    def __ne__(self, other):
        return self.__target__ != other
    def __gt__(self, other):
        return self.__target__ > other
    def __ge__(self, other):
        return self.__target__ >= other

