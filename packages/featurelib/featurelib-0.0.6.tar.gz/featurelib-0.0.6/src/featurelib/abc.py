

# @contains all abstract methodologies for
# - creating features and maintaining them.

import abc
import typing
import inspect
import warnings
import functools
import dataclasses


# @analyis result (to be used later)
@dataclasses.dataclass
class CompositionAnalysisResult:
    feature: str
    methods: typing.FrozenSet[str]
    type: typing.Literal['feature', 'abstract-feature']

# @metaclass that helps fixing MRO and handles
# - features and final implementation differently.

class metaclass(abc.ABCMeta):

    # @registry to track all feature classes
    _feature_registry: typing.ClassVar[typing.Dict[str, typing.Type]] = {}

    # @dependency graph for quick loop
    _dependency_graph: typing.ClassVar[typing.Dict[str, typing.Set[str]]] = {}


    # @custom __new__ method to enforce logic as per
    # - requirement.
    def __new__(mcls, name, bases, namespace, /, **kwargs):

        is_endpoint = kwargs.pop('endpoint', False)
        is_abstract = kwargs.pop('abstract', False)

        # @filter out any direct 'feature' base classes when a class
        # - already inherits from a 'feature' subclass.
        feature_subclasses = [b for b in bases if isinstance(b, metaclass) and b is not feature]

        if feature_subclasses and feature in bases:
            # @remove feature from bases to avoid diamond inheritence
            bases = tuple(b for b in bases if b is not feature)

        # @call the default __new__
        cls = super().__new__(mcls, name, bases, namespace, **kwargs)
        
        # @register feature (but not `feature` class itself or endpoint classes)
        if name != 'feature' and not namespace.get('_abstract_feature', False) and not is_endpoint and not is_abstract:
            mcls._feature_registry[name] = cls

            # @set feature_name and feature_dependencies
            cls._feature_name = name
            cls._feature_dependencies = {
                typing.cast(typing.Type[feature], b)._feature_name for b in bases if isinstance(b, type) and hasattr(b, '_feature_name') and b._feature_name != 'feature'
            }

            mcls._dependency_graph[name] = cls._feature_dependencies
        
        if '__init__' in namespace and not is_endpoint:
            raise TypeError(
                f"class {name} cannot implement __init__ as it is defined as a "
                "'feature' for some larger final implementation (endpoint)"
            )

        return cls

    # @method to get all features
    @classmethod
    def features(mcls) -> typing.Dict[str, typing.Type]:
        return mcls._feature_registry.copy()


    # @method to generate a feature dependency map/graph
    @classmethod
    def dependency_graph(mcls) -> typing.Dict[str, typing.Set[str]]:
        return mcls._dependency_graph.copy()


# @feature class that helps separate actual implementations
# - of complex operations away from the final implementation.

class feature(abc.ABC, metaclass=metaclass):


    _feature_name: typing.ClassVar[str]
    _feature_dependencies: typing.ClassVar[typing.Set[str]]
    _abstract_feature: typing.ClassVar[bool] = False

    # @a method to get dependencies
    @classmethod
    def dependencies(cls, type: typing.Literal['self', 'all'] = 'self') -> typing.Set[str]:
        if type == 'self':
            if hasattr(cls, '_feature_dependencies'):
                return cls._feature_dependencies.copy()
            return set()
        else:
            result: typing.Set[str] = set()
            meta = cls.__class__

            def add(name: str) -> None:
                if name in result:
                    return
                
                result.add(name)
                dependencies = meta.dependency_graph().get(name, set())
                for dep in dependencies:
                    add(dep)
            
            if hasattr(cls, '_feature_name'):
                add(cls._feature_name)
            
            return result


    # @composition
    @classmethod
    def composition_analysis(cls, target: typing.Type) -> CompositionAnalysisResult:
        methods = {name for name, _ in inspect.getmembers(cls, predicate=inspect.isfunction) if not name.startswith('_')}
        type = 'feature' if not inspect.isabstract(cls) else 'abstract-feature'
        return CompositionAnalysisResult(
            feature=cls.__name__,
            methods=frozenset(methods),
            type=type,
        )


abstract = abc.abstractmethod


# @a decorator that marks a method as requiring a certain features
# - to be present.

