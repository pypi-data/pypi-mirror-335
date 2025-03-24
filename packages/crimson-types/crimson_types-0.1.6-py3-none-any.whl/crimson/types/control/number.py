"""
Define different custom number types.

The same functionality can be implemented in different ways,

to provide more options, and open the more various and wider possibilities.
"""

from crimson.types.addon.intelli_type import IntelliHolder, T
from crimson.types.addon.annotated import AnnotatedType


class IntRange(AnnotatedType, int, IntelliHolder[T]):
    """
    Int Type, with additional information injection capability.

    Example:
        - [link](https://github.com/crimson206/types/blob/main/example/control/number.ipynb) to example notebook
    """


class FloatRange(
    AnnotatedType,
    float,
    IntelliHolder[T],
):
    """
    Float Type, with additional information injection capability.

    Example:
        - [link](https://github.com/crimson206/types/blob/main/example/control/highlighted/number.ipynb.md) to example notebook
    """
