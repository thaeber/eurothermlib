from typing import Any, ClassVar

import pint


class TypedQuantity(pint.Quantity):
    __dimensionality__: ClassVar[str | None] = None

    def __class_getitem__(cls, item):
        return type(cls.__name__, (cls,), {"__dimensionality__": item})

    def __init__(self, *args, **kwargs):
        if not self.check(self.__dimensionality__):  # type: ignore
            raise pint.DimensionalityError(
                units2=self.__dimensionality__,
                units1=self.units,
                extra_msg=f' (value = {self})',
            )

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: Any) -> Any:
        # your validation logic here
        print(f"Validating {v} as {cls.__dimensionality__}")
        return v
