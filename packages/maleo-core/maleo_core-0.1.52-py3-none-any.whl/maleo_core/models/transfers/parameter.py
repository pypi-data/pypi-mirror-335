import urllib.parse
from pydantic import BaseModel, Field, field_validator
from typing import Dict, List, Literal, Optional, Union
from maleo_core.utils.constants import SORT_COLUMN_PATTERN, DATE_FILTER_PATTERN

class Expand(BaseModel):
    expand:list[str] = Field([], description="Expanded field(s)")

class StatusUpdate(BaseModel):
    action:Literal["activate", "deactivate", "restore", "delete"] = Field(..., description="Status update's action to be executed")

class Check(BaseModel):
    is_active:Optional[bool] = Field(None, description="Filter results based on active status.")
    is_deleted:Optional[bool] = Field(None, description="Filter results based on deletion status.")

class Get(Check):
    page:int = Field(1, ge=1, description="Page number, must be >= 1.")
    limit:int = Field(10, ge=1, le=1000, description="Page size, must be 1 <= limit <= 1000.")
    search:Optional[str] = Field(None, description="Search parameter string.")
    sort:list[str] = Field(["id.asc"], description="Sorting columns in 'column_name.asc' or 'column_name.desc' format.")
    filter:list[str] = Field([], description="Filters for date range, e.g. 'created_at|from::<ISO_DATETIME>|to::<ISO_DATETIME>'.")

    @field_validator("sort")
    def validate_sort_columns(cls, values):
        if not isinstance(values, list):
            return ["id.asc"]
        return [value for value in values if SORT_COLUMN_PATTERN.match(value)]

    @field_validator("filter")
    def validate_date_filters(cls, values):
        if isinstance(values, list):
            decoded_values = [urllib.parse.unquote(value) for value in values]
            return [value for value in decoded_values if DATE_FILTER_PATTERN.match(value)]

AllowedMethods = Literal["OPTIONS", "GET", "POST", "PATCH", "PUT", "DELETE", "*"]
AllowedRoles = Union[List[int], Literal["*"]]
RoutesPermissions = Dict[str, Dict[AllowedMethods, AllowedRoles]]