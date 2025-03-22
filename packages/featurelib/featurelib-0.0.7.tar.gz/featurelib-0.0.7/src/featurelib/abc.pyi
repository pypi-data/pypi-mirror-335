"""abc [`Module`].

Contains abstract classes and methods for creating features.

Includes:
- `metaclass` [`class`] for handling MRO anamolies and enforce structure rules applicable to any feature.
- `feature` [`class`] for creating features.
- `endpoint` [`decorator`] for marking a class as the final endpoint.
- `abstract` [`decorator`] for creating abstract features.
- `abstract_fmethod` [`decorator`] for marking methods as abstract in abstract features.
- `requires` [`decorator`] for documenting feature requirements of any method as well as a runtime check.
- `validate_features` [`function`] to validate implementation of features present in a class.
- `feature_compatibility` [`function`] to check and warn about potential errors in all code features present.
- `feature_info` [`function`] to get information about all or specific feature(s).
- `optimize` [`function`] to optimize multiple inheritable features into an optimal order to avoid MRO issues.
"""


import abc
import typing
import dataclasses


@dataclasses.dataclass
class CompositionAnalysisResult:
    """Data class for storing composition analysis result."""
    feature: str
    methods: typing.FrozenSet[str]
    type: typing.Literal['feature', 'abstract-feature']


class metaclass(abc.ABCMeta):
    """A default metaclass for `feature` abstract class.
    
    Automatically handles any Method Resolution Order (mro) anamolies and
    enforces strict rules to avoid implementing `__init__` method in feature
    definitions.

    Responsibilities:
    - Manage feature registry
    - Enforce initialization restrictions
    - Resolve diamond inheritence issues
    - Track feature dependencies
    """
    _feature_registry: typing.ClassVar[typing.Dict[str, typing.Type]]
    _dependency_graph: typing.ClassVar[typing.Dict[str, typing.Set[str]]]

    def __new__(mcls, name: str, bases: typing.Tuple[typing.Type, ...], namespace: typing.Dict[str, typing.Any], /, **kwargs): ...

    @classmethod
    def features(mcls) -> typing.Dict[str, typing.Set[str]]:
        """Returns a comprehensive list of all available features."""

    @classmethod
    def dependency_graph(mcls) -> typing.Dict[str, typing.Set[str]]:
        """Returns the dependency graph of all features."""

class feature(abc.ABC, metaclass=metaclass):
    """feature [`Abstract Class`].
    
    Any feature must inherit this class to create a `feature` implementation.

    :
    - Cannot define `__init__`
    - Can be composed together
    - Have automatic MRO resolution
    - Can depend on other features.

    Example usage:
    ```python
    # logging feature
    class Logging(feature):
        def log(self, *args, **kwargs) -> None:
            # some logic here
            pass
    
    # printing feature
    class Printing(feature):
        def print_in_bytes_form(self) -> None:
            # some logic here
            pass
    
    # an aggregate feature (inheriting from other features)
    class TerminalLogger(Logging, Printing, feature):
        # Some implementations here
        pass
    ```

    Note that all the above classes cannot define a `__init__` method.
    For the final endpoint class which will inherit a number of features
    and has the final code that does something, use the `endpoint`
    keyword argument while class definition.

    ```python
    class Main(Logging, Printing, TerminalLogger, endpoint=True):
        def __init__(self) -> None: ... # valid
    ```
    """

    _feature_name: typing.ClassVar[str]
    _feature_dependencies: typing.ClassVar[typing.Set[str]]
    _abstract_feature: typing.ClassVar[bool]

    def __init__(self) -> None:
        """If this is a class that inherits from `feature` abstract class
        directly or indirectly and does not contain the `endpoint`
        keyword argument, will raise a `TypeError`."""

    @classmethod
    def dependencies(cls, type: typing.Literal['self', 'all'] = 'self') -> typing.Set[str]:
        """Returns a set of dependencies (features) of this feature if `type` is
        set to 'self' which is default.
        
        Returns all dependencies of this feature (direct or indirect) if `type` is set
        to 'all'.
        """

    @classmethod
    def composition_analysis(cls, target: typing.Type) -> CompositionAnalysisResult:
        """Analyze whether a target class correctly implements this feature."""


CLASS = typing.TypeVar('CLASS')


abstract = abc.abstractmethod


