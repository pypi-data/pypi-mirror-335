from typing import Annotated, Any, TypeVar

from pydantic import BeforeValidator, Field

T = TypeVar("T")


def to_uppercase(value: str | T) -> str | T:
    if isinstance(value, str):
        return value.upper()
    return value


def to_lowercase(value: str | T) -> str | T:
    if isinstance(value, str):
        return value.lower()
    return value


def convert_to_list(value: list[T] | T) -> list[T]:
    if isinstance(value, list):
        return value
    return [value]


def empty_str_to_none(value: T) -> T | None:
    if value == "":
        return None
    return value


def get_list_depth(value: Any) -> int:
    count = 0
    while isinstance(value, list):
        value = value[0]
        count += 1
    return count


def translate_authorisation(value: T) -> T:
    if not isinstance(value, str):
        return value
    return value.replace("AUTHORISATION", "AUTHORIZATION")


type Uppercase[T] = Annotated[T, BeforeValidator(to_uppercase)]
type Lowercase[T] = Annotated[T, BeforeValidator(to_lowercase)]
type Translated[T] = Annotated[T, BeforeValidator(translate_authorisation)]
type CoercedOptional[T] = Annotated[T | None, BeforeValidator(empty_str_to_none)]
type CoercedList[T] = Annotated[list[T], Field(min_length=1), BeforeValidator(convert_to_list)]
