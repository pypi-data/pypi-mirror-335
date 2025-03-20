from simpleworkspace.__lazyimporter__ import __LazyImporter__, __TYPE_CHECKING__
if(__TYPE_CHECKING__):
    from . import crosscryptv2 as _crosscryptv2
    from . import crosscryptv2_alteration_ctr as _crosscryptv2_alteration_ctr

crosscryptv2: '_crosscryptv2' = __LazyImporter__(__package__, '.crosscryptv2')
crosscryptv2_alteration_ctr: '_crosscryptv2_alteration_ctr' = __LazyImporter__(__package__, '.crosscryptv2_alteration_ctr')
