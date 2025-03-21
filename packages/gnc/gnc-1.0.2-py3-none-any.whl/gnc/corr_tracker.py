import builtins as __builtin__
from sys import version_info as _swig_python_version_info
# Import the low-level C/C++ module
if __package__ or "." in __name__:
    from . import _gnc
else:
    import _gnc

"""
SEARCH_RADIUS_FACTOR– коефіцієнт радіусу пошуку об'єкта. Застосовуєть для встановлення області пошуку об'єкта. 
Приклад: Область пошуку = SEARCH_RADIUS_FACTOR * рамка в пікселях/фактична ознака обє'кта(rx=48 + ry=48 + 1(центральний піксель)) 
CORRELATION_THRESHOLD=0.85 – поріг впевненості, що об'єкт є шукомим. Робочий діапазон від 0.925 до 0.98
ALT_SEARCH_RADIUS_FACTOR=0 – альтернативний коефіцієнт радіусу пошуку (для випадків втрати об'єкта).
SIGMA_EXP= від -5.0 до 5.0 – параметр який зазначає які значення в рамці відповідності до обє'кта є більш важливі.
Приклад:-5.0 - Центральний піксель є безумовно вжливим; 5.0 - Вся Рамка є важливою.
CLONE_IMAGE=False – чи клонувати зображення під час обробки.
DEPTH=1 – глибина обробки.
ZOOM_FACTOR=1 – коефіцієнт масштабування.
MODE_1D=False – чи працювати в одновимірному режимі.
CONTRAST_THRESHOLD=0.0 – поріг контрасту для фільтрації об'єктів.
CONTRAST_K_SIZE=3 – розмір ядра для обчислення контрасту.
CONTRAST_GREYSCALE=False – чи використовувати градації сірого для контрасту.
NIGHT - Встановлює нові значення для ALT_SEARCH_RADIUS_FACTOR; CORRELATION_THRESHOLD; SIGMA_EXP
"""
SEARCH_RADIUS_FACTOR = 1.5
CORRELATION_THRESHOLD = 0.98
ALT_SEARCH_RADIUS_FACTOR = SEARCH_RADIUS_FACTOR + 1
SIGMA_EXP = 4
CLONE_IMAGE = False
DEPTH = 5
ZOOM_FACTOR = 10
MODE_1D = True
CONTRAST_THRESHOLD = 1000
CONTRAST_K_SIZE = 3
CONTRAST_GREYSCALE = False
NIGHT = False
NIGHT_ALT_SEARCH_RADIUS_FACTOR = SEARCH_RADIUS_FACTOR + 2
NIGHT_CORRELATION_THRESHOLD = 0.925
NIGHT_SIGMA_EXP = -0.25


def _swig_repr(self):
    try:
        strthis = "proxy of " + self.this.__repr__()
    except __builtin__.Exception:
        strthis = ""
    return "<%s.%s; %s >" % (self.__class__.__module__, self.__class__.__name__, strthis,)


def _swig_setattr_nondynamic_instance_variable(set):
    def set_instance_attr(self, name, value):
        if name == "this":
            set(self, name, value)
        elif name == "thisown":
            self.this.own(value)
        elif hasattr(self, name) and isinstance(getattr(type(self), name), property):
            set(self, name, value)
        else:
            raise AttributeError("You cannot add instance attributes to %s" % self)

    return set_instance_attr


def _swig_setattr_nondynamic_class_variable(set):
    def set_class_attr(cls, name, value):
        if hasattr(cls, name) and not isinstance(getattr(cls, name), property):
            set(cls, name, value)
        else:
            raise AttributeError("You cannot add class attributes to %s" % cls)

    return set_class_attr


def _swig_add_metaclass(metaclass):
    """Class decorator for adding a metaclass to a SWIG wrapped class - a slimmed down version of six.add_metaclass"""

    def wrapper(cls):
        return metaclass(cls.__name__, cls.__bases__, cls.__dict__.copy())

    return wrapper


class _SwigNonDynamicMeta(type):
    """Meta class to enforce nondynamic attributes (no new attributes) for a class"""
    __setattr__ = _swig_setattr_nondynamic_class_variable(type.__setattr__)


class CorrTracker(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc="The membership flag")
    __repr__ = _swig_repr

    def __init__(self, search_radius_factor=SEARCH_RADIUS_FACTOR, correlation_threshold=CORRELATION_THRESHOLD,
                 alt_search_radius_factor=ALT_SEARCH_RADIUS_FACTOR, sigma_exp=SIGMA_EXP,
                 clone_image=CLONE_IMAGE, depth=DEPTH, zoom_factor=ZOOM_FACTOR, mode_1d=MODE_1D,
                 contrast_threshold=CONTRAST_THRESHOLD, contrast_k_size=CONTRAST_K_SIZE,
                 contrast_greyscale=CONTRAST_GREYSCALE, night=NIGHT):
        self.search_radius_factor = search_radius_factor
        self.correlation_threshold = correlation_threshold
        self.alt_search_radius_factor = alt_search_radius_factor
        self.sigma_exp = sigma_exp
        self.clone_image = clone_image
        self.depth = depth
        self.zoom_factor = zoom_factor
        self.mode_1d = mode_1d
        self.contrast_threshold = contrast_threshold
        self.contrast_k_size = contrast_k_size
        self.contrast_greyscale = contrast_greyscale
        if night:
            self.alt_search_radius_factor = NIGHT_ALT_SEARCH_RADIUS_FACTOR
            self.correlation_threshold = NIGHT_CORRELATION_THRESHOLD
            self.sigma_exp = NIGHT_SIGMA_EXP
        _gnc.PyTrackerCorr_swiginit(self, _gnc.new_PyTrackerCorr(self.search_radius_factor, self.correlation_threshold,
                                                                 self.alt_search_radius_factor, self.sigma_exp,
                                                                 self.clone_image, self.depth,
                                                                 self.zoom_factor, self.mode_1d,
                                                                 self.contrast_threshold, self.contrast_k_size,
                                                                 self.contrast_greyscale))

    __swig_destroy__ = _gnc.delete_PyTrackerCorr

    def init(self, image, bounding_box):
        return _gnc.PyTrackerCorr_init(self, image, bounding_box)

    def update(self, image, bounding_box):
        return _gnc.PyTrackerCorr_update(self, image, bounding_box)

    def variance(self):
        return _gnc.PyTrackerCorr_variance(self)

    def matches(self):
        return _gnc.PyTrackerCorr_matches(self)


# Register CorrTracker in _gnc:
_gnc.PyTrackerCorr_swigregister(CorrTracker)
# Константа - Максимальне значення SIGMA_EXP
cvar = _gnc.cvar
SIGMA_EXP_MAX = cvar.SIGMA_EXP_MAX