_FeatureType: typing.TypeAlias = typing.Type[feature]
P = typing.ParamSpec("P")
R = typing.TypeVar('R')


def requires(*features: _FeatureType) -> typing.Callable[[typing.Callable[P, R]], typing.Callable[P, R]]:
    """This decorator marks a method as requiring certain features to be present.
    
    Usage:
    ```python
    class SomeClass:
        @requires(feature1, feature2)
        def process(self) -> None: ...
    ```
    """


def validate(cls: typing.Type) -> bool:
    """Validate that a class correctly implements all of its features. Prints warnings for each issue."""


@dataclasses.dataclass
class FeatureInfo:
    """Info about a feature class."""
    name: str
    direct_dependencies: typing.FrozenSet[str]
    all_dependencies: typing.FrozenSet[str]
    public_methods: typing.FrozenSet[str]
    docstring: typing.Union[str, None]
    is_abstract: bool


@dataclasses.dataclass
class AllFeaturesInfo:
    """Info about all registered features."""
    all_features: typing.FrozenSet[str]
    dependency_graph: typing.Dict[str, typing.FrozenSet[str]]


@typing.overload
def feature_info(cls: typing.Type[feature]) -> FeatureInfo:
    """Get information about a feature class."""
@typing.overload
def feature_info() -> AllFeaturesInfo:
    """Get information about all features that are registered."""


_cls_1 = typing.TypeVar('_cls_1')
_cls_2 = typing.TypeVar('_cls_2')
_cls_3 = typing.TypeVar('_cls_3')
_cls_4 = typing.TypeVar('_cls_4')
_cls_5 = typing.TypeVar('_cls_5')
_cls_6 = typing.TypeVar('_cls_6')
_cls_7 = typing.TypeVar('_cls_7')
_cls_8 = typing.TypeVar('_cls_8')
_cls_9 = typing.TypeVar('_cls_9')
_cls_10 = typing.TypeVar('_cls_10')


@typing.overload
def optimize(cls1: _cls_1, /) -> typing.Tuple[_cls_1]:
    """Optimizes the inheritence order to minimize MRO conflicts.
    
    Uses a topological sort based on Kahn's algorithm to ensure a valid
    linearization of the inheritence hierarchy.

    Usage:
    ```python
    class SomeClass(*optimize(feature1, feature1, ...AnyClassHere)): pass
    ```
    """


@typing.overload
def optimize(cls1: _cls_1, cls2: _cls_2, /) -> typing.Tuple[_cls_1, _cls_2]:
    """Optimizes the inheritence order to minimize MRO conflicts.
    
    Uses a topological sort based on Kahn's algorithm to ensure a valid
    linearization of the inheritence hierarchy.

    Usage:
    ```python
    class SomeClass(*optimize(feature1, feature1, ...AnyClassHere)): pass
    ```
    """


@typing.overload
def optimize(cls1: _cls_1, cls2: _cls_2, cls3: _cls_3, /) -> typing.Tuple[_cls_1, _cls_2, _cls_3]:
    """Optimizes the inheritence order to minimize MRO conflicts.
    
    Uses a topological sort based on Kahn's algorithm to ensure a valid
    linearization of the inheritence hierarchy.

    Usage:
    ```python
    class SomeClass(*optimize(feature1, feature1, ...AnyClassHere)): pass
    ```
    """


@typing.overload
def optimize(cls1: _cls_1, cls2: _cls_2, cls3: _cls_3, cls4: _cls_4, /) -> typing.Tuple[_cls_1, _cls_2, _cls_3, _cls_4]:
    """Optimizes the inheritence order to minimize MRO conflicts.
    
    Uses a topological sort based on Kahn's algorithm to ensure a valid
    linearization of the inheritence hierarchy.

    Usage:
    ```python
    class SomeClass(*optimize(feature1, feature1, ...AnyClassHere)): pass
    ```
    """


@typing.overload
def optimize(cls1: _cls_1, cls2: _cls_2, cls3: _cls_3, cls4: _cls_4, cls5: _cls_5, /) -> typing.Tuple[_cls_1, _cls_2, _cls_3, _cls_4, _cls_5]:
    """Optimizes the inheritence order to minimize MRO conflicts.
    
    Uses a topological sort based on Kahn's algorithm to ensure a valid
    linearization of the inheritence hierarchy.

    Usage:
    ```python
    class SomeClass(*optimize(feature1, feature1, ...AnyClassHere)): pass
    ```
    """