def requires(*features: typing.Type):
    def decorator(function):
        function._required_features = features
        @functools.wraps(function)
        def wrapper(self, *args, **kwargs):
            for feature in features:
                if not isinstance(self, feature):
                    raise TypeError(f"Method {function.__name__} requires {feature.__name__} feature.")
            return function(self, *args, **kwargs)
        
        # Store, required features for introspection
        wrapper._required_features = features
        return wrapper
    return decorator


def validate(cls: typing.Type) -> bool:
    # @instead of returning anything at all, just warn the user
    feature_bases = [base for base in cls.__bases__
                     if isinstance(base, type) and issubclass(base, feature) and base is not feature]
    
    # @if no inheritence is found for any feature, raise RuntimeError and exit.
    if not feature_bases:
        raise RuntimeError(f"{cls.__name__} does not inherit any features.")
    
    # @if inheritence is found but it is not an endpoint, show an warning
    # - as this function must be used with endpoints.
    if not getattr(cls, '_is_feature_endpoint', False):
        warnings.warn(f'{cls.__name__} is not an endpoint.', RuntimeWarning, 2)
        return False


    # @check for diamond inheritence issues
    seen = set()
    duplicate = set()

    for base in feature_bases:
        deps = base.dependencies('all')
        duplicates = seen.intersection(deps)
        duplicate.update(duplicates)
        seen.update(deps)


    # @return warning, if duplicate features are found in inheritence
    if duplicate:
        warnings.warn(f"Diamond inheritence detected. {', '.join(duplicate)} are included multiple times in the inheritance hierarchy.", SyntaxWarning, 2)
        return False


    # Check method compatibility
    methods = {}
    for base in feature_bases:
        base_methods = base.composition_analysis(cls).methods
        for method in base_methods:
            if method in methods:
                warnings.warn(f"Method '{method}' is defined in multiple features: {methods[method]} and {base.__name__}", SyntaxWarning, 2)
                return False
            else:
                methods[method] = base.__name__


    # check for missing abstract methods
    abstract_methods = []
    for base in feature_bases:
        if getattr(base, '_abstract_feature', False):
            for name, method in inspect.getmembers(base, predicate=inspect.isfunction):
                if getattr(method, '__isabstractmethod__', False) and not hasattr(cls, name):
                    abstract_methods.append((name, base.__name__))
    
    # @if abstract methods are found to be not implemented in cls,
    # - and cls is not an abstract feature or not an abstract class:
    if abstract_methods and (not hasattr(cls, '_abstract_feature') or not inspect.isabstract(cls)):
        for name, base in abstract_methods:
            warnings.warn(f"{cls.__name__} does not implement required abstract method '{name}' from {base}.")
            return False

    # @check for method requirements
    for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
        if hasattr(method, '_required_features'):
            for req_feature in method._required_features:
                if not issubclass(cls, req_feature):
                    warnings.warn(f"Method '{name}' requires feature '{req_feature.__name__}' which is not included in the class hierarchy.", SyntaxWarning, 2)
                    return False


    # @check for __init__ method in non endpoints
    if hasattr(cls, '__init__') and not getattr(cls, '_is_feature_endpoint', False):
        # @check if __init__ is actually defined and not inherited
        if cls.__init__.__qualname__.split('.')[0] == cls.__name__:
            warnings.warn(f"{cls.__name__} implements '__init__' method but is not marked as an endpoint.")
            return False

    return True


@dataclasses.dataclass
class FeatureInfo:
    name: str
    direct_dependencies: typing.FrozenSet[str]
    all_dependencies: typing.FrozenSet[str]
    public_methods: typing.FrozenSet[str]
    docstring: typing.Union[str, None]
    is_abstract: bool


@dataclasses.dataclass
class AllFeaturesInfo:
    all_features: typing.FrozenSet[str]
    dependency_graph: typing.Dict[str, typing.FrozenSet[str]]


def feature_info(cls: typing.Union[typing.Type[feature], None] = None) -> typing.Union[FeatureInfo, AllFeaturesInfo]:
    meta = metaclass

    if cls is None:
        return AllFeaturesInfo(
            all_features=frozenset(meta.features().keys()),
            dependency_graph={k: frozenset(v) for k, v in meta.dependency_graph().items()}
        )

    if not (isinstance(cls, type) and issubclass(cls, feature)):
        raise TypeError(f"{cls} is not a feature subclass.")
    
    return FeatureInfo(
        name=cls.__name__,
        direct_dependencies=frozenset(cls.dependencies()),
        all_dependencies=frozenset(cls.dependencies('all')),
        public_methods=frozenset([name for name, _ in inspect.getmembers(cls, predicate=inspect.isfunction) if not name.startswith('_')]),
        docstring=inspect.getdoc(cls),
        is_abstract=getattr(cls, '_abstract_feature', False)
    )



