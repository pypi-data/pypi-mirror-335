import re
import urllib.parse
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Dict, List, Literal, Optional, Union
from maleo_core.utils.constants import SORT_COLUMN_PATTERN, DATE_FILTER_PATTERN

AllowedMethods = Literal["OPTIONS", "GET", "POST", "PATCH", "PUT", "DELETE", "*"]
AllowedRoles = Union[List[int], Literal["*"]]
RoutesPermissions = Dict[str, Dict[AllowedMethods, AllowedRoles]]

class Expand(BaseModel):
    expand:list[str] = Field([], description="Expanded field(s)")

class StatusUpdateAction(str, Enum):
    ACTIVATE = "activate"
    DEACTIVATE = "deactivate"
    RESTORE = "restore"
    DELETE = "delete"

class StatusUpdate(BaseModel):
    action:StatusUpdateAction = Field(..., description="Status update's action to be executed")

class Check(BaseModel):
    is_deleted:Optional[bool] = Field(None, description="Filter results based on deletion status.")
    is_active:Optional[bool] = Field(None, description="Filter results based on active status.")

class GetQuery(Check):
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
            #* Replace space followed by 2 digits, colon, 2 digits with + and those digits
            fixed_values = []
            for value in decoded_values:
                #* Look for the pattern: space followed by 2 digits, colon, 2 digits
                fixed_value = re.sub(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+) (\d{2}:\d{2})', r'\1+\2', value)
                fixed_values.append(fixed_value)
            final_values = [value for value in fixed_values if DATE_FILTER_PATTERN.match(value)]
            return final_values

class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"

class SortColumn(BaseModel):
    name:str = Field(..., description="Column name.")
    order:SortOrder = Field(..., description="Sort order.")

class DateFilter(BaseModel):
    name:str = Field(..., description="Column name.")
    from_date:Optional[datetime] = Field(None, description="From date.")
    to_date:Optional[datetime] = Field(None, description="To date.")

class Get(GetQuery):
    sort_columns:list[SortColumn] = Field([SortColumn(name="id", order=SortOrder.ASC)], description="List of columns to be sorted")
    date_filters:list[DateFilter] = Field([], description="Date filters to be applied")

    @model_validator(mode="after")
    def set_sort_columns(self):
        #* Process sort parameters
        sort_columns = []
        for item in self.sort:
            parts = item.split('.')
            if len(parts) == 2 and parts[1].lower() in ["asc", "desc"]:
                try:
                    sort_columns.append(SortColumn(name=parts[0],order=SortOrder(parts[1].lower())))
                except ValueError:
                    continue

        #* Only update if we have valid sort columns, otherwise keep the default
        if sort_columns:
            self.sort_columns = sort_columns
        return self

    @model_validator(mode="after")
    def set_date_filters(self):
        #* Process filter parameters
        date_filters = []
        for filter_item in self.filter:
            parts = filter_item.split('|')
            if len(parts) >= 2 and parts[0]:
                name = parts[0]
                from_date = None
                to_date = None

                #* Process each part to extract from and to dates
                for part in parts[1:]:
                    if part.startswith('from::'):
                        try:
                            from_date_str = part.replace('from::', '')
                            from_date = datetime.fromisoformat(from_date_str)
                        except ValueError:
                            continue
                    elif part.startswith('to::'):
                        try:
                            to_date_str = part.replace('to::', '')
                            to_date = datetime.fromisoformat(to_date_str)
                        except ValueError:
                            continue

                #* Only add filter if at least one date is specified
                if from_date or to_date:
                    date_filters.append(DateFilter(name=name, from_date=from_date, to_date=to_date))

        #* Update date_filters
        self.date_filters = date_filters
        return self