from __future__ import annotations

from enum import Enum
from typing import List

from fa_common import CamelModel


class ProjectStatus(str, Enum):
    PENDING = "PENDING"
    READY = "READY"
    FAILED = "FAILED"
    ERROR = "ERROR"


class TableSort(CamelModel):
    column: str
    ascending: bool = True


class TableLoadParams(CamelModel):
    sheet: str | int | None = None
    separator: str | None = None
    encoding: str | None = None
    transpose: bool = False
    header_start_row: int = 0
    data_start_row: int = 1
    data_end_row: int | None = None


class TableInfo(CamelModel):
    columns: list[str]
    numeric_columns: list[str] = []
    total_rows: int | None = 0
    data: dict | str | None = None


class ColumnDefinition(CamelModel):
    name: str
    position: int


class ColumnDefinitionRange(ColumnDefinition):
    length: int

    def get_name(self, number: int) -> str:
        return f"{self.name}_{number}"

    def get_position(self, number: int) -> int:
        return self.position + number

    def get_all_names(self) -> List[str]:
        return [self.get_name(i) for i in range(self.length)]

    def get_all_postions(self) -> List[int]:
        return [self.get_position(i) for i in range(self.length)]


# class Project(DocumentDBTimeStampedModel):
#     name: str = Field(..., pattern=r"^$|^[0-9a-zA-Z_ ]+$")
#     user_id: str
#     status: ProjectStatus = ProjectStatus.PENDING
#     workspace_name: str
#     project_type: str
#     dataset_ref: Optional[str]
#
#     @classmethod
#     def get_db_collection(cls) -> str:
#         return f"{get_settings().COLLECTION_PREFIX}projects"


# class GenericProject(Project):
#     project_type: str
#     params: Optional[Dict[str, Any]] = None
