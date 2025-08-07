# %%
from multiprocessing import Value
import re
import tokenize
from typing import Any, ClassVar, Type, TypeAlias

import pint
from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema


# %%
class TypedQuantity(pint.Quantity):
    __dimensionality__: ClassVar[str | None] = None

    def __class_getitem__(cls, item):
        return type(cls.__name__, (cls,), {"__dimensionality__": item})

    # def __init__(self, *args, **kwargs):
    #     if not self.check(self.__dimensionality__):  # type: ignore
    #         raise pint.DimensionalityError(
    #             units2=self.__dimensionality__,
    #             units1=self.units,
    #             extra_msg=f' (value = {self})',
    #         )

    def __new__(cls, *args, **kwargs):
        obj = pint.Quantity.__new__(pint.Quantity, *args, **kwargs)
        if not obj.check(cls.__dimensionality__):  # type: ignore
            raise pint.DimensionalityError(
                units2=cls.__dimensionality__,
                units1=obj.units,
                extra_msg=f' (value = {obj})',
            )
        return obj

    @staticmethod
    def parse_expression(input_string: str):
        if m := re.match(
            rf'(?P<number>{tokenize.Number}){tokenize.Whitespace}(?P<unit>(\[(.*)\])|(.*))',
            input_string,
        ):
            number = m.group('number')
            try:
                number = int(number)
            except ValueError:
                number = float(number)

            unit = m.group('unit')
            # if unit and (unit[0] == '[') and (unit[-1] == ']'):
            if unit and unit[0].startswith('[') and unit.endswith(']'):
                unit = unit[1:-1]

            return number, unit

        else:
            return None

    @classmethod
    def _validate(cls, source_value, units=None):
        ureg = pint.application_registry.get()
        if source_value is None:
            raise ValueError
        try:
            if units is not None:
                value = ureg(source_value, units=units)
            else:
                if isinstance(source_value, str):
                    # here we try to split the magnitude from the unit in case
                    # only a single unit is given, e.g. "20degC". This avoids
                    # an error with offset units where we cannot create a
                    # quantity via pint.Quantity("20.0degC"), but
                    # pint.Quantity(20.0, "degC") works
                    # (see https://github.com/hgrecco/pint/issues/386)
                    parsed = TypedQuantity.parse_expression(source_value)
                    if parsed is not None:
                        source_value, units = parsed
                value = ureg.Quantity(source_value, units=units)  # type: ignore
                # value = cls(source_value, units=units)  # type: ignore
        except pint.UndefinedUnitError as ex:
            raise ValueError(f'Cannot convert "{source_value}" to quantity') from ex
        if not isinstance(value, pint.Quantity):
            raise TypeError(f'pint.Quantity required ({value}, type = {type(value)})')
        if cls.__dimensionality__ is not None:
            dim = cls.__dimensionality__
            if not value.check(dim):
                raise ValueError(
                    f"The dimensionality of '{source_value} {units}' is "
                    f"not compatible with '{dim}'"
                )
        return value

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Type[Any], handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        # assert source_type is Quantity
        # print(source_type, type(source_type))
        # assert issubclass(source_type, Quantity)
        return core_schema.no_info_after_validator_function(
            cls._validate,
            core_schema.any_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(
                cls._serialize,
                info_arg=False,
                return_schema=core_schema.str_schema(),
            ),
        )

    @staticmethod
    def _serialize(value: pint.Quantity) -> str:
        return str(value)


VoltageQ: TypeAlias = TypedQuantity['[electric_potential]']
TemperatureQ: TypeAlias = TypedQuantity['[temperature]']
TemperatureRateQ: TypeAlias = TypedQuantity['[temperature]/[time]']
DimensionlessQ: TypeAlias = TypedQuantity['[]']
FrequencyQ: TypeAlias = TypedQuantity['1/[time]']
TimeQ: TypeAlias = TypedQuantity['[time]']
FractionQ: TypeAlias = TypedQuantity['[]']

# %%
