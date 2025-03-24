from typing import Generic, TypeVar

T = TypeVar("T")


class IntelliHolder(Generic[T]):
    """
    It is Generic[T] holder.

    You can inherit to your custom type class, and \n
    when you hover on your function, the function will show you \n
            - not only the name of your custom type,
            - but also it's inner type.

    Example:
        - [link](https://github.com/crimson206/types/blob/main/example/addon/intelli_type.ipynb) to example
    """
