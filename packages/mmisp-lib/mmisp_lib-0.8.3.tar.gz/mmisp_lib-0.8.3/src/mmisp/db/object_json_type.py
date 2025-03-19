import json
from typing import Any, Self

from sqlalchemy.engine import Dialect
from sqlalchemy.types import Text, TypeDecorator


class DBObjectJson(TypeDecorator):
    impl = Text

    def load_dialect_impl(self: Self, dialect: Dialect) -> Any:
        return dialect.type_descriptor(Text)

    def process_bind_param(self: Self, value: Any, dialect: Dialect) -> str | None:
        """Handle value before getting into the DB"""
        if value is None:
            return None
        if not isinstance(value, dict):
            raise ValueError(f"this type should only be used for dicts, got {type(value)}")
        return json.dumps(value)

    def process_result_value(self: Self, value: Any, dialect: Dialect) -> dict | None:
        """Handle values from the database"""
        if value is None:
            return None

        res = json.loads(value)
        print("Result is", res)
        if res == []:
            res = {}
        if not isinstance(res, dict):
            raise ValueError(f"this type should only be used for dicts got: {type(res)}")

        return res
