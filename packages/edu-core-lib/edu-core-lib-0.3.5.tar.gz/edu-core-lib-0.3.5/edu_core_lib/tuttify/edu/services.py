import inspect
import sys


def get_evaluation_scheme_names():
    from . import evaluation

    result = []
    for name, obj in inspect.getmembers(sys.modules[evaluation.__name__]):
        if inspect.isclass(obj):
            result.append(
                {
                    "repr_name": obj.name,
                    "class_name": obj.__name__,
                }
            )
    return result
