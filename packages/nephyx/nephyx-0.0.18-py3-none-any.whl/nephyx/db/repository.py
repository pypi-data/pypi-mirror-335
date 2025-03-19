from collections.abc import Sequence
from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

#from src.domain.shared.filters import PageParams
from .model import ModelBase

ModelType = TypeVar("ModelType", bound=ModelBase)
#UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType], session: Session):
        self.model = model
        self.session = session

    def get(self, id: UUID | str) -> ModelType | None:
        return self.session.get(self.model, id)

    def get_by(self, **filters) -> ModelType | None:
        query = select(self.model)
        query = self.__filter(query, filters)
        return self.session.execute(query).scalars().first()

    def list_all(self, query_params: dict[str, Any] | None = None) -> tuple[Sequence[ModelType], int]:
        query = select(self.model)
        page_params = None
        if query_params:
            query = self.__filter(query, query_params.get("where", {}))
            query = self.__order_by(query, query_params.get("order_by", []))
            page_params = query_params.get("page_params", None)
        return self.paginate(query, page_params=page_params)


    def paginate(
            self, query: Select, *, scalars: bool = True, page_params: dict[str, str] | None = None
    ) -> tuple[Sequence[Any], int]:
        count_query = select(func.count()).select_from(query.subquery())
        total = self.session.scalar(count_query)

        if total is None:
            total = 0  # TODO throw exception

        result_query = query.offset(page_params["offset"]).limit(page_params["limit"]) \
            if page_params else query
        items = self.session.scalars(result_query).all() if scalars else self.session.execute(result_query).all()

        return items, total

    def __filter(self, query: Select, filters: dict[str, Any]):
        conditions = [
            getattr(self.model, key) == value
            for key, value in filters.items()
        ]
        return query.where(*conditions)

    def __order_by(self, query: Select, order: list[str]):
        return query.order_by(*order)

    # TODO proper create and update method
    def create(self, obj_in: ModelType) -> ModelType:
        self.session.add(obj_in)
        self.session.commit()
        self.session.refresh(obj_in)
        return obj_in

    def update(self, obj_in: ModelType) -> ModelType:
        self.session.commit()
        self.session.refresh(obj_in)
        return obj_in

    def update_all(self, objs_in: list[ModelType]):
        self.session.commit()
