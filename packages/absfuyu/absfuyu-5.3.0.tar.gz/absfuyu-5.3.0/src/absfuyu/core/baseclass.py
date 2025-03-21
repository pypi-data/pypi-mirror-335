"""
Absfuyu: Core
-------------
Bases for other features

Version: 5.2.0
Date updated: 11/03/2025 (dd/mm/yyyy)
"""

# Module Package
# ---------------------------------------------------------------------------
__all__ = [
    # Color
    "CLITextColor",
    # Support
    "MethodNPropertyList",
    "MethodNPropertyResult",
    # Mixins
    "ShowAllMethodsMixin",
    "AutoREPRMixin",
    # Class
    "BaseClass",
    # Metaclass
    "PositiveInitArgsMeta",
]

# Library
# ---------------------------------------------------------------------------
from typing import ClassVar, Literal, NamedTuple, Self


# Color
# ---------------------------------------------------------------------------
class CLITextColor:
    """Color code for text in terminal"""

    WHITE = "\x1b[37m"
    BLACK = "\x1b[30m"
    BLUE = "\x1b[34m"
    GRAY = "\x1b[90m"
    GREEN = "\x1b[32m"
    RED = "\x1b[91m"
    DARK_RED = "\x1b[31m"
    MAGENTA = "\x1b[35m"
    YELLOW = "\x1b[33m"
    RESET = "\x1b[39m"


# Mixins
# ---------------------------------------------------------------------------
# @versionadded("5.1.0")
class MethodNPropertyList(NamedTuple):
    """
    Contains lists of methods, classmethods, staticmethods, and properties of a class.

    Parameters
    ----------
    methods : list[str]
        List contains method names of a class.

    classmethods : list[str]
        List contains classmethod names of a class.

    staticmethods : list[str]
        List contains staticmethod names of a class.

    properties : list[str]
        List contains property names of a class.
    """

    methods: list[str]
    classmethods: list[str]
    staticmethods: list[str]
    properties: list[str]

    def __repr__(self) -> str:
        """
        Only shows list with items in repr

        *This overwrites ``NamedTuple.__repr__()``*
        """
        # return super().__repr__()
        cls_name = self.__class__.__name__
        out = []
        sep = ", "
        for x in self._fields:
            if len(getattr(self, x)) > 0:
                out.append(f"{x}={repr(getattr(self, x))}")
        return f"{cls_name}({sep.join(out)})"

    def is_empty(self) -> bool:
        """
        Checks if all lists (methods, classmethods, staticmethods, properties) are empty.
        """
        # for x in self:
        #     if len(x) > 0:
        #         return False
        # return True
        return all(len(getattr(self, x)) == 0 for x in self._fields)

    def pack(
        self,
        include_method: bool = True,
        include_classmethod: bool = True,
        classmethod_indicator: str = "<classmethod>",
        include_staticmethod: bool = True,
        staticmethod_indicator: str = "<staticmethod>",
    ) -> Self:
        """
        Combines methods, classmethods, and staticmethods into one list.

        Parameters
        ----------
        include_method : bool, optional
            Whether to include methods in the output, by default ``True``

        include_classmethod : bool, optional
            Whether to include classmethods in the output, by default ``True``

        classmethod_indicator : str, optional
            A string used to mark classmethod in the output. This string is appended
            to the name of each classmethod to visually differentiate it from regular
            instance methods, by default ``"<classmethod>"``

        include_staticmethod : bool, optional
            Whether to include staticmethods in the output, by default ``True``

        staticmethod_indicator : str, optional
            A string used to mark staticmethod in the output. This string is appended
            to the name of each staticmethod to visually differentiate it from regular
            instance methods, by default ``"<staticmethod>"``

        Returns
        -------
        Self
            MethodNPropertyList (combined methods lists)


        Example:
        --------
        >>> test = MethodNPropertyList(["a"], ["b"], ["c"], ["d"])
        >>> test.pack()
        MethodNPropertyList(methods=['a', 'b <classmethod>', 'c <staticmethod>'], properties=['d'])
        """
        new_methods_list = []

        # Method
        if include_method:
            new_methods_list.extend(self.methods)

        # Classmethod
        if include_classmethod:
            new_methods_list.extend(
                [f"{x} {classmethod_indicator}".strip() for x in self.classmethods]
            )

        # Staticmethod
        if include_staticmethod:
            new_methods_list.extend(
                [f"{x} {staticmethod_indicator}".strip() for x in self.staticmethods]
            )

        return self.__class__(new_methods_list, [], [], self.properties)

    def sort(self, reverse: bool = False) -> Self:
        """
        Sorts every element in each method list.

        Parameters
        ----------
        reverse : bool, optional
            Descending order, by default ``False``

        Returns
        -------
        Self
            Sorted.


        Example:
        --------
        >>> test = MethodNPropertyList(["b", "a"], ["d", "c"], ["f", "e"], ["h", "g"])
        >>> test.sort()
        MethodNPropertyList(methods=['a', 'b'], classmethods=['c', 'd'], staticmethods=['e', 'f'], properties=['g', 'h'])

        >>> test.pack().sort()
        MethodNPropertyList(methods=['a', 'b', 'c <classmethod>', 'd <classmethod>', 'e <staticmethod>', 'f <staticmethod>'], properties=['g', 'h'])
        """
        sorted_vals = [
            sorted(getattr(self, field), reverse=reverse) for field in self._fields
        ]
        # return self._make(sorted_vals)
        return self.__class__(*sorted_vals)


