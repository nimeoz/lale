from lale.sklearn_compat import clone_op
from lale.operators import Operator, make_operator

import logging
import inspect
import importlib

logger = logging.getLogger(__name__)

def wrap_imported_operators():
    calling_frame = inspect.stack()[1][0]
    symtab = calling_frame.f_globals
    for name, impl in symtab.items():
        if inspect.isclass(impl) and not issubclass(impl, Operator):
            module = impl.__module__.split('.')[0]
            klass = impl.__name__
            try:
                m = importlib.import_module('lale.lib.' + module)
                symtab[name] = clone_op(getattr(m, klass), name)
                logger.info(f'Lale:Wrapped known operator:{name}')
            except (ModuleNotFoundError, AttributeError):
                try:
                    m = importlib.import_module('lale.lib.autogen')
                    symtab[name] = clone_op(getattr(m, klass), name)
                    logger.info(f'Lale:Wrapped autogen operator:{name}')
                except (ModuleNotFoundError, AttributeError):
                    if hasattr(impl, 'fit') and (
                    hasattr(impl, 'predict') or hasattr(impl, 'transform')):
                        logger.info(f'Lale:Wrapped unkwnown operator:{name}')
                        symtab[name] = make_operator(impl=impl, name=name)
      