def optimize(*classes):
    # Separate feature classes from non-feature classes
    feature_classes = [cls for cls in classes if isinstance(cls, type) and issubclass(cls, feature)]
    non_feature_classes = [cls for cls in classes if cls not in feature_classes]
    
    # Return early if no feature classes
    if not feature_classes:
        return classes
    
    # Build complete inheritance hierarchy
    # Include all relevant classes, not just those in the input list
    all_classes = set(feature_classes)
    
    # Map of class -> all its base feature classes (direct and indirect)
    all_bases = {}
    
    def get_all_feature_bases(cls):
        if cls in all_bases:
            return all_bases[cls]
        
        result = set()
        for base in cls.__bases__:
            if base is feature:
                continue  # Skip the main feature class
            if isinstance(base, type) and issubclass(base, feature):
                result.add(base)
                all_classes.add(base)  # Ensure this base is included
                result.update(get_all_feature_bases(base))
        
        all_bases[cls] = result
        return result
    
    # Collect all base classes for each input class
    for cls in feature_classes:
        get_all_feature_bases(cls)
    
    # Convert to list for consistent ordering operations
    all_classes = list(all_classes)
    
    # Function to compute C3 linearization (Python's MRO algorithm)
    def compute_mro(cls):
        # Base case: cls has no bases or only feature as base
        bases = [base for base in cls.__bases__ 
                if base is not feature and isinstance(base, type) and issubclass(base, feature)]
        if not bases:
            return [cls]
        
        # Get MROs of all bases
        base_mros = [compute_mro(base) for base in bases]
        
        # Merge the MROs
        result = [cls]
        
        # C3 linearization algorithm
        while any(mro for mro in base_mros):
            # Find a candidate for the next class
            for mro in base_mros:
                if not mro:
                    continue
                
                candidate = mro[0]
                # Check if candidate is not in the tail of any other MRO
                if all(candidate not in m[1:] for m in base_mros if m):
                    # Add to result and remove from all MROs
                    result.append(candidate)
                    for m in base_mros:
                        if m and m[0] == candidate:
                            m.pop(0)
                    break
            else:
                # If we get here, there's a cycle or conflict in the inheritance
                raise TypeError(
                    f"Cannot create a consistent method resolution order (MRO) for {cls.__name__}"
                )
        
        return result
    
    # Compute MRO for each class in the input
    try:
        # Start from "leaf" classes (those that aren't bases for any other classes)
        leaf_classes = set(all_classes)
        for cls in all_classes:
            for base in get_all_feature_bases(cls):
                if base in leaf_classes:
                    leaf_classes.remove(base)
        
        # If no leaf classes (circular dependencies), use all classes
        if not leaf_classes:
            leaf_classes = set(all_classes)
        
        # Compute MROs for leaf classes
        mros = {}
        for cls in leaf_classes:
            mros[cls] = compute_mro(cls)
        
        # Now collect classes in the correct order
        result = []
        for cls in feature_classes:
            if cls in mros:
                # Add classes from the MRO that are in the input
                for c in mros[cls]:
                    if c in feature_classes and c not in result:
                        result.append(c)
        
        # Add any missing classes from the input
        missing = [cls for cls in feature_classes if cls not in result]
        result.extend(missing)
        
        return non_feature_classes + result
    
    except TypeError as e:
        # On MRO conflict, log warning and return classes in a safe order
        warnings.warn(
            f"MRO conflict detected: {str(e)}. "
            "Returning a potentially safe ordering, but inheritance issues may occur.",
            RuntimeWarning
        )
        
        # Try to create a safe ordering based on inheritance depth
        depth_map = {}
        for cls in all_classes:
            depth_map[cls] = len(get_all_feature_bases(cls))
        
        # Sort by inheritance depth (most derived classes first)
        ordered_classes = sorted(feature_classes, key=lambda cls: -depth_map[cls])
        return tuple(non_feature_classes + ordered_classes)


__all__ = ['metaclass', 'feature', 'endpoint', 'abstract',
           'abstract_fmethod', 'requires', 'validate_features',
           'feature_compatibility', 'feature_info', 'optimize']