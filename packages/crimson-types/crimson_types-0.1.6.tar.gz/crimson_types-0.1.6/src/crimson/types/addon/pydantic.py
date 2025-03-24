from typing import Any, Generator, cast, Type
from pydantic import create_model


class PydanticCompatible:
    """
    See the [link](https://github.com/crimson206/types/blob/main/example/addon/pydantic_compatible.ipynb)
    """

    validate_base_index: int = 0

    @classmethod
    def __get_validators__(cls) -> Generator:
        yield cls.validate

    @classmethod
    def validate(cls, value: Any, _):
        try:
            DynamicTester = create_model(
                "DynamicTester", base=(cls.__bases__[cls.validate_base_index], ...)
            )
        except AttributeError as e:
            e
            raise Exception(
                "The innertype of your custom type class must be placed as the first base of the type class as default. If you want to place it another position, specify the position using `validate_base_index`. See the link, https://github.com/crimson206/types/blob/main/example/addon/pydantic_compatible.ipynb"
            )

        DynamicTester(base=value)
        return cast(Type[cls], value)  # type: ignore
