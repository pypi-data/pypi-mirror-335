import base64
import io

from dill._dill import Unpickler as DillUnpickler, Pickler, _main_module
from pickle import _Unpickler as StockUnpickler


class Unpickler(StockUnpickler):
    """python's Unpickler extended to interpreter sessions and more types"""

    from dill.settings import settings
    _session = False

    def __init__(
        self, *, fix_imports=True, encoding="ASCII", errors="strict", buffers=None
    ):
        self.file = io.BytesIO()
        super().__init__(
            self.file,
            fix_imports=fix_imports,
            encoding=encoding,
            errors=errors,
            buffers=buffers,
        )

    def find_class(self, module, name):
        if (module, name) == ('__builtin__', '__main__'):
            return self._main.__dict__  # XXX: above set w/save_module_dict
        elif (module, name) == ('__builtin__', 'NoneType'):
            return type(None)  # XXX: special case: NoneType missing
        if module == 'dill.dill': module = 'dill._dill'
        return StockUnpickler.find_class(self, module, name)

    def __init__(self, *args, **kwds):
        settings = Pickler.settings
        _ignore = kwds.pop('ignore', None)
        StockUnpickler.__init__(self, *args, **kwds)
        self._main = _main_module
        self._ignore = settings['ignore'] if _ignore is None else _ignore

    def load(self):  # NOTE: if settings change, need to update attributes
        obj = StockUnpickler.load(self)
        if type(obj).__module__ == getattr(_main_module, '__name__', '__main__'):
            if not self._ignore:
                # point obj class to main
                try:
                    obj.__class__ = getattr(self._main, type(obj).__name__)
                except (AttributeError, TypeError):
                    pass  # defined in a file
        # _main_module.__dict__.update(obj.__dict__) #XXX: should update globals ?
        return obj

    load.__doc__ = StockUnpickler.load.__doc__
    pass

    def load_data(
        self, file, buffers=None
    ):  # NOTE: if settings change, need to update attributes
        # Add the content of `file` to `self.file`
        self.file.seek(0)
        self.file.truncate()
        self.file.write(file.read())
        return self.load()


unpickler = Unpickler()


def load_base64(data):
    file = io.BytesIO(base64.decodebytes(data.encode()))
    return unpickler.load_data(file)



from typing import TypedDict

MyProps = TypedDict("MyProps", {
    "test": str,
    "aria_label": str
})


from pret.render import p


p(on_click=lambda e: print(e.target.aria_label))