# @versionadded("5.1.0")
class MethodNPropertyResult(dict[str, MethodNPropertyList]):
    """
    All methods and properties of a class and its parent classes.

    Sorted in ascending order.
    """

    _LINELENGTH: ClassVar[int] = 88

    def _merge_value(
        self,
        value_name: Literal["methods", "classmethods", "staticmethods", "properties"],
    ) -> list[str]:
        """
        Merge all specified values from the dictionary.

        Parameters
        ----------
        value_name : Literal["methods", "classmethods", "staticmethods", "properties"]
            The type of value to merge.

        Returns
        -------
        list[str]
            A list of merged values.
        """
        merged = []
        for _, methods_n_properties in self.items():
            if value_name in methods_n_properties._fields:
                merged.extend(getattr(methods_n_properties, value_name))
        return merged

    def flatten_value(self) -> MethodNPropertyList:
        """
        Merge all attributes of ``dict``'s values into one ``MethodNPropertyList``.

        Returns
        -------
        MethodNPropertyList
            Flattened value


        Example:
        --------
        >>> test = MethodNPropertyResult(
        ...     ABC=MethodNPropertyList(["a"], ["b"], ["c"], ["d"]),
        ...     DEF=MethodNPropertyList(["e"], ["f"], ["g"], ["h"]),
        ... )
        >>> test.flatten_value()
        MethodNPropertyList(methods=["a", "e"], classmethods=["b", "f"], staticmethods=["c", "g"], properties=["d", "h"])
        """
        res = []
        for x in ["methods", "classmethods", "staticmethods", "properties"]:
            res.append(self._merge_value(x))  # type: ignore
        return MethodNPropertyList._make(res)

    def pack_value(
        self,
        include_method: bool = True,
        include_classmethod: bool = True,
        classmethod_indicator: str = "<classmethod>",
        include_staticmethod: bool = True,
        staticmethod_indicator: str = "<staticmethod>",
    ) -> Self:
        """
        Join method, classmethod, staticmethod into one list for each value.

        Parameters
        ----------
        include_method : bool, optional
            Whether to include method in the output, by default ``True``

        include_classmethod : bool, optional
            Whether to include classmethod in the output, by default ``True``

        classmethod_indicator : str, optional
            A string used to mark classmethod in the output. This string is appended
            to the name of each classmethod to visually differentiate it from regular
            instance methods, by default ``"<classmethod>"``

        include_staticmethod : bool, optional
            Whether to include staticmethod in the output, by default ``True``

        staticmethod_indicator : str, optional
            A string used to mark staticmethod in the output. This string is appended
            to the name of each staticmethod to visually differentiate it from regular
            instance methods, by default ``"<staticmethod>"``

        Returns
        -------
        Self
            MethodNPropertyResult with packed value.


        Example:
        --------
        >>> test = MethodNPropertyResult(
        ...     ABC=MethodNPropertyList(["a"], ["b"], ["c"], ["d"]),
        ...     DEF=MethodNPropertyList(["e"], ["f"], ["g"], ["h"]),
        ... )
        >>> test.pack_value()
        {
            "ABC": MethodNPropertyList(
                methods=["a", "b <classmethod>", "c <staticmethod>"], properties=["d"]
            ),
            "DEF": MethodNPropertyList(
                methods=["e", "f <classmethod>", "g <staticmethod>"], properties=["h"]
            ),
        }
        """
        for class_name, method_prop_list in self.items():
            self[class_name] = method_prop_list.pack(
                include_method=include_method,
                include_classmethod=include_classmethod,
                classmethod_indicator=classmethod_indicator,
                include_staticmethod=include_staticmethod,
                staticmethod_indicator=staticmethod_indicator,
            )
        return self

    def prioritize_value(
        self,
        value_name: Literal[
            "methods", "classmethods", "staticmethods", "properties"
        ] = "methods",
    ) -> dict[str, list[str]]:
        """
        Prioritize which field of value to show.

        Parameters
        ----------
        value_name : Literal["methods", "classmethods", "staticmethods", "properties"], optional
            The type of value to prioritize, by default ``"methods"``

        Returns
        -------
        dict[str, list[str]]
            A dictionary with prioritized values.


        Example:
        --------
        >>> test = MethodNPropertyResult(
        ...     ABC=MethodNPropertyList(["a"], ["b"], ["c"], ["d"]),
        ...     DEF=MethodNPropertyList(["e"], ["f"], ["g"], ["h"]),
        ... )
        >>> test.prioritize_value("methods")
        {'ABC': ['a'], 'DEF': ['e']}
        >>> test.prioritize_value("classmethods")
        {'ABC': ['b'], 'DEF': ['f']}
        >>> test.prioritize_value("staticmethods")
        {'ABC': ['c'], 'DEF': ['g']}
        >>> test.prioritize_value("properties")
        {'ABC': ['d'], 'DEF': ['h']}
        """
        result = {}
        for k, v in self.items():
            result[k] = getattr(v, value_name, v.methods)
        return result

    def print_output(
        self,
        where_to_print: Literal["methods", "properties"] = "methods",
        print_in_one_column: bool = False,
    ) -> None:
        """
        Beautifully print the result.

        Parameters
        ----------
        where_to_print : Literal["methods", "properties"], optional
            Whether to print ``self.methods`` or ``self.properties``, by default ``"methods"``

        print_in_one_column : bool, optional
            Whether to print in one column, by default ``False``
        """

        print_func = print  # Can be extended with function parameter

        # Loop through each class base
        for order, (class_base, methods_n_properties) in enumerate(
            self.items(), start=1
        ):
            methods: list[str] = getattr(
                methods_n_properties, where_to_print, methods_n_properties.methods
            )
            mlen = len(methods)  # How many methods in that class
            if mlen == 0:
                continue
            print_func(f"{order:02}. <{class_base}> | len: {mlen:02}")

            # Modify methods list
            max_method_name_len = max([len(x) for x in methods])
            if mlen % 2 == 0:
                p1, p2 = methods[: int(mlen / 2)], methods[int(mlen / 2) :]
            else:
                p1, p2 = methods[: int(mlen / 2) + 1], methods[int(mlen / 2) + 1 :]
                p2.append("")
            new_methods = list(zip(p1, p2))

            # print
            if print_in_one_column:
                # This print 1 method in one line
                for name in methods:
                    print(f"    - {name.ljust(max_method_name_len)}")
            else:
                # This print 2 methods in 1 line
                for x1, x2 in new_methods:
                    if x2 == "":
                        print_func(f"    - {x1.ljust(max_method_name_len)}")
                    else:
                        print_func(
                            f"    - {x1.ljust(max_method_name_len)}    - {x2.ljust(max_method_name_len)}"
                        )

            print_func("".ljust(self._LINELENGTH, "-"))


