from typing import Generic, TypeVar
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        coerce_numbers_to_str=False,
        alias_generator=to_camel,
        populate_by_name=True,
    )


Data = TypeVar("Data", bound=(BaseSchema))


# TODO check if this is really required
class DataResponse(BaseSchema, Generic[Data]):
    success: bool = True
    data: Data | list[Data]


class SingleDataResponse(BaseSchema, Generic[Data]):
    success: bool = True
    data: Data


class ListDataResponse(BaseSchema, Generic[Data]):
    success: bool = True
    data: list[Data]


class PaginationMetadata(BaseSchema):
    page: int
    limit: int | None
    total: int
    pages: int


class PaginatedDataResponse(BaseSchema, Generic[Data]):
    success: bool = True
    data: list[Data]
    metadata: PaginationMetadata
