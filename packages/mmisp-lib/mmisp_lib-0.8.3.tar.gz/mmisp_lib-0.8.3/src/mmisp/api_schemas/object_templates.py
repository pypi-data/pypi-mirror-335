from pydantic import BaseModel, Field
from pydantic.types import UUID


class ObjectTemplatesRequirements(BaseModel):
    requiredOneOf: list[str] | None
    required: list[str] | None


class ObjectTemplate(BaseModel):
    class Config:
        allow_population_by_field_name = True

    id: int
    user_id: int
    org_id: int
    uuid: UUID
    name: str
    meta_category: str = Field(..., alias="meta-category")
    description: str
    version: str
    requirements: ObjectTemplatesRequirements
    fixed: bool
    active: bool


class ObjectTemplateElement(BaseModel):
    class Config:
        allow_population_by_field_name = True

    id: int
    object_template_id: int
    object_relation: str
    type: str  # AttributeType?
    ui_priority: int = Field(..., alias="ui-priority")
    categories: list
    sane_default: list
    values_list: list
    description: str
    disable_correlation: bool | None
    multiple: bool


class RespObjectTemplateView(BaseModel):
    ObjectTemplate: ObjectTemplate
    ObjectTemplateElement: list[ObjectTemplateElement]


class RespItemObjectTemplateIndex(BaseModel):
    ObjectTemplate: ObjectTemplate