@typing.overload
def optimize(cls1: _cls_1, cls2: _cls_2, cls3: _cls_3, cls4: _cls_4, cls5: _cls_5, cls6: _cls_6, /) -> typing.Tuple[_cls_1, _cls_2, _cls_3, _cls_4, _cls_5, _cls_6]:
    """Optimizes the inheritence order to minimize MRO conflicts.
    
    Uses a topological sort based on Kahn's algorithm to ensure a valid
    linearization of the inheritence hierarchy.

    Usage:
    ```python
    class SomeClass(*optimize(feature1, feature1, ...AnyClassHere)): pass
    ```
    """


@typing.overload
def optimize(cls1: _cls_1, cls2: _cls_2, cls3: _cls_3, cls4: _cls_4, cls5: _cls_5, cls6: _cls_6, cls7: _cls_7, /) -> typing.Tuple[_cls_1, _cls_2, _cls_3, _cls_4, _cls_5, _cls_6, _cls_7]:
    """Optimizes the inheritence order to minimize MRO conflicts.
    
    Uses a topological sort based on Kahn's algorithm to ensure a valid
    linearization of the inheritence hierarchy.

    Usage:
    ```python
    class SomeClass(*optimize(feature1, feature1, ...AnyClassHere)): pass
    ```
    """


@typing.overload
def optimize(cls1: _cls_1, cls2: _cls_2, cls3: _cls_3, cls4: _cls_4, cls5: _cls_5, cls6: _cls_6, cls7: _cls_7, cls8: _cls_8, /) -> typing.Tuple[_cls_1, _cls_2, _cls_3, _cls_4, _cls_5, _cls_6, _cls_7, _cls_8]:
    """Optimizes the inheritence order to minimize MRO conflicts.
    
    Uses a topological sort based on Kahn's algorithm to ensure a valid
    linearization of the inheritence hierarchy.

    Usage:
    ```python
    class SomeClass(*optimize(feature1, feature1, ...AnyClassHere)): pass
    ```
    """


@typing.overload
def optimize(cls1: _cls_1, cls2: _cls_2, cls3: _cls_3, cls4: _cls_4, cls5: _cls_5, cls6: _cls_6, cls7: _cls_7, cls8: _cls_8, cls9: _cls_9, /) -> typing.Tuple[_cls_1, _cls_2, _cls_3, _cls_4, _cls_5, _cls_6, _cls_7, _cls_8, _cls_9]:
    """Optimizes the inheritence order to minimize MRO conflicts.
    
    Uses a topological sort based on Kahn's algorithm to ensure a valid
    linearization of the inheritence hierarchy.

    Usage:
    ```python
    class SomeClass(*optimize(feature1, feature1, ...AnyClassHere)): pass
    ```
    """


@typing.overload
def optimize(cls1: _cls_1, cls2: _cls_2, cls3: _cls_3, cls4: _cls_4, cls5: _cls_5, cls6: _cls_6, cls7: _cls_7, cls8: _cls_8, cls9: _cls_9, cls10: _cls_10, /) -> typing.Tuple[_cls_1, _cls_2, _cls_3, _cls_4, _cls_5, _cls_6, _cls_7, _cls_8, _cls_9, _cls_10]:
    """Optimizes the inheritence order to minimize MRO conflicts.
    
    Uses a topological sort based on Kahn's algorithm to ensure a valid
    linearization of the inheritence hierarchy.

    Usage:
    ```python
    class SomeClass(*optimize(feature1, feature1, ...AnyClassHere)): pass
    ```
    """


@typing.overload
def optimize(*classes) -> typing.Tuple[typing.Any, ...]:
    """Optimizes the inheritence order to minimize MRO conflicts.
    
    Uses a topological sort based on Kahn's algorithm to ensure a valid
    linearization of the inheritence hierarchy.

    Usage:
    ```python
    class SomeClass(*optimize(feature1, feature1, ...AnyClassHere)): pass
    ```
    """



__all__: typing.List[str] = ['metaclass', 'feature', 'endpoint', 'abstract',
                             'abstract_fmethod', 'requires', 'validate_features',
                             'feature_compatibility', 'feature_info', 'optimize']