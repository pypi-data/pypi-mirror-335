from enum import Enum
from typing import List, Tuple, Union
from sqlmodel import SQLModel
from sqlalchemy import cast, and_
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import func


def extract_enum_values(values: List[Union[Enum, List[Enum]]]) -> List[str]:
    """
    Extracts string values from a list of Enums or nested lists of Enums.
    Ensures all values are converted to strings.
    """
    return [
        str((item[0] if isinstance(item, list) else item).value)
        if hasattr((item[0] if isinstance(item, list) else item), "value")
        else str(item[0] if isinstance(item, list) else item)
        for item in values
    ]


def apply_jsonb_contains_filter(
    stmt,
    count_stmt,
    filter_value: List[Union[Enum, List[Enum]]],
    model_class: SQLModel,
    field_name: str
) -> Tuple:
    """
    Applies a JSONB containment filter (`@>`) on a model field.
    """
    if not filter_value:
        return stmt, count_stmt

    values = extract_enum_values(filter_value)
    field = getattr(model_class, field_name)
    condition = cast(field, JSONB).contains(values)

    stmt = stmt.where(condition)
    if count_stmt is not None:
        count_stmt = count_stmt.where(condition)

    return stmt, count_stmt


def apply_comma_separated_filter(
    stmt,
    count_stmt,
    filter_value: List[Union[Enum, List[Enum]]],
    model_class: SQLModel,
    field_name: str
) -> Tuple:
    """
    Filters entries where ALL tags in filter_value are present
    in the comma-separated string field.
    """
    if not filter_value:
        return stmt, count_stmt

    tag_values = extract_enum_values(filter_value)
    field = getattr(model_class, field_name)
    padded_field = func.concat(',', field, ',')

    conditions = [padded_field.ilike(f'%,{tag},%') for tag in tag_values]
    combined_condition = and_(*conditions)

    stmt = stmt.where(combined_condition)
    if count_stmt is not None:
        count_stmt = count_stmt.where(combined_condition)

    return stmt, count_stmt
