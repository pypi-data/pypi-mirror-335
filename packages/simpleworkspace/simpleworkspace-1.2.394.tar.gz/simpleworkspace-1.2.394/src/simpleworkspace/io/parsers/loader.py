from simpleworkspace.__lazyimporter__ import __LazyImporter__, __TYPE_CHECKING__
if(__TYPE_CHECKING__):
    from . import archive as _archive
    from . import csv as _csv
    from . import json5 as _json5
    from . import logging as _logging
    from . import m3u8 as _m3u8
    from . import toml as _toml

archive: '_archive' = __LazyImporter__(__package__, '.archive')
csv: '_csv' = __LazyImporter__(__package__, '.csv')
json5: '_json5' = __LazyImporter__(__package__, '.json5')
logging: '_logging' = __LazyImporter__(__package__, '.logging')
m3u8: '_m3u8' = __LazyImporter__(__package__, '.m3u8')
toml: '_toml' = __LazyImporter__(__package__, '.toml')
