from simpleworkspace.__lazyimporter__ import __LazyImporter__, __TYPE_CHECKING__
if(__TYPE_CHECKING__):
    from . import observables as _observables
    from . import caseinsensitivedict as _caseinsensitivedict
    from . import linq as _linq
    from . import proxy as _proxy
observables: '_observables' = __LazyImporter__(__package__, '.observables')
caseinsensitivedict: '_caseinsensitivedict' = __LazyImporter__(__package__, '.caseinsensitivedict')
linq: '_linq' = __LazyImporter__(__package__, '.linq')
proxy: '_proxy' = __LazyImporter__(__package__, '.proxy')