class ShowAllMethodsMixin:
    """
    Show all methods of the class and its parent class minus ``object`` class

    *This class is meant to be used with other class*


    Example:
    --------
    >>> class TestClass(ShowAllMethodsMixin):
    ...     def method1(self): ...
    >>> TestClass._get_methods_and_properties()
    {
        "ShowAllMethodsMixin": MethodNPropertyList(
            classmethods=[
                "_get_methods_and_properties",
                "show_all_methods",
                "show_all_properties",
            ]
        ),
        "TestClass": MethodNPropertyList(
            methods=["method1"]
        ),
    }
    """

    # @versionadded("5.1.0")
    @classmethod
    def _get_methods_and_properties(
        cls,
        skip_private_attribute: bool = True,
        include_private_method: bool = False,
    ) -> MethodNPropertyResult:
        """
        Class method to get all methods and properties of the class and its parent classes

        Parameters
        ----------
        skip_private_attribute : bool, optional
            Whether to include attribute with ``__`` (dunder) in the output, by default ``True``

        include_private_method : bool, optional
            Whether to include private method in the output, by default ``False``

        Returns
        -------
        MethodNPropertyResult
            A dictionary where keys are class names and values are tuples of method names and properties.
        """

        # MRO in reverse order
        classes = cls.__mro__[::-1]
        result = {}

        # For each class base in classes
        for base in classes:
            methods = []
            classmethods = []
            staticmethods = []
            properties = []

            # Dict items of base
            for name, attr in base.__dict__.items():
                # Skip private attribute
                if name.startswith("__") and skip_private_attribute:
                    continue

                # Skip private Callable
                if base.__name__ in name and not include_private_method:
                    continue

                # Methods
                if callable(attr):
                    if isinstance(attr, staticmethod):
                        staticmethods.append(name)
                    else:
                        methods.append(name)
                if isinstance(attr, classmethod):
                    classmethods.append(name)

                # Property
                if isinstance(attr, property):
                    properties.append(name)

                # Save to result
                result[base.__name__] = MethodNPropertyList(
                    methods=sorted(methods),
                    classmethods=sorted(classmethods),
                    staticmethods=sorted(staticmethods),
                    properties=sorted(properties),
                )

        return MethodNPropertyResult(result)

    @classmethod
    def show_all_methods(
        cls,
        print_result: bool = False,
        include_classmethod: bool = True,
        classmethod_indicator: str = "<classmethod>",
        include_staticmethod: bool = True,
        staticmethod_indicator: str = "<staticmethod>",
        include_private_method: bool = False,
    ) -> dict[str, list[str]]:
        """
        Class method to display all methods of the class and its parent classes,
        including the class in which they are defined in alphabetical order.

        Parameters
        ----------
        print_result : bool, optional
            Beautifully print the output, by default ``False``

        include_classmethod : bool, optional
            Whether to include classmethod in the output, by default ``True``

        classmethod_indicator : str, optional
            A string used to mark classmethod in the output. This string is appended
            to the name of each classmethod to visually differentiate it from regular
            instance methods, by default ``"<classmethod>"``

        include_staticmethod : bool, optional
            Whether to include staticmethod in the output, by default ``True``

        staticmethod_indicator : str, optional
            A string used to mark staticmethod in the output. This string is appended
            to the name of each staticmethod to visually differentiate it from regular
            instance methods, by default ``"<staticmethod>"``

        include_private_method : bool, optional
            Whether to include private method in the output, by default ``False``

        Returns
        -------
        dict[str, list[str]]
            A dictionary where keys are class names and values are lists of method names.
        """

        result = cls._get_methods_and_properties(
            include_private_method=include_private_method
        ).pack_value(
            include_classmethod=include_classmethod,
            classmethod_indicator=classmethod_indicator,
            include_staticmethod=include_staticmethod,
            staticmethod_indicator=staticmethod_indicator,
        )

        if print_result:
            result.print_output("methods")

        return result.prioritize_value("methods")

    @classmethod
    def show_all_properties(cls, print_result: bool = False) -> dict[str, list[str]]:
        """
        Class method to display all properties of the class and its parent classes,
        including the class in which they are defined in alphabetical order.

        Parameters
        ----------
        print_result : bool, optional
            Beautifully print the output, by default ``False``

        Returns
        -------
        dict[str, list[str]]
            A dictionary where keys are class names and values are lists of property names.
        """

        # result = cls.get_methods_and_properties().prioritize_value("properties")
        result = MethodNPropertyResult(
            {
                cls.__name__: MethodNPropertyList(
                    [],
                    [],
                    [],
                    cls._get_methods_and_properties().flatten_value().properties,
                )
            }
        )

        if print_result:
            result.print_output("properties")

        return result.prioritize_value("properties")


