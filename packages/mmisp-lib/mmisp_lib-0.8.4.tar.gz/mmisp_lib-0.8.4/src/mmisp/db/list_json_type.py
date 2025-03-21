import json
from typing import Any, Self

from sqlalchemy.engine import Dialect
from sqlalchemy.types import Text, TypeDecorator


class DBListJson(TypeDecorator):
    impl = Text

    def load_dialect_impl(self: Self, dialect: Dialect) -> Any:
        return dialect.type_descriptor(Text)

    def process_bind_param(self: Self, value: Any, dialect: Dialect) -> str | None:
        """Handle value before getting into the DB"""
        if value is None:
            return None
        if not isinstance(value, list):
            raise ValueError("this type should only be used for lists")
        return json.dumps(value)

    def process_result_value(self: Self, value: Any, dialect: Dialect) -> list | None:
        """Handle values from the database"""
        if value is None:
            return None

        res = json.loads(value)
        if not isinstance(res, list):
            raise ValueError("this type should only be used for lists")

        return res