class AutoREPRMixin:
    """
    Generate ``repr()`` output as ``<class(param1=any, param2=any, ...)>``

    *This class is meant to be used with other class*


    Example:
    --------
    >>> class Test(AutoREPRMixin):
    ...     def __init__(self, param):
    ...         self.param = param
    >>> print(repr(Test(1)))
    Test(param=1)
    """

    def __repr__(self) -> str:
        """
        Generate a string representation of the instance's attributes.

        This function retrieves attributes from either the ``__dict__`` or
        ``__slots__`` of the instance, excluding private attributes (those
        starting with an underscore). The attributes are returned as a
        formatted string, with each attribute represented as ``"key=value"``.

        Convert ``self.__dict__`` from ``{"a": "b"}`` to ``a=repr(b)``
        or ``self.__slots__`` from ``("a",)`` to ``a=repr(self.a)``
        (excluding private attributes)
        """
        # Default output
        out = []
        sep = ", "  # Separator

        # Get attributes
        cls_dict = getattr(self, "__dict__", None)
        cls_slots = getattr(self, "__slots__", None)

        # Check if __dict__ exist and len(__dict__) > 0
        if cls_dict is not None and len(cls_dict) > 0:
            out = [
                f"{k}={repr(v)}"
                for k, v in self.__dict__.items()
                if not k.startswith("_")
            ]

        # Check if __slots__ exist and len(__slots__) > 0
        elif cls_slots is not None and len(cls_slots) > 0:
            out = [
                f"{x}={repr(getattr(self, x))}"
                for x in self.__slots__  # type: ignore
                if not x.startswith("_")
            ]

        # Return out
        return f"{self.__class__.__name__}({sep.join(out)})"


# Class
# ---------------------------------------------------------------------------
class BaseClass(ShowAllMethodsMixin, AutoREPRMixin):
    """Base class"""

    def __str__(self) -> str:
        return repr(self)

    def __format__(self, format_spec: str) -> str:
        """
        Formats the object according to the specified format.
        If no format_spec is provided, returns the object's string representation.
        (Currently a dummy function)

        Usage
        -----
        >>> print(f"{<object>:<format_spec>}")
        >>> print(<object>.__format__(<format_spec>))
        >>> print(format(<object>, <format_spec>))
        """

        return self.__str__()


# Metaclass
# ---------------------------------------------------------------------------
class PositiveInitArgsMeta(type):
    """Make sure that every args in a class __init__ is positive"""

    def __call__(cls, *args, **kwargs):
        # Check if all positional and keyword arguments are positive
        for arg in args:
            if isinstance(arg, (int, float)) and arg < 0:
                raise ValueError(f"Argument {arg} must be positive")
        for key, value in kwargs.items():
            if isinstance(value, (int, float)) and value < 0:
                raise ValueError(f"Argument {key}={value} must be positive")

        # Call the original __init__ method
        return super().__call__(*args, **kwargs)
